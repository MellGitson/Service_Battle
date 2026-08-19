# Carnet de la Flotte — Solo-Corsair

Mesures relevées sur `vm-prod` (maquette Docker-in-Docker locale, `infra/`).

## Taille des images

| Service | Avant (Étape 3, sans BDD) | Après (Étape 7, avec psycopg2) |
| :--- | :---: | :---: |
| `sb-api` | 184 MB | 195 MB |
| `sb-front` | 124 MB | 124 MB |
| `sb-annexe` | 124 MB | 124 MB |

L'augmentation de `sb-api` (+11 MB) vient de l'ajout de `psycopg2-binary` pour la connexion PostgreSQL réelle (Étape 7).

## Temps total de livraison pipeline

Mesuré sur les runs GitHub Actions récents (`push` sur `main` → build + transfert + déploiement + healthcheck) :

| Run | Durée |
| :--- | :---: |
| PR #4 (Dockerfiles + compose) | 41s |
| fix(ci) transfert images | 36s |
| PR #6 (healthchecks) | 36s |
| PR #7 (workload) | 34s |

**Moyenne : ~37s** du push à la validation healthcheck des 3 services.

## Nombre de coups encaissés (1 instance vs 3 instances)

Salve de 200 requêtes sur `POST /travail` (calcul + écriture/lecture PostgreSQL), envoyées en parallèle :

| Configuration | Durée pour 200 requêtes |
| :--- | :---: |
| 1 instance `api` | 40s |
| 3 instances `api` (`--scale api=3`) | 32s |

Le passage à l'échelle réduit le temps de traitement de ~20 % sur cette salve. Le gain est limité par la contention sur la base PostgreSQL unique (`INSERT` + `SELECT count(*)` séquentiels par requête), qui reste le goulot d'étranglement principal plutôt que le CPU des instances API.

Répartition de charge : Docker Compose résout `http://api:5000` en DNS round-robin entre les instances répliquées ; aucun proxy applicatif n'a été nécessaire pour ce test.

## Seuil de saturation (passage au carré pâle)

Non atteint lors des tests : avec 3 instances API et PostgreSQL en local (vm-prod), aucune requête n'a échoué ni timeout sur les salves testées (200 et 1000 requêtes). Le healthcheck `/sante` (30s de tolérance) n'a jamais basculé en échec pendant les tirs de charge.

## Temps de rétablissement après 1000 coups

Salve de 1000 requêtes envoyées avec un contrôle de concurrence (lots de 50) sur `POST /travail`, 3 instances API :

- Durée totale de la salve : **220s** (1000 requêtes)
- Temps de réponse de `/sante` immédiatement après la fin de la salve : **< 1s** (200 OK)
- Compteur final en base : 1401 coups cumulés (cohérent avec les tests précédents + cette salve)

Le système ne nécessite pas de "récupération" au sens propre : les requêtes sont traitées de manière synchrone, donc dès que la dernière requête de la salve est traitée, le service est immédiatement disponible pour la suivante.
