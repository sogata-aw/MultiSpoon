import asyncio
import os

import discord
import pytubefix.exceptions
from discord.ext import commands, tasks

import datetime as d
import traceback

from classes.music import Music
from pytubefix import YouTube


before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
options = "-vn"

@discord.app_commands.guild_only()
class YoutubeCog(commands.GroupCog, group_name="youtube"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.error(coro=self.on_app_command_error)
        self.download_task = False
        self.play_query: dict[str, list[Music]] = {}
        self.music_list: list[Music] = []
        self.tasks: dict[str, asyncio.Task] = {}
        self.index = 0

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        error_time = d.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

    @discord.app_commands.command(name="play",
                                  description="Permet de jouer une musique via un url dans votre salon vocal")
    @discord.app_commands.describe(url="L'url de la vidéo que vous souhaitez écouter")
    async def play(self, interaction: discord.Interaction, url: str):
        voice_chat = interaction.user.voice.channel
        await interaction.response.defer()

        if not voice_chat:
            await interaction.send_message(":x: Vous n'êtes pas dans un salon vocal")
        else:
            try:
                if not self.play_query.get(interaction.guild.name):
                    self.play_query[interaction.guild.name] = []
                added = False
                i = 0
                while not added and i < len(self.music_list):
                    if self.music_list[i].url == url:
                        if interaction.guild.name not in self.music_list[i].requested:
                            self.music_list[i].requested.append(interaction.guild.name)
                        if self.music_list[i].downloaded:
                            self.play_query[interaction.guild.name].append(self.music_list[i])
                            await interaction.followup.send(embed=discord.Embed(title=":white_check_mark: Ajouté à la file d'attente"))
                        added = True
                    i += 1

                if not added:
                    self.music_list.append(Music.generate_music(url, interaction.guild.name))
                    await interaction.followup.send(embed=discord.Embed(title=":white_check_mark: Ajouté à la file de téléchargement"))

                if not self.download_task:
                    self.download.start()
                    self.download_task = True

                if not discord.utils.get(self.bot.voice_clients, guild=interaction.guild):
                    await voice_chat.connect()

                if not self.tasks.get(interaction.guild.name) or self.tasks[interaction.guild.name].done():
                    self.tasks[interaction.guild.name] = asyncio.create_task(self.stream(interaction))

            except pytubefix.exceptions.RegexMatchError:
                await interaction.followup.send(embed=discord.Embed(title=":x: Le lien est invalide"))

    @discord.app_commands.command(name="pause", description="Mets sur pause la musique")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message(embed=discord.Embed(title=":x: Le bot n'est pas dans un salon vocal"))
        else:
            voice_client.pause()
            await interaction.response.send_message(embed=discord.Embed(title=":pause_button: La musique a été mis sur pause"))

    @discord.app_commands.command(name="resume", description="Mets la musique sur play")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message(embed=discord.Embed(title=":x: Le bot n'est pas dans un salon vocal"))
        elif not voice_client.is_paused():
            await interaction.response.send_message(embed=discord.Embed(title=":x: La musique n'est pas mis sur pause"))
        else:
            voice_client.resume()
            await interaction.response.send_message(embed=discord.Embed(title=":arrow_forward: La musique a été mis sur play"))

    @discord.app_commands.command(name="stop",
                                  description="Stop la musique et déconnecte le bot")
    async def stop(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if not voice_client:
            await interaction.send_message(embed=discord.Embed(title=":x: Le bot est pas dans un salon"))
        else:
            self.tasks[interaction.guild.name].cancel()
            await voice_client.disconnect(force=False)
            await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le bot a été déconnecté du salon vocal"))

    @discord.app_commands.command(name="skip", description="Saute la musique et lance la suivante")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        await interaction.response.defer()

        if vc:
            vc.stop()
            await interaction.followup.send(embed=discord.Embed(title=":next_track: Skipped"))
        else:
            await interaction.followup.send(embed=discord.Embed(title=":x: Le bot n'est pas connecté"))


    @discord.app_commands.command(name="queue", description="Affiche la file d'attente")
    async def queue(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Fil d'attente")
        print(self.play_query[interaction.guild.name])
        for i in range(len(self.play_query[interaction.guild.name])):
            if i == self.index :
                embed.add_field(name=str(i + 1) + ". " + self.play_query[interaction.guild.name][i].title, value="", inline=False)
            else:
                embed.add_field(name="", value=str(i + 1) + ". " + self.play_query[interaction.guild.name][i].title,inline=False)
        await interaction.response.send_message(embed=embed)

    @tasks.loop(seconds=5)
    async def download(self):
        if not self.bot.voice_clients:
            self.download.stop()
            self.download_task = False

        for music in self.music_list:
            if not music.downloaded:
                music.download()
                music.downloaded = True

                for guild in music.requested:
                    print(self.play_query.get(guild))
                    if not self.play_query.get(guild):
                        self.play_query[guild] = []
                    self.play_query[guild].append(music)

    @tasks.loop(seconds=5)
    async def check_limit(self):
        pass

    async def stream(self, interaction):
        vc = interaction.guild.voice_client
        self.index = 0

        while not self.play_query.get(interaction.guild.name):
            await asyncio.sleep(0.1)

        while self.index < len(self.play_query[interaction.guild.name]):
            if not vc.is_playing():
                if not discord.utils.get(self.bot.voice_clients, guild=interaction.guild):
                    return
                vc.play(discord.FFmpegOpusAudio("music/" + self.play_query[interaction.guild.name][self.index].filename + ".opus", before_options=before_options, options=options))
                await interaction.channel.send(embed=self.play_query[interaction.guild.name][self.index].generate_embed(":arrow_forward: Playing"))

            while vc.is_playing() or vc.is_paused():
                await asyncio.sleep(0.1)

            self.index += 1

        self.play_query[interaction.guild.name].clear()
        return

    @staticmethod
    def get_nbfiles():
        count = 0

        for path in os.listdir('./music/'):
            # check if current path is a file
            if os.path.isfile(os.path.join('./music/', path)):
                count += 1

        return count


async def setup(bot):
    await bot.add_cog(YoutubeCog(bot))
