import discord
from discord.ext import commands

import os
from keep_alive import keep_alive

import captcha as c
import settings as s

tokenBeta = os.getenv('DTB')
token = os.getenv('DT')


class MultiSpoon(commands.Bot):
    def __init__(self, intents, token):
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.settings = s.loading()

    async def on_ready(self):
        print("Je suis prêt")

        for server in bot.guilds:
            print(f'{server.name}(id: {server.id})')
        print("Début de la synchronisation")

        for guild in bot.guilds:
            try:
                if self.settings[guild.name]["query"] is not None:
                    self.settings[guild.name]["query"] = []
            except KeyError:
                pass

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

        user = await bot.fetch_user(649268058652672051)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await self.embed("Un serveur a ajouté le bot", guild))

    async def on_guild_remove(self, guild: discord.Guild):
        await s.delete_settings(guild, self.settings)
        print(f"Le serveur {guild.name} a été supprimé de la configuration")

        user = await bot.fetch_user(649268058652672051)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await self.embed("Un serveur a supprimé le bot", guild))

    async def embed(self, title, guild):
        embed = discord.Embed(title=title, color=0x00ff00)
        embed.set_thumbnail(url=guild.icon)
        embed.set_author(name=guild.name)
        embed.add_field(name="Nom du serveur", value=guild.name, inline=False)
        embed.add_field(name="ID du serveur", value=guild.id, inline=False)
        embed.add_field(name="Propriétaire du serveur", value=f"{guild.owner},{guild.owner.mention}, {guild.owner_id}",
                        inline=False)
        embed.add_field(name="Nombre de membres", value=guild.member_count, inline=False)
        embed.set_footer(text=f"Date de création du serveur : {guild.created_at}")
        return embed

    async def on_member_join(self, member):
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

    def run(self):
        super().run(self.token)


if __name__ == "__main__":
    keep_alive()
    bot = MultiSpoon(discord.Intents.all(), token)
    bot.run()
