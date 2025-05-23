import typing
import asyncio
import os

import discord
from discord.ext import commands

from view.aideView import AideSelectView
from utilities import captchas as c, settings as s
from utilities import embeds as e

@discord.app_commands.guild_only()
class SettingsCog(commands.GroupCog, group_name="set"):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def is_admin():
        async def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.guild_permissions.administrator
        return discord.app_commands.check(predicate)

    @discord.app_commands.command(name="role",
                             description="Permet de configurer le rôle d'arrivée et celui après la vérification")
    @discord.app_commands.describe(option="Arrivée : rôle à l'arrivée, vérifié : rôle après vérification",
                                   role="Le rôle que vous voulez sélectionner")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_role(self, interaction, option: str, role: discord.Role):
        if option == "arrivée":
            await s.set_role_before(interaction, role, self.bot.settings)
        elif option == "vérifié":
            await s.set_role_after(interaction, role, self.bot.settings)
        s.save(self.bot.settings)

    @discord.app_commands.command(name="channel",
                             description="Permet de configurer le salon ou sera envoyé le message quand quelqu'un arrive sur le serveur")
    @discord.app_commands.describe(channel="Le salon dans lequel vous voulez envoyer le message de bienvenue")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_channel(self, interaction, channel: discord.TextChannel):
        await s.set_verification_channel(interaction, channel, self.bot.settings)
        s.save(self.bot.settings)

    @discord.app_commands.command(name="timeout",
                             description="Permet de configurer le temps en seconde avant expiration du captcha")
    @discord.app_commands.describe(time="Le temps en secondes avant expiration de `/verify`")
    @is_admin()
    @discord.app_commands.guild_only()
    async def set_timeout(self, interaction, time: int):
        await s.set_timeout(interaction, time, self.bot.settings)
        s.save(self.bot.settings)

    # Setrole
    @set_role.autocomplete("option")
    async def autocomplete_option(self, interaction, option: str) -> typing.List[discord.app_commands.Choice[str]]:
        liste = []
        for choice in ["arrivée", "vérifié"]:
            liste.append(discord.app_commands.Choice(name=choice, value=choice))
        return liste

async def setup(bot):
    await bot.add_cog(SettingsCog(bot))

