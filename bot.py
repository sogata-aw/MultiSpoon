import discord
from discord.ext import commands, tasks

import datetime as d
import asyncio
import os

from dotenv import load_dotenv
import logging
import colorlog
import bdd

from view.verifyView import VerifyView

from utilities import embeds as e
from utilities import dater as dat

#Configuration des logs

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s[%(levelname)s] [%(name)s]: %(message)s',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))

bot_logger = logging.getLogger("BOT_DISCORD")
bot_logger.addHandler(handler)
bot_logger.setLevel(logging.DEBUG)



load_dotenv('.env')

#Token

mode = os.getenv('DEFAULT_TOKEN')

token_base = os.getenv('DT')
token_beta = os.getenv('DTB')


class MultiSpoon(commands.Bot):

    def __init__(self, intents, token):
        super().__init__(command_prefix="!", intents=intents)
        self.token: str = token
        self.guilds_data: dict[str, bdd.GuildData] = bdd.load_guilds()
        self.commands_data: dict[str, dict[str, str]] = bdd.load_commands()
        self.createur: int = 649268058652672051

    async def on_ready(self):

        await self.change_presence(status=discord.Status.online, activity=discord.Game(name='/aide'))

        for server in bot.guilds:
            self.guilds_data[server.name].inVerification = []

            bot_logger.debug(f'{server.name}(id: {server.id})')

        bot_logger.info("-----Début de la synchronisation-----")

        await bot.tree.sync()

        bot_logger.info("-----Synchronisation terminée-----")

        commandes = self.tree.get_commands()

        #Affichage des commandes du bot
        for command in commandes:
            bot_logger.debug(f"Commande : {command.name}\nDescription : {command.description}\n------------------------")

        bot_logger.debug(self.cogs)

        self.verif_temps.start()
        self.sauvegarde.start()

        bot_logger.debug(self.guilds_data)
        bot_logger.info("Je suis prêt !")

    #-----Event-----


    async def on_guild_join(self, guild: discord.Guild):
        await bdd.add_guild(self.guilds_data, guild)
        bot_logger.info(f"Le serveur {guild.name} a été ajouté à la configuration")

        user = await self.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await e.embed_add("Un serveur a ajouté le bot", guild))

    async def on_guild_remove(self, guild: discord.Guild):
        await bdd.remove_guild(self.guilds_data, guild)
        bot_logger.info(f"Le serveur {guild.name} a été supprimé de la configuration")

        user = await bot.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await e.embed_add("Un serveur a supprimé le bot", guild))

    async def on_member_join(self, member):
        if member.id in self.guilds_data[member.guild.name].alreadyVerified:
            await member.add_roles(member.guild.get_role(self.guilds_data[member.guild.name].roleAfter))
        else:
            channel = None
            try:
                #Récupération du salon du serveur si configuré
                channel = member.guild.get_channel(self.guilds_data[member.guild.name].verificationChannel)

                #Attribution du rôle au nouveau membre
                await member.add_roles(member.guild.get_role(self.guilds_data[member.guild.name].roleBefore))

                #Gestion des erreurs
                try:
                    await channel.send(
                        f"Bienvenue {member.mention} ! Veuillez utiliser la commande `/verify` ou cliquer sur le bouton ci-dessous", view=VerifyView(self))
                except discord.Forbidden:
                    await channel.send(
                        "Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres")
            except AttributeError:
                await channel.send(":warning: Le bot ne trouve pas le rôle d'arrivée")

    async def on_member_remove(self, member : discord.Member | discord.abc.User):
        if member.id not in self.guilds_data[member.guild.name].alreadyVerified and self.guilds_data[member.guild.name].verificationChannel:
            guild = self.get_guild(member.guild.id)
            channel = guild.get_channel(self.guilds_data[member.guild.name].verificationChannel)

            def check_msg(msg: discord.Message):
                return (msg.author.name == member.name or
                        member.name.lower() in msg.content.lower()
                        or member.guild.name.lower() in msg.content.lower()
                        or "code" in msg.content.lower()
                        or member.mention in msg.content)

            await channel.purge(limit=50, check=check_msg)

    #Suppression automatique du salon dans les données du bot s'il était temporaire
    async def on_guild_channel_delete(self, channel):
        for i in range(len(self.guilds_data[channel.guild.name].tempChannels)):
            if self.guilds_data[channel.guild.name].tempChannels[i].id == channel.id:
                self.guilds_data[channel.guild.name].tempChannels.pop(i)
        bdd.save_guilds(self.guilds_data)

    #Suppression automatique du rôle dans les données du bot s'il était temporaire
    async def on_guild_role_delete(self, role):
        for i in range(len(self.guilds_data[role.guild.name].tempRoles)):
            if self.guilds_data[role.guild.name].tempRoles[i].id == role.id:
                self.guilds_data[role.guild.name].tempRoles.pop(i)
        bdd.save_guilds(self.guilds_data)

    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None and after.channel.id in self.guilds_data[after.channel.guild.name].channelToCheck:
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
            self.guilds_data[after.channel.guild.name].tempVoiceChannels.append(temp_channel.id)


    #Synchronisation avec les cogs
    async def setup_hook(self):
        bot_logger.info("-----Début de l'ajout des commandes-----")
        for extension in os.listdir("./cogs"):
            if extension.endswith(".py") and not extension.startswith("__"):
                await self.load_extension(f'cogs.{extension[:-3]}')
                bot_logger.info(f"cogs.{extension[:-3]} chargé avec succès !")

        bot_logger.info("-----Ajout des commandes terminée-----")

    #-----Tasks-----

    @tasks.loop(seconds=10)
    async def verif_temps(self):
        bot_logger.info("-----Début de la vérification-----")

        for guild in self.guilds_data:
            #Récupération du serveur
            serveur = self.get_guild(self.guilds_data[guild].id)

            #Récupération des rôles et salons temporaire
            temp_salons = self.guilds_data[guild].tempChannels
            temp_roles = self.guilds_data[guild].tempRoles
            temp_vocs = self.guilds_data[guild].tempVoiceChannels
            await asyncio.sleep(1)

            for salon in temp_salons:
                #Récupération de la date à laquelle le salon doit être supprimé
                date_final = d.datetime.strptime(salon.duree, "%Y-%m-%d %H:%M:%S:%f")

                #Si la date est dépassé, alors on récupère le salon pour le supprimer
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
                if channel and len(channel.members) == 0 :
                    await channel.delete()
                    temp_vocs.remove(temp_voc)

        bot_logger.info("-----Fin de la vérification-----")
        await asyncio.sleep(1)

    @tasks.loop(minutes=15)
    async def sauvegarde(self):
        bdd.save_guilds(self.guilds_data)
        bot_logger.info("Sauvegarde effectué !")

    @verif_temps.before_loop
    @sauvegarde.before_loop
    async def before_looping(self):
        await bot.wait_until_ready()



    def run(self, **kwargs):
        super().run(self.token)


if __name__ == "__main__":
    if mode == "beta":
        bot = MultiSpoon(discord.Intents.all(), token_beta)
    else:
        bot = MultiSpoon(discord.Intents.all(), token_base)
    bot.run()
