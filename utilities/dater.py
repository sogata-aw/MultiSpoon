import discord
import datetime as d

from utilities import settings as s


async def mois_en_jours(mois):
    return mois * 30


async def annee_en_jours(annee):
    return mois_en_jours(12 * annee)


async def create_channel_duree(ctx, nom, typesalon, settings, categorie=None, duree=None):
    if typesalon == "textuel":
        salon_temp = await ctx.guild.create_text_channel(name=nom, category=categorie)
        await add_channel(ctx, settings, salon_temp, nom, typesalon, categorie, duree)
    elif typesalon == "vocal":
        salon_temp = await ctx.guild.create_voice_channel(name=nom, category=categorie)
        await add_channel(ctx, settings, salon_temp, nom, typesalon, categorie, duree)
    else:
        await ctx.send(embed=discord.Embed(title=":warning: Le type n'est pas valide"))


async def add_channel(ctx, settings, salon, nom, typesalon, categorie=None, duree=None):
    settings["guild"][ctx.guild.name]["tempChannels"].append({
        "name": nom,
        "id": salon.id,
        "categorie": categorie.id if categorie is not None else None,
        "type": typesalon,
        "duree": duree.strftime("%Y-%m-%d %H:%M:%S:%f")
    })
    s.save(settings)
    await ctx.send(embed=discord.Embed(title=":white_check_mark: Le salon a été crée", colour=0x008001))


async def ajouter_temps(duree_split):
    duration = d.datetime.now()
    duree_split = str_to_int(duree_split)
    jours = semaines = heures = minutes = 0
    for i in range(len(duree_split)):
        if duree_split[i] in ['an', 'ans']:
            jours += annee_en_jours(duree_split[i - 1])
        elif duree_split[i] == 'mois':
            jours += annee_en_jours(duree_split[i - 1])
        elif duree_split[i] in ['j,jours,jour']:
            jours += duree_split[i - 1]
        elif duree_split[i] in ['h', 'heure', 'heures']:
            heures += duree_split[i - 1]
        elif duree_split[i] in ['m', 'min', 'minute', 'minutes']:
            minutes += duree_split[i - 1]
        elif i == (len(duree_split) - 1) and type(duree_split[i]) == int:
            minutes += duree_split[i]
    duration += d.timedelta(weeks=semaines, days=jours, hours=heures, minutes=minutes)
    return duration


async def delete_channel(channel, settings, guild):
    for salon in settings["guild"][guild.name]["tempChannels"]:
        if salon["id"] == channel.id:
            await channel.delete()
            s.save(settings)
            print("salon supprimé")


def str_to_int(liste):
    for i in range(len(liste)):
        try:
            liste[i] = int(liste[i])
        except ValueError:
            pass
    return liste
