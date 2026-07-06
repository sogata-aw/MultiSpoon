import datetime as d
import re


def mois_en_jours(mois: int):
    return mois * 30

def annee_en_jours(annee: int):
    return mois_en_jours(12 * annee)

async def ajouter_temps(duree_split: list[str]):
    duration = d.datetime.now()
    duree_split = str_to_int(duree_split)
    jours = heures = minutes = 0
    for i in range(len(duree_split)):
        if duree_split[i] in ['an', 'ans']:
            jours += mois_en_jours(int(duree_split[i - 1]))
        elif duree_split[i] == 'mois':
            jours += annee_en_jours(int(duree_split[i - 1]))
        elif duree_split[i] in ['j', 'jours', 'jour']:
            jours += duree_split[i - 1]
        elif duree_split[i] in ['h', 'heure', 'heures']:
            heures += duree_split[i - 1]
        elif duree_split[i] in ['m', 'min', 'minute', 'minutes']:
            minutes += duree_split[i - 1]
        elif i == (len(duree_split) - 1) and isinstance(duree_split[i], int):
            minutes += duree_split[i]
    duration += d.timedelta(days=jours, hours=heures, minutes=minutes)
    return duration

def est_couleur_hexa(code: str):
    pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$"
    return bool(re.match(pattern, code))

def str_to_int(liste: list[str]):
    for i in range(len(liste)):
        try:
            liste[i] = int(liste[i])
        except ValueError:
            pass
    return liste
