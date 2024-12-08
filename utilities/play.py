import discord
from pytubefix import YouTube
import os
from dotenv import load_dotenv

from utilities import music as m
from utilities import embeds as e

load_dotenv('../.env')

ffmpeg = os.getenv('FFMPEG')


async def get_audio(ctx, url: str, settings: dict):
    yt = YouTube(url)
    yt.streams.filter(only_audio=True).first().download(output_path="./music/" + ctx.guild.name + "/",
                                                        filename=yt.title + ".m4a")
    current = m.Music(url, yt.title, "./music/" + ctx.guild.name + "/" + yt.title + ".m4a", yt.thumbnail_url, yt.length)
    settings[ctx.guild.name]["query"].append(current)
    settings[ctx.guild.name]["queryGlobal"].append(current)
    print(yt.title + " ajouté à la playlist")
    return current


async def add_audio(ctx, url, numero: int, settings: dict) -> discord.Embed:
    current = await get_audio(ctx, url, settings)
    if numero == 0:
        embed = await e.embed_musique(ctx, "Now playing : " + current.title, url, current)
    else:
        embed = await e.embed_musique(ctx, "Added " + current.title + " to queue", url, current)
    return embed


def play_audio(ctx, vc, musique : m.Music):
    print("yes")
    vc.play(discord.FFmpegPCMAudio(executable=ffmpeg,
                                   source="./music/" + ctx.guild.name + "/" + musique .title + ".m4a"))


def supprimer_musique(ctx, musique : m.Music):
    if os.path.isfile("./music/" + ctx.guild.name + "/" + musique.title + ".m4a"):
        os.remove("./music/" + ctx.guild.name + "/" + musique.title + ".m4a")
