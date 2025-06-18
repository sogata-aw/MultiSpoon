import discord
from discord.ext import commands

import os
import typing
import datetime
import traceback

def is_me():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 649268058652672051
    return discord.app_commands.check(predicate)

@discord.app_commands.dm_only()
class ReloadCog(commands.GroupCog, group_name="reload"):
    def __init__(self, bot):
        self.bot = bot

        self.bot.tree.error(coro=self.on_app_command_error)

    # -----Commandes-----

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
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
    # -----Commandes-----

    @discord.app_commands.command(name="extension",
                                  description="Commande inutilisable")
    @discord.app_commands.describe(extension="Le nom de celle que vous voulez recharger")
    @is_me()
    async def reload(self, interaction, extension: str):
        await self.bot.reload_extension(f"cogs.{extension}")
        await interaction.response.send_message(f"✅ Extension `{extension}` rechargée !")

    @discord.app_commands.command(name="all",
                                  description="Commande inutilisable")
    @is_me()
    async def reload_all(self, interaction):
        await self.bot.setup_hook()
        await interaction.response.send_message(f"✅ Extensions rechargées !")

    # Reload

    @reload.autocomplete("extension")
    async def autocomplete_extension(self, interaction, extension: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py") and not cog.startswith("__"):
                liste.append(discord.app_commands.Choice(name=cog[:-3], value=cog[:-3]))
        return liste

async def setup(bot):
    await bot.add_cog(ReloadCog(bot))