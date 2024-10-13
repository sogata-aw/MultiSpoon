import discord
from discord.ext import commands
import json


async def set_timeout(interaction, sec):
    if sec < 30:
        await interaction.response.send_message(":warning: Le temps est invalide ! Il doit être supérieur à 30 secondes")
    else:
        settings["timeout"] = sec


async def set_role_before(interaction, id):
    role = interaction.guild.get_role(id)
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings["roleBefore"] = id
        await interaction.response.send_message("✅ Le rôle d'arrivée a été mis à jour")


async def set_role_after(interaction, id):
    role = interaction.guild.get_role(id)
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings["roleAfter"] = id
        await interaction.response.send_message("✅ Le rôle après vérification a été mis à jour")


async def set_verification_channel(interaction, id):
    salon = interaction.guild.get_channel(id)
    if salon is None or not isinstance(salon, discord.TextChannel):
        await interaction.response.send_message(":warning: Le salon selectionné n'est pas valide")
    else:
        settings["verificationChannel"] = id
        await interaction.response.send_message("✅ Le salon des vérifications a été mis à jour")


async def save():
    with open("settings.json", "w") as file:
        json.dump(settings, file)


def loading():
    with open("settings.json", "r") as file:
        return json.load(file)

settings = loading()