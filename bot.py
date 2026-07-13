from email import message

import discord
from discord.ext import commands, tasks

import datetime as d
import traceback
import asyncio
import os
import json
import sys

from dotenv import load_dotenv
import logging
import colorlog
import bdd
import newBDD
from utilities.embeds import embed_log
from utilities.webhook import get_webhook

from view.verifyView import VerifyView

from utilities import embeds as e
from utilities import dater as dat


class MultiSpoon(commands.Bot):

    def __init__(self, intents: discord.Intents, token: str, update: bool):
        super().__init__(command_prefix="!", intents=intents)
        self.token: str = token
        self.commands_data: dict[str, dict[str, str]] = bdd.load_commands()
        self.createur: int = 649268058652672051
        self.update = update

        # Initialisation du logger

        self.logger = logging.getLogger("BOT_DISCORD")

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        with open("data/logger.json", 'r') as file:
            logger_settings = json.load(file)

        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(logger_settings["format"], log_colors=logger_settings["logColors"]))

        self.logger.addHandler(handler)
        self.logger.setLevel(logger_settings["level"])

    async def on_ready(self):

        # Changement du status

        await self.change_presence(status=discord.Status.online, activity=discord.Game(name='/aide'))

        # Affichage des serveurs

        for server in bot.guilds:
            self.logger.debug(f'{server.name}(id: {server.id})')

        # Synchronisation des commandes

        self.logger.info("-----Début de la synchronisation-----")
        await bot.tree.sync()
        self.logger.info("-----Synchronisation terminée-----")

        commandes = self.tree.get_commands()

        # Affichage des commandes du bot

        for command in commandes:
            self.logger.debug(
                f"Commande : {command.name}\nDescription : {command.description}\n------------------------")

        self.logger.debug(self.cogs)

        # Lancement des loops

        self.verif_temps.start()

        self.logger.info("MultiSpoon est prêt !")

        if self.update:
            user = await self.fetch_user(self.createur)
            dm_channel = await user.create_dm()
            await dm_channel.send(embed=discord.Embed(title="Le bot a été correctement mis à jour et a redémarré", color=discord.Colour.green()))

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):

        # Formattage des données

        error_time = d.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))

        # Notification au développeur

        user = await self.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(
            embed=discord.Embed(title="Une erreur est survenue dans le serveur : " + interaction.guild.name,
                                color=discord.Colour.red()))

        # Formattage du log

        log_entry = (
            f"[{error_time}] ERREUR Slash Command (COG)\n"
            f"Auteur: {interaction.user} (ID: {interaction.user.id})\n"
            f"Guild: {interaction.guild} | Channel: {interaction.channel}\n"
            f"Erreur: {repr(error)}\n"
            f"\n{tb}\n"
            f"{'-' * 60}\n"
        )

        # Ajout de l'erreur au fichier

        with open("errors.log", "a", encoding="utf-8") as f:
            f.write(log_entry)

        # Envoi de l'information à l'utilisateur

        if interaction.response.is_done():
            await interaction.followup.send(
                embed=discord.Embed(title="❌ Une erreur est survenue (suivi).", color=discord.Colour.red()),
                ephemeral=True)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(title="❌ Une erreur est survenue.", color=discord.Colour.red()), ephemeral=True)

    # -----Event-----

    async def on_guild_join(self, guild: discord.Guild):
        await newBDD.addGuild(guild)
        self.logger.info(f"Le serveur {guild.name} a été ajouté à la configuration")

        user = await self.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await e.embed_add("Un serveur a ajouté le bot", guild))

    async def on_guild_remove(self, guild: discord.Guild):
        await newBDD.deleteGuild(guild.id)
        self.logger.info(f"Le serveur {guild.name} a été supprimé de la configuration")

        user = await bot.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await e.embed_add("Un serveur a supprimé le bot", guild))

    async def on_member_join(self, member: discord.Member):
        guild = await newBDD.getGuildById(member.guild.id)
        user_verified = await newBDD.isUserVerified(member.id, guild.id)
        if user_verified:
            await member.add_roles(member.guild.get_role(guild.role_after))
        else:
            # Récupération du salon du serveur si configuré
            channel = member.guild.get_channel(guild.verification_channel)
            try:

                # Attribution du rôle au nouveau membre
                await member.add_roles(member.guild.get_role(guild.role_before))

                # Gestion des erreurs
                try:
                    embed = discord.Embed(title="",
                                          description=f"Bienvenue {member.mention} ! Veuillez utiliser la commande `/verify` ou cliquer sur le bouton ci-dessous",
                                          color=discord.Colour.green())
                    embed.set_author(name=member.name, icon_url=member.display_avatar)
                    await channel.send(member.mention, embed=embed, view=VerifyView(self))
                except discord.Forbidden:
                    await channel.send(embed=discord.Embed(
                        title="Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres",
                        color=discord.Colour.red()))
            except AttributeError:
                await channel.send(embed=discord.Embed(title=":warning: Le bot ne trouve pas le rôle d'arrivée",
                                                       color=discord.Colour.yellow()))

    async def on_member_remove(self, member: discord.Member):
        guild_data = await newBDD.getGuildById(member.guild.id)
        user_verified = await newBDD.isUserVerified(member.id, guild_data.id)
        if not user_verified and guild_data.verification_channel:
            guild = self.get_guild(member.guild.id)
            channel = guild.get_channel(guild_data.verificationChannel)

            def check_msg(msg: discord.Message):
                return (msg.author.name == member.name or
                        member.name.lower() in msg.content.lower()
                        or member.guild.name.lower() in msg.content.lower()
                        or "code" in msg.content.lower()
                        or member.mention in msg.content)

            await channel.purge(limit=50, check=check_msg)

    # Suppression automatique du salon dans les données du bot s'il était temporaire
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        guild = await newBDD.getGuildById(channel.guild.id)
        temp_channel = await newBDD.getTempChannel(channel.id, guild.id)
        white_channel = await newBDD.getWhiteChannel(channel.id, guild.id)

        if temp_channel:
            await newBDD.deleteTempChannel(temp_channel)

        if guild.white_list_active and white_channel:
            await newBDD.deleteChannelFromWhiteList(white_channel)

            log_channel = channel.guild.get_channel(guild.log_channel)

            if log_channel:
                await log_channel.send(
                    embed=discord.Embed(title=f"Le salon {channel.mention} a été retiré de la white list",
                                        color=discord.Color.green()))

    # Suppression automatique du rôle dans les données du bot s'il était temporaire
    async def on_guild_role_delete(self, role: discord.Role):
        temp_role = await newBDD.getTempRole(role.id, role.guild.id)
        if temp_role:
            await newBDD.deleteTempRole(temp_role)

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel is not None:
            trigger_channel = await newBDD.getTriggerChannel(after.channel.id, member.guild.id)
            if trigger_channel:
                    temp_channel = await member.guild.create_voice_channel(
                        name=f"Salon de {member.display_name}",
                        category=after.channel.category,
                        bitrate=after.channel.bitrate,
                        user_limit=after.channel.user_limit,
                        overwrites=after.channel.overwrites
                    )

                    # Déplacer l’utilisateur dans le nouveau salon
                    await member.move_to(temp_channel)

                    print(f"{member} a été déplacé dans {temp_channel.name}")
                    await newBDD.addTriggeredChannel(temp_channel.id, member.guild.id)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        guild_data = await newBDD.getGuildById(message.guild.id)

        if guild_data.spoon_pot != 0 and message.channel.id == guild_data.spoon_pot:
            await message.guild.ban(user=message.author, delete_message_seconds=60, reason="Tombé dans le pot de cuillère")
            log_channel = message.guild.get_channel(guild_data.log_channel)
            if log_channel:
                embed = embed_log(
                    f"{message.author.mention} est tombé dans le pot de cuillère et a été banni",
                    message.author,
                )
                await log_channel.send(embed=embed)

        if guild_data.white_list_active:
            white_channel = await newBDD.getWhiteChannel(message.channel.id, guild_data.id)
            if not white_channel:
                role = message.guild.get_role(guild_data.role_after)
                if role not in message.author.roles:
                    await message.delete()
                    channel = message.guild.get_channel(guild_data.verification_channel)
                    await message.channel.send(content=message.author.mention, embed=discord.Embed(
                        title=f":warning: Vous n'avez pas les droits pour écrire ici, veuillez passer la vérification dans {channel.mention}",
                        color=discord.Colour.yellow()))
        else:
            linked_channels = await newBDD.getLinks(message.channel.id, guild_data.id)
            for linked_channel in linked_channels:
                linked_guild = self.get_guild(linked_channel.linked_guild_id)
                channel = linked_guild.get_channel(linked_channel.linked_channel_id)
                webhook = await get_webhook(channel, "SpoonLink")
                await webhook.send(content=message.content, username=message.author.display_name, avatar_url=message.author.display_avatar.url)

    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        guild = await newBDD.getGuildById(channel.guild.id)
        if guild.on_create_channel:
            await newBDD.addToWhiteList(channel.id, guild.id)

            log_channel = channel.guild.get_channel(guild.log_channel)

            if log_channel:
                await log_channel.send(
                    embed=discord.Embed(title=f"Le salon {channel.mention} a été ajouté à la white list",
                                        color=discord.Color.green()))

    # Synchronisation avec les cogs
    async def setup_hook(self):
        self.logger.info("-----Début de l'ajout des commandes-----")
        for extension in os.listdir("./cogs"):
            if extension.endswith(".py") and not extension.startswith("__"):
                await self.load_extension(f'cogs.{extension[:-3]}')
                self.logger.info(f"cogs.{extension[:-3]} chargé avec succès !")

        self.logger.info("-----Ajout des commandes terminée-----")

    # -----Tasks-----

    @tasks.loop(seconds=7)
    async def verif_temps(self):
        self.logger.info("-----Début de la vérification-----")
        guilds = await newBDD.getAllGuilds()
        for guild in guilds:
            # Récupération du serveur
            serveur = self.get_guild(guild.id)

            # Récupération des rôles et salons temporaire
            temp_salons = await newBDD.getTempChannelsByGuildId(guild.id)
            temp_roles = await newBDD.getTempRolesByGuildId(guild.id)
            temp_vocs = await newBDD.getTriggeredChannelByGuildId(guild.id)
            await asyncio.sleep(0.5)

            for salon in temp_salons:
                # Récupération de la date à laquelle le salon doit être supprimé
                date_final = d.datetime.strptime(salon.duree, "%Y-%m-%d %H:%M:%S:%f")

                # Si la date est dépassé, alors on récupère le salon pour le supprimer
                if d.datetime.now() > date_final:
                    channel = serveur.get_channel(salon.id)
                    await channel.delete()
                await asyncio.sleep(0.5)

            for temp_role in temp_roles:
                # Récupération de la date à laquelle le rôle doit être supprimé
                date_final = d.datetime.strptime(temp_role.duree, "%Y-%m-%d %H:%M:%S:%f")

                # Si la date est dépassé, alors on récupère le rôle pour le supprimer
                if d.datetime.now() > date_final:
                    role = serveur.get_role(temp_role.id)
                    await role.delete()
                await asyncio.sleep(0.5)

            for temp_voc in temp_vocs:
                channel = serveur.get_channel(temp_voc.voice_channel_id)
                if channel and len(channel.members) == 0:
                    await channel.delete()
                    await newBDD.deleteTriggeredVoiceChannel(channel.id)

        self.logger.info("-----Fin de la vérification-----")
        await asyncio.sleep(0.5)

    @verif_temps.before_loop
    async def before_looping(self):
        await bot.wait_until_ready()

    def run(self, **kwargs):
        super().run(self.token)


if __name__ == "__main__":

    # Chargement de l'env

    load_dotenv('.env')

    mode = os.getenv('DEFAULT_TOKEN')

    token_base = os.getenv('DT')
    token_beta = os.getenv('DTB')

    updated = sys.argv and sys.argv[1] == "updated"

    if mode == "beta":
        bot = MultiSpoon(discord.Intents.all(), token_beta, updated)
    else:
        bot = MultiSpoon(discord.Intents.all(), token_base, updated)

    bot.run()
