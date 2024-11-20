import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

from utilities import settings as s
from utilities import embeds as e

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
            print(f'{server.name}(id: {server.id})')

        for guild in bot.guilds:
            try:
                if self.settings[guild.name]["query"] is not None:
                    self.settings[guild.name]["query"] = []
            except KeyError:
                pass

        print("Début de la synchronisation")

        await bot.tree.sync()

        print("Synchronisation terminée\n")

        commandes = bot.tree.get_commands()

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
            channel = member.guild.get_channel(self.settings[member.guild.name]["verificationChannel"])
            print(member.guild.get_role(self.settings[member.guild.name]["roleBefore"]))
            await member.add_roles(member.guild.get_role(self.settings[member.guild.name]["roleBefore"]))
            try:
                await channel.send(
                    f"Bienvenue {member.mention} ! Veuillez utiliser la commande `/verify`")
            except discord.Forbidden:
                await channel.send(
                    "Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres")
        except AttributeError:
            await channel.send(":warning: Le bot ne trouve pas le rôle d'arrivée")

    async def setup_hook(self):
        print("Début de l'ajout des commandes")
        for extension in ['moderation', 'musique']:
            await self.load_extension(f'cogs.{extension}')
        print("Ajout des commandes terminée")

    def run(self, **kwargs):
        super().run(self.token)


if __name__ == "__main__":
    bot = MultiSpoon(discord.Intents.all(), tokenBeta)
    bot.run()
