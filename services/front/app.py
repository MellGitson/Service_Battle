import os
import urllib.request
import urllib.error
from flask import Flask, render_template, request

from pouls import demarrerLePouls

app = Flask(__name__)

PAVILLON_FICHIER = os.environ.get("PAVILLON_FICHIER", "/data/pavillon.txt")
URL_API = os.environ.get("URL_API", "http://api:5000")


def _donnees_api():
    try:
        with urllib.request.urlopen(f"{URL_API}/travail", timeout=3) as reponse:
            return reponse.status == 200
    except (urllib.error.URLError, TimeoutError):
        return None


@app.get("/")
def index():
    pavillon = ""
    if os.path.exists(PAVILLON_FICHIER):
        with open(PAVILLON_FICHIER) as f:
            pavillon = f.read()
    api_disponible = _donnees_api()
    return render_template(
        "index.html",
        groupe=os.environ.get("GROUPE", ""),
        pavillon=pavillon,
        api_disponible=api_disponible,
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
    return {"status": "ok"}, 200


if __name__ == "__main__":
    demarrerLePouls()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
