import os
from flask import Flask, request

from pouls import demarrerLePouls

app = Flask(__name__)

PAVILLON_FICHIER = os.environ.get("PAVILLON_FICHIER", "/data/pavillon.txt")


@app.get("/travail")
def travail():
    return {"status": "ok"}


@app.get("/sante")
def sante():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    demarrerLePouls()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
