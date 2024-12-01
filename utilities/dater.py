async def mois_en_semaines(mois):
    jours = mois * 30
    semaines = jours // 7
    jours = jours - semaines * 7
    return jours, semaines


async def annee_en_semaines(annee):
    return mois_en_semaines(12 * annee)
