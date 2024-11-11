import discord
from discord.ext import commands
import json


async def set_timeout(interaction, sec):
    if sec < 30:
        await interaction.response.send_message(":warning: Le temps est invalide ! Il doit être supérieur à 30 secondes")
    else:
        settings[interaction.guild.name]["timeout"] = sec
        await interaction.response.send_message("✅ Le temps avant expiration du captcha a été mis à jour")


async def set_role_before(interaction, role):
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings[interaction.guild.name]["roleBefore"] = role.id
        await interaction.response.send_message("✅ Le rôle d'arrivée a été mis à jour")


async def set_role_after(interaction, role):
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings[interaction.guild.name]["roleAfter"] = role.id
        await interaction.response.send_message("✅ Le rôle après vérification a été mis à jour")


async def set_verification_channel(interaction, channel):
    if channel is None or not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message(":warning: Le salon selectionné n'est pas valide")
    else:
        settings[interaction.guild.name]["verificationChannel"] = channel.id
        await interaction.response.send_message("✅ Le salon des vérifications a été mis à jour")

async def create_settings(guild):
    settings[guild.name] = {"verificationChannel": 0,
                            "roleBefore": 0,
                            "roleAfter": 0,
                            "timeout": 300,
                            "nbEssais": 3,
                            "logchannel": 0
                            }
    await save()


async def delete_settings(guild):
    del settings[guild.name]
    await save()

async def save():
    with open("settings.json", "w") as file:
        json.dump(settings, file)


def loading():
    with open("settings.json", "r") as file:
        return json.load(file)

settings = loading()