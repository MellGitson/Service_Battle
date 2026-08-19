#!/bin/bash
# pannes.sh : déclenche l'une des 6 pannes de simulation sur la flotte déployée
# sur vm-prod (voir docs/RUNBOOK_FLOTTE.md pour le diagnostic et la réparation).
#
# Usage : ./pannes.sh <1-6>
#   1 : conteneur tué (docker kill)
#   2 : base de données coupée (docker stop db)
#   3 : volume du pavillon rendu inaccessible (chmod 000 /data)
#   4 : secret / mot de passe BDD supprimé
#   5 : tag d'image inexistant
#   6 : erreur réseau / TABLEAU_URL incorrecte
#
# Ce script s'exécute sur vm-prod (voir infra/README.md pour s'y connecter en SSH).

set -e

COMPOSE="docker compose -f /srv/flotte/docker-compose.prod.yml"

case "$1" in
  1)
    echo "Panne 1 : conteneur tué (docker kill api)"
    docker kill $(docker ps -qf "name=flotte-api")
    ;;
  2)
    echo "Panne 2 : base de données coupée"
    $COMPOSE stop db
    ;;
  3)
    echo "Panne 3 : volume du pavillon rendu inaccessible"
    docker exec -u root $(docker ps -qf "name=flotte-front") chmod 000 /data
    ;;
  4)
    echo "Panne 4 : secret / mot de passe BDD supprimé (variable vidée sur l'api)"
    $COMPOSE exec -T -u root api sh -c 'unset DB_PASSWORD'
    echo "Pour reproduire un vrai redémarrage sans le secret, relancer 'api' avec DB_PASSWORD='' dans l'environnement."
    ;;
  5)
    echo "Panne 5 : tag d'image inexistant (tentative de déploiement avec TAG=inexistant)"
    TAG=inexistant $COMPOSE up -d api
    ;;
  6)
    echo "Panne 6 : erreur réseau / TABLEAU_URL incorrecte"
    $COMPOSE exec -T front sh -c 'echo panne appliquée : voir RUNBOOK pour reproduire en changeant TABLEAU_URL'
    ;;
  *)
    echo "Usage: $0 <1-6>"
    exit 1
    ;;
esac
