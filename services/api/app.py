import os
import psycopg2
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge

from pouls import demarrerLePouls

app = Flask(__name__)
metrics = PrometheusMetrics(app)

VERSION = os.environ.get("VERSION", "dev")
metrics.info("service_version", "Version déployée du service", version=VERSION)
sante_bdd_gauge = Gauge("sante_bdd", "Connexion à la base de données (1 = ok, 0 = ko)")

PAVILLON_FICHIER = os.environ.get("PAVILLON_FICHIER", "/data/pavillon.txt")

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


def _connexion_bdd():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, connect_timeout=3
    )


def _init_table():
    with _connexion_bdd() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS coups (id SERIAL PRIMARY KEY, recu_a TIMESTAMPTZ DEFAULT now())"
            )
        conn.commit()


@app.get("/travail")
def travail():
    somme = sum(i * i for i in range(10000))
    with _connexion_bdd() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO coups DEFAULT VALUES RETURNING id")
            coup_id = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM coups")
            total = cur.fetchone()[0]
        conn.commit()
    return {"status": "ok", "coup_id": coup_id, "total_coups": total, "somme": somme}


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
        sante_bdd_gauge.set(0)
        return {"status": "ko", "raison": "connexion base de données indisponible"}, 503
    sante_bdd_gauge.set(1)
    return {"status": "ok"}, 200


if __name__ == "__main__":
    _init_table()
    demarrerLePouls()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
