import discord
from discord.ext import commands, tasks

import datetime as d
import traceback
import asyncio
import os
import json

from dotenv import load_dotenv
import logging
import colorlog
import bdd

from view.verifyView import VerifyView

from utilities import embeds as e
from utilities import dater as dat

class MultiSpoon(commands.Bot):

    def __init__(self, intents: discord.Intents, token: str):
        super().__init__(command_prefix="!", intents=intents)
        self.token: str = token
        self.guilds_data: dict[int, bdd.GuildData] = bdd.load_guilds()
        self.commands_data: dict[str, dict[str, str]] = bdd.load_commands()
        self.createur: int = 649268058652672051

        # Initialisation du logger

        self.logger = logging.getLogger("BOT_DISCORD")

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        with open("data/logger.json", 'r') as file:
            logger_settings = json.load(file)

        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(logger_settings["format"], log_colors=logger_settings["logColors"]))

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
            self.logger.debug(f"Commande : {command.name}\nDescription : {command.description}\n------------------------")

        self.logger.debug(self.cogs)

        # Lancement des loops

        self.verif_temps.start()
        self.sauvegarde.start()

        self.logger.debug(self.guilds_data)
        self.logger.info("MultiSpoon est prêt !")



    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):

        # Formattage des données

        error_time = d.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))

        # Notification au développeur

        user = await self.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=discord.Embed(title="Une erreur est survenue dans le serveur : " + interaction.guild.name, color=discord.Colour.red()))

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
            await interaction.followup.send(embed=discord.Embed(title="❌ Une erreur est survenue (suivi).", color=discord.Colour.red()), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(title="❌ Une erreur est survenue.", color=discord.Colour.red()), ephemeral=True)

    # -----Event-----

    async def on_guild_join(self, guild: discord.Guild):
        await bdd.add_guild(self.guilds_data, guild)
        self.logger.info(f"Le serveur {guild.name} a été ajouté à la configuration")

        user = await self.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await e.embed_add("Un serveur a ajouté le bot", guild))

    async def on_guild_remove(self, guild: discord.Guild):
        await bdd.remove_guild(self.guilds_data, guild)
        self.logger.info(f"Le serveur {guild.name} a été supprimé de la configuration")

        user = await bot.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await e.embed_add("Un serveur a supprimé le bot", guild))

    async def on_member_join(self, member: discord.Member):
        if member.id in self.guilds_data[member.guild.id].alreadyVerified:
            await member.add_roles(member.guild.get_role(self.guilds_data[member.guild.id].roleAfter))
        else:
            channel = None
            try:
                # Récupération du salon du serveur si configuré
                channel = member.guild.get_channel(self.guilds_data[member.guild.id].verificationChannel)

                # Attribution du rôle au nouveau membre
                await member.add_roles(member.guild.get_role(self.guilds_data[member.guild.id].roleBefore))

                # Gestion des erreurs
                try:
                    embed = discord.Embed(title="",
                                          description=f"Bienvenue {member.mention} ! Veuillez utiliser la commande `/verify` ou cliquer sur le bouton ci-dessous",
                                          color=discord.Colour.green())
                    embed.set_author(name=member.name, icon_url=member.display_avatar)
                    await channel.send(member.mention, embed=embed, view=VerifyView(self))
                except discord.Forbidden:
                    await channel.send(embed=discord.Embed(title="Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres", color=discord.Colour.red()))
            except AttributeError:
                await channel.send(embed=discord.Embed(title=":warning: Le bot ne trouve pas le rôle d'arrivée", color=discord.Colour.yellow()))

    async def on_member_remove(self, member: discord.abc.User):
        if member.id not in self.guilds_data[member.guild.id].alreadyVerified and self.guilds_data[member.guild.id].verificationChannel:
            guild = self.get_guild(member.guild.id)
            channel = guild.get_channel(self.guilds_data[member.guild.id].verificationChannel)

            def check_msg(msg: discord.Message):
                return (msg.author.name == member.name or
                        member.name.lower() in msg.content.lower()
                        or member.guild.name.lower() in msg.content.lower()
                        or "code" in msg.content.lower()
                        or member.mention in msg.content)

            await channel.purge(limit=50, check=check_msg)

    # Suppression automatique du salon dans les données du bot s'il était temporaire
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        for i in range(len(self.guilds_data[channel.guild.id].tempChannels)):
            if self.guilds_data[channel.guild.id].tempChannels[i].id == channel.id:
                self.guilds_data[channel.guild.id].tempChannels.pop(i)
        bdd.save_guilds(self.guilds_data)

    # Suppression automatique du rôle dans les données du bot s'il était temporaire
    async def on_guild_role_delete(self, role: discord.Role):
        for i in range(len(self.guilds_data[role.guild.id].tempRoles)):
            if self.guilds_data[role.guild.id].tempRoles[i].id == role.id:
                self.guilds_data[role.guild.id].tempRoles.pop(i)
        bdd.save_guilds(self.guilds_data)

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel is not None and after.channel.id in self.guilds_data[after.channel.guild.id].channelToCheck:
            temp_channel = await after.channel.guild.create_voice_channel(
                name=f"Salon de {member.display_name}",
                category=after.channel.category,
                bitrate=after.channel.bitrate,
                user_limit=after.channel.user_limit,
                overwrites=after.channel.overwrites
            )

            # Déplacer l’utilisateur dans le nouveau salon
            await member.move_to(temp_channel)

            print(f"{member} a été déplacé dans {temp_channel.name}")
            self.guilds_data[after.channel.guild.id].tempVoiceChannels.append(temp_channel.id)

    # Synchronisation avec les cogs
    async def setup_hook(self):
        self.logger.info("-----Début de l'ajout des commandes-----")
        for extension in os.listdir("./cogs"):
            if extension.endswith(".py") and not extension.startswith("__"):
                await self.load_extension(f'cogs.{extension[:-3]}')
                self.logger.info(f"cogs.{extension[:-3]} chargé avec succès !")

        self.logger.info("-----Ajout des commandes terminée-----")

    # -----Tasks-----

    @tasks.loop(seconds=10)
    async def verif_temps(self):
        self.logger.info("-----Début de la vérification-----")
        guilds_data = self.guilds_data.copy()
        for guild in guilds_data:
            # Récupération du serveur
            serveur = self.get_guild(guilds_data[guild].id)

            # Récupération des rôles et salons temporaire
            temp_salons = guilds_data[guild].tempChannels
            temp_roles = guilds_data[guild].tempRoles
            temp_vocs = guilds_data[guild].tempVoiceChannels
            await asyncio.sleep(1)

            for salon in temp_salons:
                # Récupération de la date à laquelle le salon doit être supprimé
                date_final = d.datetime.strptime(salon.duree, "%Y-%m-%d %H:%M:%S:%f")

                # Si la date est dépassé, alors on récupère le salon pour le supprimer
                if d.datetime.now() > date_final:
                    channel = serveur.get_channel(salon.id)
                    await dat.delete_channel(channel, self.guilds_data, serveur)
                await asyncio.sleep(1)

            for temp_role in temp_roles:
                # Récupération de la date à laquelle le rôle doit être supprimé
                date_final = d.datetime.strptime(temp_role.duree, "%Y-%m-%d %H:%M:%S:%f")

                # Si la date est dépassé, alors on récupère le rôle pour le supprimer
                if d.datetime.now() > date_final:
                    role = serveur.get_role(temp_role.id)
                    await dat.delete_role(role, self.guilds_data, serveur)
                await asyncio.sleep(1)

            for temp_voc in temp_vocs:
                channel = serveur.get_channel(temp_voc)
                if channel and len(channel.members) == 0:
                    await channel.delete()
                    temp_vocs.remove(temp_voc)

        self.logger.info("-----Fin de la vérification-----")
        await asyncio.sleep(1)

    @tasks.loop(minutes=5)
    async def sauvegarde(self):
        bdd.save_guilds(self.guilds_data)
        self.logger.info("Sauvegarde effectué !")

    @verif_temps.before_loop
    @sauvegarde.before_loop
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

    if mode == "beta":
        bot = MultiSpoon(discord.Intents.all(), token_beta)
    else:
        bot = MultiSpoon(discord.Intents.all(), token_base)

    bot.run()
