import datetime as d
import re


def mois_en_jours(mois: int):
    return mois * 30

def annee_en_jours(annee: int):
    return mois_en_jours(12 * annee)

def get_expiration_time(minutes: int, heures: int, jours: int, semaines: int, mois: int, annees: int):
    return d.datetime.now() + d.timedelta(weeks=semaines, days=jours + mois_en_jours(mois) + annee_en_jours(annees), hours=heures, minutes=minutes)

def est_couleur_hexa(code: str):
    pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$"
    return bool(re.match(pattern, code))
