import os
import typing

import discord
from discord.ext import commands

from bot import MultiSpoon
import bdd

def is_me():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 649268058652672051

    return discord.app_commands.check(predicate)


@discord.app_commands.dm_only()
class ReloadCog(commands.GroupCog, group_name="reload"):
    def __init__(self, bot: MultiSpoon):
        self.bot = bot
        self.bot.tree.error(coro=self.bot.on_app_command_error)

    # -----Commandes-----

    @discord.app_commands.command(name="extension", description="Commande inutilisable")
    @discord.app_commands.describe(
        extension="Le nom de celle que vous voulez recharger"
    )
    @is_me()
    async def reload(self, interaction: discord.Interaction, extension: str):
        await self.bot.reload_extension(f"cogs.{extension}")
        await interaction.response.send_message(
            f"✅ Extension `{extension}` rechargée !"
        )

    @discord.app_commands.command(name="all", description="Commande inutilisable")
    @is_me()
    async def reload_all(self, interaction: discord.Interaction):
        await self.bot.setup_hook()
        await interaction.response.send_message("✅ Extensions rechargées !")

    @discord.app_commands.command(name="guilds", description="Commande inutilisable")
    @is_me()
    async def reload_all(self, interaction: discord.Interaction):
        count = 0
        for guild in self.bot.guilds:
            if not self.bot.guilds_data[guild.id]:
                await bdd.add_guild(self.bot.guilds_data, guild)
                count += 1
        await interaction.response.send_message(f"{count} serveurs étaient manquants!")


    # Reload

    @reload.autocomplete("extension")
    async def autocomplete_extension(
        self, interaction: discord.Interaction, extension: str
    ) -> typing.List[discord.app_commands.Choice[str]]:
        liste = []
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py") and not cog.startswith("__"):
                liste.append(discord.app_commands.Choice(name=cog[:-3], value=cog[:-3]))
        return liste


async def setup(bot):
    await bot.add_cog(ReloadCog(bot))
