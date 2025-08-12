from base64 import b64encode
import os
from dotenv import load_dotenv
import discord
import subprocess
import json

load_dotenv(".env")

ytdlp = os.getenv("YTDLP")

class Music:
    def __init__(self, title: str, url: str, requested_by: str, thumbnail : str, time : int, downloaded: bool = False):
        self.title: str = title
        self.url: str = url
        self.downloaded: str = downloaded
        self.thumbnail: str = thumbnail
        self.time: int = time
        self.filename: str = str(b64encode(self.title.encode()))
        self.requested: list[str] = [requested_by]

    def generate_embed(self, state : str) -> discord.Embed:
        embed = discord.Embed(title=f"{state} : {self.title} ({self.time_to_min()})", url=self.url)
        embed.set_image(url=self.thumbnail)

        return embed


    def download(self):
        os.system(f'{ytdlp} -x --audio-format opus --audio-quality 0 --cookies data/cookies.txt -v -P "music" -o "{self.filename}.%(ext)s" --restrict-filenames ' + self.url)

    def time_to_min(self):
        sec = self.time
        minute = 0

        while sec > 60:
            if sec >= 60:
                minute += 1
                sec -= 60

        if minute < 10 :
            minute = "0" + str(minute)
        if sec < 10 :
            sec = "0" + str(sec)

        return str(minute) + ":" + str(sec)



    def __str__(self):
        return f"[{self.title}, {self.url}, {self.downloaded}, {self.thumbnail}, {self.filename}, {self.requested}]"

    def __repr__(self):
        return str(self)

    @staticmethod
    def generate_music(url : str, guild : str):
        cmd = [ytdlp, "-j", "--cookies", "data/cookies.txt", url]

        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        info = json.loads(result.stdout)

        return Music(info["title"], url, guild, info["thumbnail"], info["duration"])