import os
from flask import Flask, render_template, request

from pouls import demarrerLePouls

app = Flask(__name__)

PAVILLON_FICHIER = os.environ.get("PAVILLON_FICHIER", "/data/pavillon.txt")


@app.get("/")
def index():
    pavillon = ""
    if os.path.exists(PAVILLON_FICHIER):
        with open(PAVILLON_FICHIER) as f:
            pavillon = f.read()
    return render_template("index.html", groupe=os.environ.get("GROUPE", ""), pavillon=pavillon)


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
