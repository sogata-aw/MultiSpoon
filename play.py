import discord
from pytubefix import YouTube
import os

import music as m

ffmpeg = "/ProgramData/chocolatey/lib/ffmpeg-full/tools/ffmpeg/bin/ffmpeg.exe"

def create_embed(interaction, title, url,settings):
    embed = discord.Embed(title=title,url=url)
    embed.set_footer(text="requested by " + interaction.user.name)
    embed.set_image(url=settings[interaction.guild.name]["query"][len(settings[interaction.guild.name]["query"]) - 1].thumbnail_url)
    return embed

async def get_audio(interaction, url, settings):
    yt = YouTube(url)
    yt.streams.filter(only_audio=True).first().download(output_path="./music/" + interaction.guild.name + "/", filename=yt.title + ".m4a")
    settings[interaction.guild.name]["query"].append(m.Music(url, yt.title, "./music/"+ interaction.guild.name + "/" + yt.title + ".m4a", yt.thumbnail_url, yt.length))
    print(yt.title + " ajouté à la playlist")

async def add_audio(interaction, url, numero,settings):
    await get_audio(interaction, url,settings)
    if numero == 0:
        embed = create_embed(interaction, "Now playing : " + settings[interaction.guild.name]["query"][0].title, url, settings)
    else:
        embed = create_embed(interaction, "Added " + settings[interaction.guild.name]["query"][len(settings[interaction.guild.name]["query"]) - 1].title + " to queue", url,settings)
    return embed

def play_audio(interaction,vc,settings):
    vc.play(discord.FFmpegPCMAudio(executable=ffmpeg,source="./music/" + interaction.guild.name + "/" + settings[interaction.guild.name]["query"][0].title + ".m4a"))


def supprimer_musique(interaction,query):
    os.remove("./music/" + interaction.guild.name + "/" + query[0].title + ".m4a")
    query.pop(0)
    return query