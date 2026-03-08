import discord
from discord.ext import commands

from bot import MultiSpoon

import bdd


def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    return discord.app_commands.check(predicate)


@discord.app_commands.guild_only()
class WhiteListCog(commands.GroupCog, group_name="white_list"):
    def __init__(self, bot: MultiSpoon):
        self.bot = bot
        self.bot.tree.error(coro=self.bot.on_app_command_error)

    # -----Commandes-----

    @discord.app_commands.command(name="activer",
                                  description="Permet d'activer la white list")
    @is_admin()
    @discord.app_commands.guild_only()
    async def activer(self, interaction: discord.Interaction):
        if not self.bot.guilds_data[interaction.guild_id].whiteListActive:
            self.bot.guilds_data[interaction.guild.id].whiteListActive = True
            await interaction.response.send_message(embed=discord.Embed(title="✅ La white list a été activé", color=discord.Color.green()))
            bdd.save_guilds(self.bot.guilds_data)
        else:
            await interaction.response.send_message(embed=discord.Embed(title=":warning: La white list est déjà activer", color=discord.Color.yellow()))

    @discord.app_commands.command(name="désactiver",
                                  description="Permet de désactiver la white list")
    @is_admin()
    @discord.app_commands.guild_only()
    async def desactiver(self, interaction: discord.Interaction):
        if self.bot.guilds_data[interaction.guild_id].whiteListActive:
            self.bot.guilds_data[interaction.guild.id].whiteListActive = False
            await interaction.response.send_message(
                embed=discord.Embed(title="✅ La white list a été désactivé", color=discord.Color.green()))
            bdd.save_guilds(self.bot.guilds_data)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(title=":warning: La white list est déjà désactivé", color=discord.Color.yellow()))

    @discord.app_commands.command(name="ajouter_salon",
                                  description="Permet d'ajouter un salon à la white list")
    @is_admin()
    @discord.app_commands.guild_only()
    async def ajouter_salon(self, interaction: discord.Interaction, salon: discord.TextChannel):
        if salon.id not in self.bot.guilds_data[interaction.guild_id].whiteList:
            self.bot.guilds_data[interaction.guild_id].whiteList.append(salon.id)
            await interaction.response.send_message(embed=discord.Embed(title="✅ Le salon a été ajouté à la white list", color=discord.Color.green()))
            bdd.save_guilds(self.bot.guilds_data)
        else:
            await interaction.response.send_message(embed=discord.Embed(title="✅ Le salon est déjà dans la white list", color=discord.Color.green()))

    @discord.app_commands.command(name="retirer_salon",
                                  description="Permet de retirer un salon de la white list")
    @is_admin()
    @discord.app_commands.guild_only()
    async def retirer_salon(self, interaction: discord.Interaction, salon: discord.TextChannel):
        if salon.id in self.bot.guilds_data[interaction.guild_id].whiteList:
            self.bot.guilds_data[interaction.guild_id].whiteList.remove(salon.id)
            await interaction.response.send_message(
                embed=discord.Embed(title="✅ Le salon a été retiré à la white list", color=discord.Color.green()))
            bdd.save_guilds(self.bot.guilds_data)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(title=":warning: Le salon n'est pas dans la white list", color=discord.Color.green()))


async def setup(bot: MultiSpoon):
    await bot.add_cog(WhiteListCog(bot))
