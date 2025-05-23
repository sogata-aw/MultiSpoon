import asyncio

import discord

from pytubefix import YouTube, Playlist
from dotenv import load_dotenv

import os
from base64 import b64encode, b64decode
from utilities import music as m
from utilities import embeds as e

load_dotenv('../.env')

ffmpeg = os.getenv('FFMPEG')
taskdl = None

async def download_music(url, interaction, audio, settings):
    audio.streams.filter(only_audio=True).first().download(output_path="./music/" + interaction.guild.name + "/",
                                                           filename=str(b64encode(audio.title.encode())) + ".m4a")
    current = m.Music(url, audio.title, "./music/" + interaction.guild.name + "/" + audio.title + ".m4a", audio.thumbnail_url,
                      audio.length)
    settings["guilds"][interaction.guild.name]["query"].append(current)
    settings["guilds"][interaction.guild.name]["queryGlobal"].append(current)
    return current

async def get_audio(interaction, url: str, settings: dict):
    if "list" not in url:
        yt = YouTube(url)
        music = await download_music(url, interaction, yt, settings)
    else:
        yt = Playlist(url)
        music = await download_music(url, interaction, yt.videos[0], settings)
        await interaction.channel.send(embed=await e.embed_musique(interaction, "Now playing : " + yt.videos[0].title, url, yt.videos[0]))

        taskdl = asyncio.create_task(download_all(url, interaction, yt, settings))
    return music

async def download_all(url, interaction, yt, settings):
    cpt = 0
    for audio in yt.videos[1:len(yt.videos) - 1]:
        await download_music(url, interaction, audio, settings)
        cpt += 1
        print(audio.title + " ajouté à la playlist")
        await asyncio.sleep(1)

async def add_audio(interaction, url, numero: int, settings: dict) -> discord.Embed:
    current = await get_audio(interaction, url, settings)
    if current is not None:
        if numero == 0:
            embed = await e.embed_musique(interaction, "Now playing : " + current.title, url, current)
        else:
            embed = await e.embed_musique(interaction, "Added " + current.title + " to queue", url, current)
    else:
        embed = discord.Embed(title="La playlist est vide ou privée")

    return embed


def play_audio(ctx, vc, musique: m.Music):
    print("yes")
    vc.play(discord.FFmpegPCMAudio(executable=ffmpeg,
                                   source="./music/" + ctx.guild.name + "/" + str(b64encode(musique.title.encode())) + ".m4a"))


def supprimer_musique(ctx, musique: m.Music):
    if os.path.isfile("./music/" + ctx.guild.name + "/" + musique.title + ".m4a"):
        os.remove("./music/" + ctx.guild.name + "/" + musique.title + ".m4a")
