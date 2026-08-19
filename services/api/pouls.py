import os
import threading
import time
import urllib.request
import json

TABLEAU_URL = os.environ.get("TABLEAU_URL", "")
GROUPE = os.environ.get("GROUPE", "")
COULEUR = os.environ.get("COULEUR", "")
SERVICE = os.environ.get("SERVICE", "")
VERSION = os.environ.get("VERSION", "dev")
URL_INTERNE = os.environ.get("URL_INTERNE", "")

INTERVALLE_SECONDES = 5


def _envoyer_pouls():
    if not TABLEAU_URL:
        return
    payload = json.dumps({
        "groupe": GROUPE,
        "couleur": COULEUR,
        "service": SERVICE,
        "version": VERSION,
        "url": URL_INTERNE,
    }).encode("utf-8")
    requete = urllib.request.Request(
        f"{TABLEAU_URL}/api/pouls",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(requete, timeout=3)
    except Exception:
        pass


def _boucle_pouls():
    while True:
        _envoyer_pouls()
        time.sleep(INTERVALLE_SECONDES)


def demarrerLePouls():
    thread = threading.Thread(target=_boucle_pouls, daemon=True)
    thread.start()
