import discord
import json


async def set_timeout(interaction, sec, guilds):
    if sec < 30:
        await interaction.response.send_message(":warning: Le temps est invalide ! Il doit être supérieur à 30 secondes")
    else:
        guilds[interaction.guild.name].timeout = sec
        await interaction.response.send_message("✅ Le temps avant expiration du captcha a été mis à jour")


async def set_role_before(interaction, role, guilds):
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(":warning: Le rôle sélectionné n'est pas valide")
    else:
        guilds[interaction.guild.name].roleBefore = role.id
        await interaction.response.send_message("✅ Le rôle d'arrivée a été mis à jour")


async def set_role_after(interaction, role, guilds):
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(":warning: Le rôle sélectionné n'est pas valide")
    else:
        guilds[interaction.guild.name].roleAfter = role.id
        await interaction.response.send_message("✅ Le rôle après vérification a été mis à jour")


async def set_verification_channel(interaction, channel, guilds):
    if channel is None or not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message(":warning: Le salon selectionné n'est pas valide")
    else:
        guilds[interaction.guild.name].verificationChannel = channel.id
        await interaction.response.send_message("✅ Le salon des vérifications a été mis à jour")