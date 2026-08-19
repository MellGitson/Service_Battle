# La Bataille des Services — Solo-Corsair

> Projet solo DevOps : conteneurisation, CI/CD, observabilité et résilience d'une flotte de micro-services.
> Réalisation individuelle intégrale — un seul auteur cumule les 5 rôles (Images, Livraison, État, Mesure, Astreinte).

## Informations de l'équipage

- **Nom de l'équipage :** Solo-Corsair
- **Couleur hexadécimale :** `#f1c40f` (jaune)
- **Nombre de carrés jurés :** 3 (Front, API métier, Service annexe) + 1 Base de données (PostgreSQL)
- **Pavillon :** *Solo mais jamais seul face à la tempête.*
- **Repository Git :** https://github.com/MellGitson/Service_Battle.git
- **Auteur unique :** tous les commits sont signés par ce compte.

## Structure du dépôt

```text
.
├── .github/workflows/         # Pipeline CI/CD de déploiement automatique (deploy.yml)
├── services/
│   ├── front/                 # Code source + Dockerfile du Front
│   ├── api/                   # Code source + Dockerfile de l'API métier
│   └── annexe/                # Code source + Dockerfile du Service annexe
├── infra/                     # Machine cible vm-prod (maquette Docker-in-Docker + SSH)
├── grafana/provisioning/      # Datasource Prometheus + dashboard auto-provisionnés
├── docs/
│   ├── RUNBOOK_FLOTTE.md      # Diagnostic des pannes + procédure de reconstruction
│   └── CARNET_FLOTTE.md       # Relevés chiffrés et métriques
├── docker-compose.prod.yml    # Fichier de déploiement Compose (services + Prometheus + Grafana)
├── prometheus.yml             # Configuration de scraping Prometheus
├── grafana-dashboard.json     # Export du tableau de bord Grafana (4 panneaux)
├── pannes.sh                  # Script de simulation des 6 pannes
└── .env.example               # Exemple de variables d'environnement (sans secrets)
```


## Démarrage rapide

**Déploiement automatique :** tout push sur `main` déclenche `.github/workflows/deploy.yml`, qui build les 3 images, les déploie sur `vm-prod` et vérifie leur santé (échec si un service ne répond pas sous 30s).

**Déploiement manuel** (depuis `vm-prod` ou toute machine avec Docker Compose) :

```bash
cp .env.example .env   # puis remplir les variables
docker compose -f docker-compose.prod.yml up -d
```

**Accès aux services une fois déployés :**

| Service | Port | Usage |
| :--- | :---: | :--- |
| Front | 3000 | Interface web (pavillon, statut) |
| Grafana | 3001 | Dashboard "Flotte Solo-Corsair" (identifiants : `admin` / `GRAFANA_ADMIN_PASSWORD`) |
| Prometheus | 9090 | Requêtes PromQL, cibles scrapées |

**Simuler une panne :** `./pannes.sh <1-6>` (voir [docs/RUNBOOK_FLOTTE.md](docs/RUNBOOK_FLOTTE.md) pour le diagnostic de chacune).
