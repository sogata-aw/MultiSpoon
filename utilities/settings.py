import discord
import json


async def set_timeout(interaction, sec, settings):
    if sec < 30:
        await interaction.response.send_message(":warning: Le temps est invalide ! Il doit être supérieur à 30 secondes")
    else:
        settings["guilds"][interaction.guild.name]["timeout"] = sec
        await interaction.response.send_message("✅ Le temps avant expiration du captcha a été mis à jour")


async def set_role_before(interaction, role, settings):
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings["guilds"][interaction.guild.name]["roleBefore"] = role.id
        await interaction.response.send_message("✅ Le rôle d'arrivée a été mis à jour")


async def set_role_after(interaction, role, settings):
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings["guilds"][interaction.guild.name]["roleAfter"] = role.id
        await interaction.response.send_message("✅ Le rôle après vérification a été mis à jour")


async def set_verification_channel(interaction, channel, settings):
    if channel is None or not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message(":warning: Le salon selectionné n'est pas valide")
    else:
        settings["guilds"][interaction.guild.name]["verificationChannel"] = channel.id
        await interaction.response.send_message("✅ Le salon des vérifications a été mis à jour")


async def create_settings(guild, settings):
    settings["guilds"][guild.name] = {
        "id": guild.id,
        "verificationChannel": 0,
        "roleBefore": 0,
        "roleAfter": 0,
        "inVerification": [],
        "alreadyVerified": [],
        "timeout": 300,
        "tempChannels": [],
        "tempRoles": [],
        "tempVoiceChannels": [],
        "logchannel": 0
    }
    save(settings)


async def delete_settings(guild, settings):
    del settings["guilds"][guild.name]
    save(settings)


def save(settings):
    with open("./settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def loading():
    with open("./settings.json", "r", encoding="utf-8") as file:
        return json.load(file)
