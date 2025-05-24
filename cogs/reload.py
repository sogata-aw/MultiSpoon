import discord
from discord.ext import commands

import os
import typing

@discord.app_commands.dm_only()
class ReloadCog(commands.GroupCog, group_name="reload"):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def is_me():
        async def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.id == 649268058652672051

        return discord.app_commands.check(predicate)

    # -----Commandes-----

    @discord.app_commands.command(name="extension",
                                  description="Permet de recharger une extension")
    @discord.app_commands.describe(extension="Le nom de celle que vous voulez recharger")
    @is_me()
    async def reload(self, interaction, extension: str):
        await self.bot.reload_extension(f"cogs.{extension}")
        await interaction.response.send_message(f"✅ Extension `{extension}` rechargée !")

    @discord.app_commands.command(name="all",
                                  description="Permet de recharger toutes les extensions")
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