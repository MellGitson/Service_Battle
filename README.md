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
├── .github/workflows/        # Pipeline CI/CD de déploiement automatique
├── services/
│   ├── front/                # Code source + Dockerfile du Front
│   ├── api/                  # Code source + Dockerfile de l'API métier
│   └── annexe/                # Code source + Dockerfile du Service annexe
├── infra/                    # Machine cible vm-prod (maquette Docker-in-Docker + SSH)
├── k8s/                      # Manifestes Kubernetes (palier optionnel)
├── docs/
│   ├── RUNBOOK_FLOTTE.md     # Procédure de redéploiement et de résolution des pannes
│   └── CARNET_FLOTTE.md      # Relevés chiffrés et métriques
├── docker-compose.prod.yml   # Fichier de déploiement Compose
├── grafana-dashboard.json    # Export du tableau de bord Grafana (4 panneaux)
├── pannes.sh                 # Script de simulation des 6 pannes
└── .env.example              # Exemple de variables d'environnement (sans secrets)
```

## Avancement (paliers)

- [x] Palier 1 — Étape 1 : initialisation du dépôt et machine cible `vm-prod`
- [ ] Palier 1 — Étape 2 : intégration du pouls et premier service
- [ ] Palier 2 — Flotte au complet & CI/CD
- [ ] Palier 3 — Persistance et robustesse des sondes
- [ ] Palier 4 — Charge, scalabilité et relevés chiffrés
- [ ] Palier 5 — Simulation des 6 pannes et runbook
- [ ] Palier 6 — Observabilité (Prometheus & Grafana)
- [ ] Palier 7 — Déploiement cluster (optionnel)

Voir [DIRECTIVES_PROJET_SERVICES_BATTLE.md](DIRECTIVES_PROJET_SERVICES_BATTLE.md) pour le détail des directives suivies.
