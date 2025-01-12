import discord
from discord.ext import commands

import asyncio

from utilities import play as p
from utilities import embeds as e
import pytubefix.exceptions

play_task = None


class MusiqueCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="play", description="Lance un audio via l'URL youtube")
    @discord.app_commands.describe(url="Lien de la vidéo youtube que vous voulez lancer")
    async def play(self, ctx, url: str):
        if ctx.guild.name not in self.bot.settings["authorized"]:
            await ctx.send(":warning: Ce serveur n'est pas autorisé à utiliser cette commande")
        else:
            global play_task
            vc = None
            state = ctx.author.voice
            if state is None:
                await ctx.send("Vous devez être dans un salon vocal pour utiliser cette commande")
            else:
                if ctx.guild.voice_client is None:
                    vc = await state.channel.connect()
                    try:
                        await p.add_audio(ctx, url, 0, self.bot.settings)

                    except pytubefix.exceptions.BotDetection:
                        await ctx.send(":warning: le bot ne peut actuellement pas lancer l'audio")
                        await vc.disconnect()
                    except pytubefix.exceptions.RegexMatchError:
                        await ctx.channel.send_message(":warning: l'audio est introuvable")
                else:
                    try:
                        embed = await p.add_audio(ctx, url, 1, self.bot.settings)
                        await ctx.send(embed=embed)
                    except pytubefix.exceptions.BotDetection:
                        await ctx.channel.send_message(":warning: le bot ne peut actuellement pas lancer l'audio")
                        await ctx.guild.voice_client.disconnect()
                    except pytubefix.exceptions.RegexMatchError:
                        await ctx.channel.send_message(":warning: l'audio est introuvable")
            if play_task is None:
                play_task = asyncio.create_task(self.boucle_musique(ctx, vc))

    async def boucle_musique(self, ctx, vc):
        global play_task
        first = True
        while vc.is_connected():
            query = self.bot.settings["guild"][ctx.guild.name]["query"]
            if not vc.is_playing() and len(query) > 0:
                current_audio = query.pop(0)
                if not first:
                    embed = await e.embed_musique(ctx, "Now playing : " + current_audio.title, current_audio.url,
                                                  current_audio)
                    await ctx.channel.send(embed=embed)
                p.play_audio(ctx, vc, current_audio)
                while vc.is_playing():
                    await asyncio.sleep(1)
                if len(query) > 0:
                    p.supprimer_musique(ctx, current_audio)
            first = False
            await asyncio.sleep(1)
        play_task = None

    @commands.hybrid_command(name="skip", description="Passe à la musique suivante")
    async def skip(self, ctx):
        if len(self.bot.settings["guild"][ctx.guild.name]["query"]) < 1:
            await ctx.send(":warning: Il n'y a pas de musique après celle-ci")
        else:
            ctx.guild.voice_client.stop()
            embed = discord.Embed(title=":next_track: Skip")
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="stop", description="Stop la musique et déconnecte le bot")
    async def stop(self, ctx):
        state = ctx.guild.voice_client
        if state is None:
            await ctx.send("Le bot est connecté à aucun salon vocal")
        else:
            await state.disconnect()
            self.bot.settings["guild"][ctx.guild.name]["query"].clear()
            for music in self.bot.settings["guild"][ctx.guild.name]["queryGlobal"]:
                p.supprimer_musique(ctx, music)
            play_task = None
            await ctx.send("Déconnecté")

    @commands.hybrid_command(name="queue", description="Affiche la liste de lecture")
    async def queue(self, ctx):
        embed = discord.Embed(title="Liste de lecture")
        query = self.bot.settings["guild"][ctx.guild.name]["query"]
        if len(query) <= 0:
            await ctx.send(":warning: La liste est vide")
        else:
            for i in range(len(query)):
                embed.add_field(name=str(i + 1) + ". " + query[i].title, value="", inline=False)
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="request",
                             description="Envoie une demande au modérateur du bot pour pouvoir activer les commandes musicales")
    @discord.app_commands.describe(raison="Si vous souhaitez vous justifier")
    async def request(self, ctx, raison: str = None):
        user = await self.bot.fetch_user(self.bot.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=e.embed_request(ctx, raison))
        await ctx.send("Votre demande a bien été transmise")


async def setup(bot):
    await bot.add_cog(MusiqueCog(bot))
