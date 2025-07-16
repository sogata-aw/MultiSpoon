import typing
import asyncio
import os
import datetime
import traceback

import discord
from discord.ext import commands

from dotenv import load_dotenv

import aiohttp

from view.aideView import AideSelectView
from view.supportView import SupportView
from view.voteView import VoteView

from utilities import captchas as c
from utilities import embeds as e

load_dotenv('.env')


def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    return discord.app_commands.check(predicate)


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.topgg_token = os.getenv("TOPGG_TOKEN")
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

    @staticmethod
    async def has_voted(user_id: int, bot_id: int, api_token: str) -> bool:
        url = f"https://top.gg/api/bots/{bot_id}/check?userId={user_id}"
        headers = {"Authorization": api_token}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                try:
                    data = await response.json()
                    return data.get("voted", 0) == 1
                except Exception as error:
                    print(f"[Top.gg] Erreur JSON : {error}")
                    return False

    @discord.app_commands.command(name="aide", description="affiche les informations sur les différentes commandes")
    async def aide(self, interaction, commande: str = None):
        if commande is None:
            embed = discord.Embed(title="Choisissez une catégorie", colour=discord.Colour.from_str("#68cd67"))
            embed.set_thumbnail(
                url="https://raw.githubusercontent.com/sogata-aw/MultiSpoon/refs/heads/master/img/logo.png")
            embed.add_field(name="",
                            value="Si vous ne trouvez pas ce que vous cherchez avec l'aide, n'hésitez pas à rejoindre le [serveur de support](https://discord.gg/aeCDNDByH8) !",
                            inline=False)
            await interaction.response.send_message(embed=embed, view=AideSelectView())

        elif commande == "Musique":
            await interaction.response.send_message(
                embed=await e.embed_aide(commande, self.bot.commands_data["Musique"]),
                view=AideSelectView())

        elif commande == "Mod\u00e9ration":
            await interaction.response.send_message(
                embed=await e.embed_aide(commande, self.bot.commands_data["Mod\u00e9ration"]),
                view=AideSelectView())

        elif commande == "Captcha":
            await interaction.response.send_message(
                embed=await e.embed_aide(commande, self.bot.commands_data["captcha"]),
                view=AideSelectView())

        elif commande == "Salon/R\u00F4le":
            await interaction.response.send_message(
                embed=await e.embed_aide(commande, self.bot.commands_data["Salon/R\u00F4le"]),
                view=AideSelectView())

    @discord.app_commands.command(name="settings",
                                  description="Affiche les différents paramètres mis en place (admin uniquement)")  # à améliorer
    @is_admin()
    @discord.app_commands.guild_only()
    async def settings(self, interaction):

        salon = interaction.guild.get_channel(self.bot.guilds_data[interaction.guild.name].verificationChannel)
        role_before = interaction.guild.get_role(self.bot.guilds_data[interaction.guild.name].roleBefore)
        role_after = interaction.guild.get_role(self.bot.guilds_data[interaction.guild.name].roleAfter)

        embed = discord.Embed(title="paramètre du bot :")
        embed.add_field(name="Salon de vérification : ", value=salon.mention)
        embed.add_field(name="Rôle d'arrivée : ", value=role_before.mention)
        embed.add_field(name="Rôle après vérification : ", value=role_after.mention)
        embed.add_field(name="Temps de la commande vérification : ",
                        value=self.bot.guilds_data[interaction.guild.name].timeout)
        embed.add_field(name="Nombre d'essais : ", value=self.bot.guilds_data[interaction.guild.name].nbEssais)

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="sync",
                                  description="Synchronise toutes les personnes qui ont le rôle après vérification")
    @is_admin()
    @discord.app_commands.guild_only()
    async def sync(self, interaction):
        for member in interaction.guild.members:
            if member.id not in self.bot.guilds_data[interaction.guild.name].alreadyVerified and member.get_role(
                    self.bot.guilds_data[interaction.guild.name].roleAfter) is not None:
                self.bot.guilds_data[interaction.guild.name].alreadyVerified.append(member.id)
        await interaction.response.send_message("Synchronisation terminé !")

    @discord.app_commands.command(name="verify", description="Permet de lancer la vérification")
    @discord.app_commands.guild_only()
    async def verify(self, interaction):
        reponse = None
        if not (interaction.guild.get_role(
                self.bot.guilds_data[interaction.guild.name].roleBefore) in interaction.user.roles):
            await interaction.response.send_message(":warning: Vous avez déjà effectué la vérification")

        elif interaction.user.name in self.bot.guilds_data[interaction.guild.name].inVerification:
            await interaction.response.send_message(
                ":warning: Vous êtes déjà en train de faire une vérification ! si vous avez raté le code donnée, attendez que le bot regénère un code")

        elif self.bot.guilds_data[interaction.guild.name].verificationChannel == 0 or \
                self.bot.guilds_data[interaction.guild.name].roleBefore == 0 or self.bot.guilds_data[
            interaction.guild.name].roleAfter == 0:

            await interaction.response.send_message(
                ":warning: La configuration n'est pas complète \n Veuillez la finaliser avant de procéder à une vérifcation"
            )
        else:
            self.bot.guilds_data[interaction.guild.name].inVerification.append(interaction.user.name)
            continuer = True
            tmps = self.bot.guilds_data[interaction.guild.name].timeout / 60
            first = True

            while continuer:
                code = c.generer_code()
                c.generer_image(code)
                attachement = discord.File("img/captcha.png", filename="img/captcha.png")
                name = interaction.user.global_name

                if first:
                    await interaction.response.send_message(
                        f"{name} veuillez rentrer le code du captcha **en minuscule**, vous avez {int(tmps)} minutes pour le faire",
                        file=attachement)
                    first = False
                else:
                    await interaction.channel.send(
                        f"{name} veuillez rentrer le code du captcha **en minuscule**, vous avez {int(tmps)} minutes pour le faire",
                        file=attachement)

                def verify_check(msg):
                    return msg.author == interaction.user and msg.channel == interaction.channel

                def msg_check(msg):
                    return (msg.author == interaction.user or interaction.client.user == msg.author and (
                                interaction.user.name.lower() in msg.content.lower()
                                or interaction.guild.name.lower() in msg.content.lower()
                                or "code" in msg.content.lower()
                                or interaction.user.mention.lower() in msg.content.lower()))

                try:
                    reponse = await self.bot.wait_for('message', check=verify_check,
                                                      timeout=self.bot.guilds_data[interaction.guild.name].timeout)

                    # Agir en fonction de la réponse de l'utilisateur
                    if reponse.content == code:
                        self.bot.guilds_data[interaction.guild.name].inVerification.remove(interaction.user.name)

                        await interaction.channel.send(f"Le code est bon ! Bienvenue sur {interaction.guild.name} !")
                        await interaction.user.add_roles(
                            interaction.guild.get_role(self.bot.guilds_data[interaction.guild.name].roleAfter))

                        await asyncio.sleep(0.5)

                        await interaction.user.remove_roles(
                            interaction.guild.get_role(self.bot.guilds_data[interaction.guild.name].roleBefore))
                        continuer = False

                        self.bot.guilds_data[interaction.guild.name].alreadyVerified.append(interaction.user.id)
                        await interaction.channel.purge(limit=50, check=msg_check)

                    else:
                        await interaction.channel.send("Code incorrect... Veuillez recommencer.")
                        await asyncio.sleep(0.5)
                        await interaction.channel.purge(limit=50, check=msg_check)

                except asyncio.TimeoutError:
                    self.bot.guilds_data[interaction.guild.name].inVerification.remove(interaction.user.name)

    @discord.app_commands.command(name="support", description="Vous propose le lien vers le serveur de support")
    async def support(self, interaction: discord.Interaction):
        embed = discord.Embed(colour=discord.Colour.from_str("#68cd67"), title="Support de MultiSpoon")
        embed.add_field(name="",
                        value="Vous avez rencontrés un problème avec l'une des commandes ? Vous pensez avoir trouvé un bug ? Ou vous voulez simplement faire une suggestion ?",
                        inline=False)
        embed.add_field(name="",
                        value="N'hésitez pas à nous en faire part sur le [serveur de support](https://discord.gg/aeCDNDByH8) où l'on pourra répondre à toutes vos question !",
                        inline=False)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/sogata-aw/MultiSpoon/refs/heads/master/img/logo.png")

        await interaction.response.send_message(embed=embed, view=SupportView(self.bot))

    @discord.app_commands.command(name="vote", description="Vous propose le lien pour voter pour le bot sur top.gg")
    async def vote(self, interaction: discord.Interaction):
        voted = await self.has_voted(interaction.user.id, self.bot.application_id, self.topgg_token)
        if voted:
            embed = discord.Embed(colour=discord.Colour.red(), title=":x:Vote indisponible")
            embed.add_field(name="", value="Vous avez déjà voté durant les 12 dernières heures, revenez plus tard",
                            inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(colour=discord.Colour.from_str("#68cd67"), title="Voter pour MultiSpoon")
            embed.add_field(name="",
                            value="Ça ne débloque rien de le faire mais c'est un petit soutien qui fait plaisir",
                            inline=False)
            await interaction.response.send_message(embed=embed, view=VoteView(self.bot))

    # -----autocomplete-----

    # Aide

    @aide.autocomplete("commande")
    async def autocomplete_commande(self, interaction, commande: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for cat in self.bot.commands_data:
            liste.append(discord.app_commands.Choice(name=cat, value=cat))

        return liste


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
