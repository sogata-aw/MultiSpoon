import datetime as d
import discord
import json
import re as r

import dater as dat

pattern = r'^(\d+\s?(an|ans))?\s?(\d+\s?(mois))?\s?(\d+\s?(j|jour|jours))?\s?(\d+\s?(heures|heure|h))?\s?(\d+\s?(minutes|minute|min|m)?)?$'

async def set_timeout(ctx, sec, settings):
    if sec < 30:
        await ctx.send(":warning: Le temps est invalide ! Il doit être supérieur à 30 secondes")
    else:
        settings[ctx.guild.name]["timeout"] = sec
        await ctx.send("✅ Le temps avant expiration du captcha a été mis à jour")


async def set_role_before(ctx, role, settings):
    if role is None or not isinstance(role, discord.Role):
        await ctx.send(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings[ctx.guild.name]["roleBefore"] = role.id
        await ctx.send("✅ Le rôle d'arrivée a été mis à jour")


async def set_role_after(ctx, role, settings):
    if role is None or not isinstance(role, discord.Role):
        await ctx.send(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings[ctx.guild.name]["roleAfter"] = role.id
        await ctx.send("✅ Le rôle après vérification a été mis à jour")


async def set_verification_channel(ctx, channel, settings):
    if channel is None or not isinstance(channel, discord.TextChannel):
        await ctx.send(":warning: Le salon selectionné n'est pas valide")
    else:
        settings[ctx.guild.name]["verificationChannel"] = channel.id
        await ctx.send("✅ Le salon des vérifications a été mis à jour")


async def create_settings(guild, settings):
    settings[guild.name] = {"verificationChannel": 0,
                            "roleBefore": 0,
                            "roleAfter": 0,
                            "timeout": 300,
                            "nbEssais": 3,
                            "tempChannels" : [],
                            "tempRoles" : [],
                            "logchannel": 0
                            }
    save(settings)

async def create_channel(ctx, nom, type, settings, categorie = None, duree = None, date = None, heure = None):
    nombre = None
    if duree is None and date is None and heure is None:
        await ctx.send(embed=discord.Embed(title=":warning: vous devez au moins mettre la duree ou la date et l'heure"))
    elif duree is not None:
        duree_match = r.findall(pattern, duree)
        total_duration = duree_de_base = d.datetime.now()
        if duree_match == None:
            await ctx.send(embed=discord.Embed(title=":warning: la durée est invalide"))
        else:
            pass

    else:
        pass

def ajouter_temps(matches, temps):
    for i in range(len(temps[0])):
        pass


async def delete_settings(guild, settings):
    del settings[guild.name]
    save(settings)


def save(settings):
    with open("./settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def loading():
    with open("./settings.json", "r", encoding="utf-8") as file:
        return json.load(file)
