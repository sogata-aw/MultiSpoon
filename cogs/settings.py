import typing

import discord
from discord.ext import commands

from bot import MultiSpoon

import bdd

import newBDD
from utilities import settings as s


def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    return discord.app_commands.check(predicate)


@discord.app_commands.guild_only()
class SettingsCog(commands.GroupCog, group_name="set"):
    def __init__(self, bot: MultiSpoon):
        self.bot = bot
        self.bot.tree.error(coro=self.bot.on_app_command_error)

    # -----Commandes-----

    @discord.app_commands.command(name="role",
                                  description="Permet de configurer le rôle d'arrivée et celui après la vérification")
    @discord.app_commands.describe(option="Arrivée : rôle à l'arrivée, vérifié : rôle après vérification",
                                   role="Le rôle que vous voulez sélectionner")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_role(self, interaction: discord.Interaction, option: str, role: discord.Role):
        guild = await newBDD.getGuildById(interaction.guild.id)

        if option == "arrivée":
            guild.role_before = role.id

        elif option == "vérifié":
            guild.role_after = role.id

        await newBDD.updateGuild(guild)
        await interaction.response.send_message(
            embed=discord.Embed(title=f"✅ Le rôle {"d'arrivée" if option == "arrivée" else "après vérification"} a été mis à jour", color=discord.Color.green()))

    @discord.app_commands.command(name="channel",
                                  description="Permet de configurer le salon ou sera envoyé le message quand quelqu'un arrive sur le serveur")
    @discord.app_commands.describe(channel="Le salon dans lequel vous voulez envoyer le message de bienvenue")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild = await newBDD.getGuildById(interaction.guild.id)
        guild.verificationChannel = channel.id
        await newBDD.updateGuild(guild)

        await interaction.response.send_message(
            embed=discord.Embed(title="✅ Le salon des vérifications a été mis à jour", color=discord.Color.green()))

    @discord.app_commands.command(name="timeout",
                                  description="Permet de configurer le temps en seconde avant expiration du captcha")
    @discord.app_commands.describe(time="Le temps en secondes avant expiration de `/verify`")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_timeout(self, interaction: discord.Interaction, time: int):
        if time < 30:
            await interaction.response.send_message(
                embed=discord.Embed(title=":warning: Le temps est invalide ! Il doit être supérieur à 30 secondes",
                                    color=discord.Colour.yellow()))
            return

        guild = await newBDD.getGuildById(interaction.guild.id)
        guild.timeout = time
        await newBDD.updateGuild(guild)

        await interaction.response.send_message(
            embed=discord.Embed(title="✅ Le temps avant expiration du captcha a été mis à jour",
                                color=discord.Color.green()))

    @discord.app_commands.command(name="log", description="Permet de configurer le salon des logs du bot")
    @discord.app_commands.describe(
        channel="Le salon de logs où les messages du bot s'afficheront (laissez vite si vous souhaitez les retirer)")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_log(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            self.bot.guilds_data[interaction.guild.id].logChannel = 0
            return
        guild = await newBDD.getGuildById(interaction.guild.id)
        guild.log_channel = channel.id
        await newBDD.updateGuild(guild)

        await interaction.response.send_message(
            embed=discord.Embed(title="✅ Le salon des log a été mis à jour", color=discord.Color.green()))

    # Set_role
    @set_role.autocomplete("option")
    async def autocomplete_option(self, interaction: discord.Interaction, option: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for choice in ["arrivée", "vérifié"]:
            liste.append(discord.app_commands.Choice(name=choice, value=choice))
        return liste


async def setup(bot: MultiSpoon):
    await bot.add_cog(SettingsCog(bot))
