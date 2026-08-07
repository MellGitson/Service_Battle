# vm-prod : la machine cible

Maquette de serveur de production : un conteneur Docker-in-Docker avec un serveur SSH,
qui publie 4 ports vers l'hote :
- `2222` -> SSH
- `3000` -> front (application)
- `3001` -> Grafana
- `9090` -> Prometheus

## Premiere fois : generer la cle de deploiement

```bash
ssh-keygen -t ed25519 -f infra/deploy_key -N "" -C "deploy@vm-prod"
cp infra/deploy_key.pub infra/deploy_key.pub  # deja au bon endroit
```

`infra/deploy_key` (privee) ne doit jamais etre committee : elle est dans `.gitignore`.
`infra/deploy_key.pub` (publique) est celle copiee dans l'image au build.

## Construire et lancer vm-prod

```bash
docker build -t vm-prod -f infra/Dockerfile.vm infra/
docker run -d \
  --name vm-prod \
  --privileged \
  -p 2222:22 \
  -p 3000:3000 \
  -p 3001:3001 \
  -p 9090:9090 \
  vm-prod
```

## Verifier qu'elle repond

```bash
ssh -i infra/deploy_key -p 2222 root@localhost 'docker ps'
```

Doit afficher la liste des conteneurs qui tournent dessus (vide au depart), sans erreur
de connexion.

## Si vm-prod a ete arretee

```bash
docker start vm-prod
ssh -i infra/deploy_key -p 2222 root@localhost 'docker ps'
```

## Si vm-prod a disparu

Reconstruire depuis ce dossier avec les commandes "Construire et lancer" ci-dessus :
c'est le test reel de cette procedure.
