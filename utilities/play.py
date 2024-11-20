import discord
from pytubefix import YouTube
import os

from utilities import music as m
from utilities import embeds as e

ffmpeg = "/ProgramData/chocolatey/lib/ffmpeg-full/tools/ffmpeg/bin/ffmpeg.exe"


async def get_audio(ctx, url: str, settings: dict):
    yt = YouTube(url)
    yt.streams.filter(only_audio=True).first().download(output_path="./music/" + ctx.guild.name + "/",
                                                        filename=yt.title + ".m4a")
    settings[ctx.guild.name]["query"].append(
        m.Music(url, yt.title, "./music/" + ctx.guild.name + "/" + yt.title + ".m4a", yt.thumbnail_url, yt.length))
    print(yt.title + " ajouté à la playlist")


async def add_audio(ctx, url, numero: int, settings: dict) -> discord.Embed:
    await get_audio(ctx, url, settings)
    if numero == 0:
        embed = await e.embed_musique(ctx, "Now playing : " + settings[ctx.guild.name]["query"][0].title, url, settings)
    else:
        embed = await e.embed_musique(ctx, "Added " + settings[ctx.guild.name]["query"][
            len(settings[ctx.guild.name]["query"]) - 1].title + " to queue", url, settings)
    return embed


def play_audio(ctx, vc, settings: dict):
    vc.play(discord.FFmpegPCMAudio(executable=ffmpeg,
                                   source="./music/" + ctx.guild.name + "/" + settings[ctx.guild.name]["query"][
                                       0].title + ".m4a"))


def supprimer_musique(ctx, query: list):
    os.remove("./music/" + ctx.guild.name + "/" + query[0].title + ".m4a")
    query.pop(0)
