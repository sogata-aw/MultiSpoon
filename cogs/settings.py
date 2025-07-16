import typing
import asyncio
import os
import datetime
import traceback

import discord
from discord.ext import commands

import bdd
from view.aideView import AideSelectView
from utilities import captchas as c, settings as s
from utilities import embeds as e

def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return discord.app_commands.check(predicate)

@discord.app_commands.guild_only()
class SettingsCog(commands.GroupCog, group_name="set"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.error(coro=self.on_app_command_error)

    # -----Commandes-----
    async def on_app_command_error(self, interaction: discord.Interaction,
                                   error: discord.app_commands.AppCommandError):
        error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        log_entry = (
            f"[{error_time}] ERREUR Slash Command (COG)\n"
            f"Auteur: {interaction.user} (ID: {interaction.user.id})\n"
            f"Guild: {interaction.guild} | Channel: {interaction.channel}\n"
            f"Erreur: {repr(error)}\n"
            f"Traceback:\n{tb}\n"
            f"{'-' * 60}\n"
        )
        with open("errors.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
        if interaction.response.is_done():
            await interaction.followup.send("❌ Une erreur est survenue (suivi).", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @discord.app_commands.command(name="role",
                             description="Permet de configurer le rôle d'arrivée et celui après la vérification")
    @discord.app_commands.describe(option="Arrivée : rôle à l'arrivée, vérifié : rôle après vérification",
                                   role="Le rôle que vous voulez sélectionner")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_role(self, interaction, option: str, role: discord.Role):
        if option == "arrivée":
            await s.set_role_before(interaction, role, self.bot.guilds_data)
        elif option == "vérifié":
            await s.set_role_after(interaction, role, self.bot.guilds_data)
        bdd.save_guilds(self.bot.guilds_data)

    @discord.app_commands.command(name="channel",
                             description="Permet de configurer le salon ou sera envoyé le message quand quelqu'un arrive sur le serveur")
    @discord.app_commands.describe(channel="Le salon dans lequel vous voulez envoyer le message de bienvenue")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_channel(self, interaction, channel: discord.TextChannel):
        await s.set_verification_channel(interaction, channel, self.bot.guilds_data)
        bdd.save_guilds(self.bot.guilds_data)

    @discord.app_commands.command(name="timeout",
                             description="Permet de configurer le temps en seconde avant expiration du captcha")
    @discord.app_commands.describe(time="Le temps en secondes avant expiration de `/verify`")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_timeout(self, interaction, time: int):
        await s.set_timeout(interaction, time, self.bot.guilds_data)
        bdd.save_guilds(self.bot.guilds_data)

    # Setrole
    @set_role.autocomplete("option")
    async def autocomplete_option(self, interaction, option: str) -> typing.List[discord.app_commands.Choice[str]]:
        liste = []
        for choice in ["arrivée", "vérifié"]:
            liste.append(discord.app_commands.Choice(name=choice, value=choice))
        return liste

async def setup(bot):
    await bot.add_cog(SettingsCog(bot))

