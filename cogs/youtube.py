import asyncio
import hashlib

import discord
import pytubefix.exceptions
from discord.ext import commands, tasks

import datetime as d
import traceback

from classes.music import Music
from pytubefix import YouTube

@discord.app_commands.guild_only()
class YoutubeCog(commands.GroupCog, group_name="youtube"):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.bot.tree.error(coro=self.on_app_command_error)
        self.play_query = {}
        self.music_list : list[Music] = []


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

    @discord.app_commands.command(name="play", description="Permet de jouer une musique via un url dans votre salon vocal")
    @discord.app_commands.describe(url="L'url de la vidéo que vous souhaitez écouter")
    async def play(self, interaction : discord.Interaction, url : str):
        voice_chat = interaction.user.voice.channel

        if not voice_chat:
            await interaction.send_message(":x: Vous n'êtes pas dans un salon vocal")
        else:
            try:
                music = YouTube(url)
                added = False
                i = 0
                while not added and i < len(self.music_list):
                    if self.music_list[i].url == url:
                        if interaction.guild.name not in self.music_list[i].requested:
                            self.music_list[i].requested.append(interaction.guild.name)
                        added = True
                    i += 1

                if not added :
                    self.music_list.append(Music(music.title, url, interaction.guild.name))

                if not discord.utils.get(self.bot.voice_clients, guild=interaction.guild):
                    await voice_chat.connect()
                    self.download.start()
                    await asyncio.create_task(self.stream(interaction))
                    await interaction.response.send_message("Connecté")

            except pytubefix.exceptions.RegexMatchError :
                await interaction.response.send_message("Le lien est invalide")


    @discord.app_commands.command(name="stop",
                                  description="Stop la musique et déconnecte le bot")
    async def stop(self, interaction : discord.Interaction):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if not voice_client :
            await interaction.send_message("Le bot est pas dans un salon")
        else:
            await voice_client.disconnect()
            await interaction.response.send_message("Déconnecté")

    @tasks.loop(seconds=5)
    async def download(self):
        for music in self.music_list:
            if not music.downloaded:
                music.download()
                music.downloaded = True

                for guild in music.requested:
                    if not self.play_query.get(guild):
                        self.play_query[guild] = []
                    self.play_query[guild].append(music.title + ".opus")


    async def stream(self, interaction):
        voice_client : discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        i = 0

        while not self.play_query.get(interaction.guild.name):
            await asyncio.sleep(0.1)

        while i < len(self.play_query[interaction.guild.name]):
            if not voice_client.is_playing():
                voice_client.play(discord.FFmpegOpusAudio("music/" + self.play_query[interaction.guild.name][0]))
                await interaction.channel.send("Playing " + self.play_query[interaction.guild.name][0])

            while voice_client.is_playing():
                await asyncio.sleep(0.1)

            i += 1



async def setup(bot):
    await bot.add_cog(YoutubeCog(bot))