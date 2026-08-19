# Runbook de la Flotte — Solo-Corsair

Procédures de diagnostic, réparation et reconstruction de la flotte déployée sur `vm-prod`.
Toutes les pannes ci-dessous ont été déclenchées et chronométrées en conditions réelles via `pannes.sh`.

## Les 3 commandes réflexes en cas d'extinction d'un carré

Dès qu'un carré s'éteint ou pâlit sur le tableau, exécuter dans l'ordre, sur `vm-prod` :

```bash
docker ps -a                                    # état de tous les conteneurs (Up / Exited / Restarting)
docker logs <nom-du-conteneur> --tail 50         # dernière erreur visible
curl -s http://localhost:5000/sante              # (depuis l'intérieur du réseau docker, ou via docker compose exec)
```

Ces trois commandes suffisent à identifier 90 % des causes avant d'aller plus loin.

---

## Les 6 pannes : diagnostic et réparation

### Panne 1 — Conteneur tué (`docker kill`)

- **Symptôme visuel :** le front affiche "Données indisponibles" ; `docker ps` ne liste plus `flotte-api-1` (il apparaît `Exited (137)` dans `docker ps -a`).
- **Cause sous-jacente :** `docker kill` envoie un `SIGKILL` direct. **Constat important observé en test réel : la policy `restart: unless-stopped` ne redémarre pas automatiquement le conteneur** dans cet environnement Docker-in-Docker (vm-prod), contrairement au comportement attendu sur un hôte Docker classique. À surveiller en priorité si un carré reste éteint sans raison apparente.
- **Manœuvre de réparation :**
  ```bash
  cd /srv/flotte
  REGISTRY=<registry> TAG=<tag> [...variables d'env...] docker compose -f docker-compose.prod.yml up -d api
  ```
- **Temps de résolution observé :** ~4s (hors diagnostic).

### Panne 2 — Base de données coupée (`docker stop db`)

- **Symptôme visuel :** `GET /sante` sur l'API retourne `503 {"status":"ko","raison":"connexion base de données indisponible"}`. Le front reste up et affiche "Données indisponibles" (dégradation gracieuse, carré front toujours PLEIN).
- **Cause sous-jacente :** `_connexion_bdd()` de l'API échoue, l'exception est catchée et transformée en 503 explicite.
- **Manœuvre de réparation :**
  ```bash
  docker compose -f /srv/flotte/docker-compose.prod.yml start db
  ```
- **Temps de résolution observé :** ~4s.

### Panne 3 — Pavillon inaccessible / volume altéré (`chmod 000 /data`)

- **Symptôme visuel :** `POST /pavillon` retourne `500 Internal Server Error`. La page d'accueil (`GET /`) reste accessible (200) mais affiche un pavillon vide (le fichier existant devient illisible avec les permissions à 000, `os.path.exists()` échoue silencieusement côté front).
- **Cause sous-jacente :** permissions du volume nommé `/data` retirées pour tous les utilisateurs, y compris `appuser` (uid 1000) qui exécute le conteneur.
- **Manœuvre de réparation :**
  ```bash
  docker exec -u root <conteneur> chmod 755 /data
  ```
- **Temps de résolution observé :** immédiat (< 1s). Le contenu précédent du pavillon est préservé sur le volume et redevient lisible instantanément après le `chmod`.

### Panne 4 — Secret / mot de passe BDD supprimé

- **Symptôme visuel :** le conteneur `api` boucle en `Restarting (1)` en continu (`docker ps -a` montre `Restarting` toutes les quelques secondes). Le front dégrade gracieusement ("Données indisponibles", `/sante` front reste 200).
- **Cause sous-jacente :** `_init_table()` s'exécute au démarrage de l'API avant `app.run()`, sans être protégée par un try/except. Si `DB_PASSWORD` est vide, PostgreSQL rejette la connexion (`fe_sendauth: no password supplied`) et le process Python crashe immédiatement — c'est un choix assumé : mieux vaut un crash bruyant et visible qu'un service qui démarre dans un état incohérent.
- **Manœuvre de réparation :** restaurer la vraie valeur de `DB_PASSWORD` dans l'environnement de déploiement, puis :
  ```bash
  REGISTRY=<registry> TAG=<tag> DB_PASSWORD=<vrai mot de passe> [...] docker compose -f docker-compose.prod.yml up -d --force-recreate db api
  ```
- **Temps de résolution observé :** ~6s.

### Panne 5 — Tag d'image inexistant

- **Symptôme visuel :** `docker compose up -d` échoue immédiatement avec `pull access denied` / `repository does not exist`. **Le conteneur en cours d'exécution n'est pas affecté** — le service reste up avec l'ancienne image.
- **Cause sous-jacente :** le tag demandé n'existe ni en local ni dans le registry configuré.
- **Manœuvre de réparation :** aucune, sauf relancer le déploiement avec le bon tag. C'est le comportement recherché : un déploiement raté ne doit jamais casser un service sain — c'est aussi ce que le healthcheck du pipeline CI/CD (30s) est censé détecter avant validation.
- **Temps de résolution observé :** N/A (aucun impact service à réparer).

### Panne 6 — Erreur réseau / `TABLEAU_URL` incorrecte

- **Symptôme visuel :** aucun impact sur le service lui-même (`/sante` reste 200). Seul effet observable : le carré du service disparaît du tableau externe car `demarrerLePouls()` ne parvient plus à envoyer le pouls périodique.
- **Cause sous-jacente :** `pouls.py` catche silencieusement toute exception réseau (`except Exception: pass`) pour ne jamais faire planter le service à cause d'un tableau externe indisponible — comportement voulu.
- **Manœuvre de réparation :**
  ```bash
  REGISTRY=<registry> TAG=<tag> TABLEAU_URL=<url correcte> [...] docker compose -f docker-compose.prod.yml up -d --force-recreate front
  ```
- **Temps de résolution observé :** ~25s (recréation complète du conteneur).

---

## Reconstruction complète sur une machine vierge

1. **Préparer la machine cible** (voir `infra/README.md`) :
   ```bash
   ssh-keygen -t ed25519 -f infra/deploy_key -N "" -C "deploy@vm-prod"
   docker build -t vm-prod -f infra/Dockerfile.vm infra/
   docker run -d --name vm-prod --privileged \
     -p 2222:22 -p 3000:3000 -p 3001:3001 -p 9090:9090 vm-prod
   ```
2. **Vérifier la connectivité SSH :**
   ```bash
   ssh -i infra/deploy_key -p 2222 root@localhost 'docker ps'
   ```
3. **Configurer le runner GitHub Actions self-hosted** sur la machine qui peut atteindre `vm-prod` (voir `.github/workflows/deploy.yml`, `runs-on: self-hosted`).
4. **Configurer les secrets et variables GitHub** du dépôt :
   - Secrets : `SSH_PRIVATE_KEY` (contenu de `infra/deploy_key`), `VM_HOST`, `VM_PORT`, `DB_PASSWORD`
   - Variables : `GROUPE`, `COULEUR`, `TABLEAU_URL`, `DB_NAME`, `DB_USER`, `PAVILLON_FICHIER`
5. **Déclencher un déploiement** en poussant sur `main` : le pipeline build, transfère et déploie automatiquement les 3 services + la base PostgreSQL, avec vérification healthcheck (échec si un service ne répond pas sous 30s).
6. **Vérifier la flotte** :
   ```bash
   curl http://<vm-prod>:3000/sante
   ```

## Simulation des pannes

```bash
./pannes.sh <1-6>
```

Voir le détail de chaque panne ci-dessus pour le diagnostic et la réparation associée.
