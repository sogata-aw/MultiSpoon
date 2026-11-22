import discord
from discord.ext import commands

import newBDD
from bot import MultiSpoon
from utilities import permissions


class OWSCog(commands.GroupCog, group_name="ows"):
    def __init__(self, bot: MultiSpoon):
        self.bot = bot
        self.bot.tree.error(coro=self.bot.on_app_command_error)

    @permissions.is_admin()
    @discord.app_commands.guild_only()
    @discord.app_commands.command(name="configurer", description="Configurer le salon pour le One Word Story")
    @discord.app_commands.rename(channel="salon")
    @discord.app_commands.describe(channel="Le salon pour le One Word Story")
    async def configure(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild = await newBDD.get_guild_by_id(interaction.guild_id)

        guild.ows_channel = channel.id
        await newBDD.update_guild(guild)

        await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le salon pour le One Word Story a été configuré", color=discord.Color.green()))

    @permissions.is_admin()
    @discord.app_commands.guild_only()
    @discord.app_commands.command(name="activer", description="Active le One Word Story")
    async def activate(self, interaction: discord.Interaction):
        guild = await newBDD.get_guild_by_id(interaction.guild_id)

        if guild.ows_activated:
            await interaction.response.send_message(embed=discord.Embed(title="Le One Word Story est déjà actif", color=discord.Color.yellow()))
            return

        guild.ows_activated = True
        await newBDD.update_guild(guild)

        await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le One Word Story a été activé", color=discord.Color.green()))

    @permissions.is_admin()
    @discord.app_commands.guild_only()
    @discord.app_commands.command(name="désactiver", description="Désactive le One Word Story")
    async def deactivate(self, interaction: discord.Interaction):
        guild = await newBDD.get_guild_by_id(interaction.guild_id)

        if not guild.ows_activated:
            await interaction.response.send_message(embed=discord.Embed(title="Le One Word Story n'est pas activé", color=discord.Color.yellow()))
            return

        guild.ows_activated = False
        await newBDD.update_guild(guild)

        await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le One Word Story a été désactivé", color=discord.Color.green()))


async def setup(bot):
    await bot.add_cog(OWSCog(bot))
