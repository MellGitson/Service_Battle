import os
import psycopg2
from flask import Flask, request

from pouls import demarrerLePouls

app = Flask(__name__)

PAVILLON_FICHIER = os.environ.get("PAVILLON_FICHIER", "/data/pavillon.txt")

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


def _connexion_bdd():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, connect_timeout=3
    )


@app.get("/travail")
def travail():
    return {"status": "ok"}


@app.post("/pavillon")
def hisser_pavillon():
    texte = request.get_data(as_text=True)
    os.makedirs(os.path.dirname(PAVILLON_FICHIER), exist_ok=True)
    with open(PAVILLON_FICHIER, "w") as f:
        f.write(texte)
    return {"status": "ok"}


@app.get("/sante")
def sante():
    try:
        conn = _connexion_bdd()
        conn.close()
    except Exception:
        return {"status": "ko", "raison": "connexion base de données indisponible"}, 503
    return {"status": "ok"}, 200


if __name__ == "__main__":
    demarrerLePouls()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
