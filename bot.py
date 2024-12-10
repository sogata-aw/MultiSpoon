import discord
from discord.ext import commands

import datetime as d
import asyncio
import os
from dotenv import load_dotenv

from utilities import settings as s
from utilities import embeds as e
from utilities import dater as dat

load_dotenv('.env')
tokenbase = os.getenv('DT')

tokenBeta = os.getenv('DTB')


class MultiSpoon(commands.Bot):
    def __init__(self, intents, token):
        super().__init__(command_prefix="!", intents=intents)
        self.token: str = token
        self.settings: dict = s.loading()
        self.createur: int = 649268058652672051

    async def on_ready(self):
        print("Je suis prêt")

        for server in bot.guilds:
            try:
                if self.settings[server.name]["query"] is not None:
                    self.settings[server.name]["query"] = []
            except KeyError:
                pass
            print(f'{server.name}(id: {server.id})')

        print("Début de la synchronisation")

        await bot.tree.sync()

        print("Synchronisation terminée\n")

        commandes = bot.tree.get_commands()

        taskv = asyncio.create_task(self.boucle_verif_temp())

        for command in commandes:
            print(f"Commande : {command.name}")
            print(f"Description : {command.description}")
            print("------------------------")

    async def on_guild_join(self, guild: discord.Guild):
        await s.create_settings(guild, self.settings)
        print(f"Le serveur {guild.name} a été ajouté à la configuration")

        user = await bot.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await e.embed_add("Un serveur a ajouté le bot", guild))

    async def on_guild_remove(self, guild: discord.Guild):
        await s.delete_settings(guild, self.settings)
        print(f"Le serveur {guild.name} a été supprimé de la configuration")

        user = await bot.fetch_user(self.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await e.embed_add("Un serveur a supprimé le bot", guild))

    async def on_member_join(self, member):
        channel = None
        try:
            channel = member.guild.get_channel(self.settings["guild"][member.guild.name]["verificationChannel"])
            await member.add_roles(member.guild.get_role(self.settings["guild"][member.guild.name]["roleBefore"]))
            try:
                await channel.send(
                    f"Bienvenue {member.mention} ! Veuillez utiliser la commande `/verify`")
            except discord.Forbidden:
                await channel.send(
                    "Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres")
        except AttributeError:
            await channel.send(":warning: Le bot ne trouve pas le rôle d'arrivée")

    async def on_guild_channel_delete(self, channel):
        for i in range(len(self.settings["guild"][channel.guild.name]["tempChannels"])):
            if self.settings["guild"][channel.guild.name]["tempChannels"][i]["id"] == channel.id:
                self.settings["guild"][channel.guild.name]["tempChannels"].pop(i)
        s.save(self.settings)

    async def setup_hook(self):
        print("Début de l'ajout des commandes")
        for extension in ['moderation', 'musique', 'salons']:
            await self.load_extension(f'cogs.{extension}')
        print("Ajout des commandes terminée")

    async def boucle_verif_temp(self):
        while True:
            guilds = self.settings["guild"]
            for guild in guilds:
                temp_salons = self.settings["guild"][guild]["tempChannels"]
                await asyncio.sleep(1)
                for salon in temp_salons:
                    date_final = d.datetime.strptime(salon["duree"], "%Y-%m-%d %H:%M:%S:%f")
                    if d.datetime.now() > date_final:
                        serveur = self.get_guild(self.settings["guild"][guild]["id"])
                        channel = serveur.get_channel(salon["id"])
                        await dat.delete_channel(channel, self.settings, serveur)
                    await asyncio.sleep(1)

    def run(self, **kwargs):
        super().run(self.token)


if __name__ == "__main__":
    bot = MultiSpoon(discord.Intents.all(), tokenBeta)
    bot.run()
