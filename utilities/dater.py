import datetime as d
import re

import discord

import bdd


async def mois_en_jours(mois: int):
    return mois * 30


async def annee_en_jours(annee: int):
    return mois_en_jours(12 * annee)


async def create_channel_duree(interaction: discord.Interaction, nom: str, typesalon: str, guilds: dict[int, bdd.GuildData], categorie: discord.CategoryChannel = None, duree: str = None):
    if typesalon == "textuel":
        salon_temp = await interaction.guild.create_text_channel(name=nom, category=categorie)
        bdd.add_temp_channel(guilds, interaction, salon_temp, nom, typesalon, categorie, duree)
        await interaction.response.send_message(
            embed=discord.Embed(title=":white_check_mark: Le salon a été crée", colour=0x008001))
    elif typesalon == "vocal":
        salon_temp = await interaction.guild.create_voice_channel(name=nom, category=categorie)
        bdd.add_temp_channel(guilds, interaction, salon_temp, nom, typesalon, categorie, duree)
        await interaction.response.send_message(
            embed=discord.Embed(title=":white_check_mark: Le salon a été crée", colour=0x008001))
    else:
        await interaction.response.send_message(embed=discord.Embed(title=":warning: Le type n'est pas valide"))


async def create_role_duree(interaction: discord.Interaction, nom: str, duree: str, couleur: str, separe: bool, mentionable: bool, guilds: dict[int, bdd.GuildData]):
    role = await interaction.guild.create_role(name=nom, colour=discord.Colour.from_str(couleur), hoist=separe,
                                               mentionable=mentionable)
    bdd.add_temp_role(guilds, interaction, nom, duree, role)
    await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le rôle a été crée", colour=0x008001))


async def ajouter_temps(duree_split: list[str]):
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
        elif i == (len(duree_split) - 1) and isinstance(duree_split[i], int):
            minutes += duree_split[i]
    duration += d.timedelta(weeks=semaines, days=jours, hours=heures, minutes=minutes)
    return duration


async def delete_channel(channel: discord.abc.GuildChannel, guilds: dict[int, bdd.GuildData], guild: discord.Guild):
    for salon in guilds[guild.id].tempChannels:
        if salon.id == channel.id:
            await channel.delete()
            print("salon supprimé")


async def delete_role(role: discord.Role, guilds: dict[int, bdd.GuildData], guild: discord.Guild):
    for temp_role in guilds[guild.id].tempRoles:
        if temp_role.id == role.id:
            await role.delete()
            print("role supprimé")


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
