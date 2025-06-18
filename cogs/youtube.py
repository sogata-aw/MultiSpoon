import discord
from discord.ext import commands

import asyncio
import datetime
import traceback

from utilities import play as p
from utilities import embeds as e
import pytubefix.exceptions

play_task = None


class YoutubeCog(commands.GroupCog, group_name="youtube"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.error(coro=self.on_app_command_error)

    # -----Commandes-----
    async def on_app_command_error(self, interaction: discord.Interaction,
                                   error: discord.app_commands.AppCommandError):
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

    @discord.app_commands.command(name="play", description="Lance un audio via l'URL youtube")
    @discord.app_commands.describe(url="Lien de la vidéo youtube que vous voulez lancer")
    async def play(self, interaction, url: str):
        if interaction.guild.name not in self.bot.settings["authorized"]:
            await interaction.response.send_message(":warning: Ce serveur n'est pas autorisé à utiliser cette commande")
        else:
            global play_task
            vc = None
            state = interaction.user.voice
            if state is None:
                await interaction.response.send_message("Vous devez être dans un salon vocal pour utiliser cette commande")
            else:
                if interaction.guild.voice_client is None:
                    vc = await state.channel.connect()
                    try:
                        await p.add_audio(interaction, url, 0, self.bot.settings)

                    except pytubefix.exceptions.BotDetection:
                        await interaction.response.send_message(":warning: le bot ne peut actuellement pas lancer l'audio")
                        await vc.disconnect()
                    except pytubefix.exceptions.RegexMatchError:
                        await interaction.response.send_message(":warning: l'audio est introuvable")
                else:
                    try:
                        embed = await p.add_audio(interaction, url, 1, self.bot.settings)
                        await interaction.response.send_message(embed=embed)
                    except pytubefix.exceptions.BotDetection:
                        await interaction.response.send_message(":warning: le bot ne peut actuellement pas lancer l'audio")
                        await interaction.guild.voice_client.disconnect()
                    except pytubefix.exceptions.RegexMatchError:
                        await interaction.response.send_message(":warning: l'audio est introuvable")
            if play_task is None:
                play_task = asyncio.create_task(self.boucle_musique(interaction, vc))

    async def boucle_musique(self, interaction, vc):
        global play_task
        first = True
        while vc.is_connected():
            query = self.bot.settings["guild"][interaction.guild.name]["query"]
            if not vc.is_playing() and len(query) > 0:
                current_audio = query.pop(0)
                if not first:
                    embed = await e.embed_musique(interaction, "Now playing : " + current_audio.title, current_audio.url,
                                                  current_audio)
                    await interaction.channel.send(embed=embed)
                p.play_audio(interaction, vc, current_audio)
                while vc.is_playing():
                    await asyncio.sleep(1)
                if len(query) > 0:
                    p.supprimer_musique(interaction, current_audio)
            first = False
            await asyncio.sleep(1)
        play_task = None

    @discord.app_commands.command(name="skip", description="Passe à la musique suivante")
    async def skip(self, interaction):
        if len(self.bot.settings["guild"][interaction.guild.name]["query"]) < 1:
            await interaction.response.send_message(":warning: Il n'y a pas de musique après celle-ci")
        else:
            interaction.guild.voice_client.stop()
            embed = discord.Embed(title=":next_track: Skip")
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="stop", description="Stop la musique et déconnecte le bot")
    async def stop(self, interaction):
        state = interaction.guild.voice_client
        if state is None:
            await interaction.response.send_message("Le bot est connecté à aucun salon vocal")
        else:
            await state.disconnect()
            self.bot.settings["guild"][interaction.guild.name]["query"].clear()
            for music in self.bot.settings["guild"][interaction.guild.name]["queryGlobal"]:
                p.supprimer_musique(interaction, music)
            play_task = None
            await interaction.response.send_message("Déconnecté")

    @discord.app_commands.command(name="queue", description="Affiche la liste de lecture")
    async def queue(self, interaction):
        embed = discord.Embed(title="Liste de lecture")
        query = self.bot.settings["guild"][interaction.guild.name]["query"]
        if len(query) <= 0:
            await interaction.response.send_message(":warning: La liste est vide")
        else:
            for i in range(len(query)):
                embed.add_field(name=str(i + 1) + ". " + query[i].title, value="", inline=False)
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="request",
                             description="Envoie une demande au modérateur du bot pour pouvoir activer les commandes musicales")
    @discord.app_commands.describe(raison="Si vous souhaitez vous justifier")
    async def request(self, interaction, raison: str = None):
        user = await self.bot.fetch_user(self.bot.createur)
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=await e.embed_request(interaction, raison))
        await interaction.response.send_message("Votre demande a bien été transmise")


async def setup(bot):
    await bot.add_cog(YoutubeCog(bot))
