#!/bin/sh
# entrypoint.vm.sh : demarre le Docker interne (dind) puis le serveur SSH,
# pour que la machine cible reponde a la fois a "docker ps" et a une connexion SSH.
set -e

dockerd-entrypoint.sh &
DOCKERD_PID=$!

until docker info >/dev/null 2>&1; do
  sleep 1
done

/usr/sbin/sshd -D &
SSHD_PID=$!

wait "$DOCKERD_PID" "$SSHD_PID"
