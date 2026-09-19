import os

import discord
import requests
from discord.ext import commands

import newBDD
from bot import MultiSpoon
from utilities.embeds import embed_movie, embed_search
from view.suggestView import SuggestView


class MovieCog(commands.GroupCog, group_name="film"):
    def __init__(self, bot: MultiSpoon):
        self.bot = bot
        self.bot.tree.error(self.bot.on_app_command_error)
        self.tmdb_token = os.getenv("TMDB_TOKEN")

    @discord.app_commands.guild_only()
    @discord.app_commands.command(name="rechercher", description="Permet de recher un film avec son titre")
    async def search(self, interaction: discord.Interaction, title: str):
        url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=fr-FR&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.tmdb_token}"
        }

        response = requests.get(url, headers=headers)
        print(response)
        movies = response.json()
        print(movies)
        text = ""

        await interaction.response.send_message(embed=embed_search(title, movies["results"]), ephemeral=True)

    @discord.app_commands.guild_only()
    @discord.app_commands.command(name="suggérer", description="Suggère un film")
    async def suggest(self, interaction: discord.Interaction, titre: int, seance: int):
        movie = await newBDD.getMovieBySeanceAndUser(seance, interaction.user.id)
        if movie:
            await interaction.response.send_message(embed=discord.Embed(title=":x: Vous avez déjà proposé un film", color=discord.Color.red()), ephemeral=True)
            return
        url = f"https://api.themoviedb.org/3/movie/{titre}?language=fr-FR"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.tmdb_token}"
        }

        response = requests.get(url, headers=headers)
        movie = response.json()
        embed=embed_movie(movie["title"], movie["poster_path"], movie["overview"], movie["genres"], interaction.user)
        await interaction.response.send_message(embed=embed, view=SuggestView(self.bot, embed, seance, movie), ephemeral=True)


    @suggest.autocomplete("titre")
    async def autocomplete_titre(self, interaction: discord.Interaction, film: str) -> list[discord.app_commands.Choice[int]]:
        movies_list = []
        url = f"https://api.themoviedb.org/3/search/movie?query={film}&include_adult=false&language=fr-FR&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.tmdb_token}"
        }

        response = requests.get(url, headers=headers)
        movies = response.json()

        for movie in movies["results"]:
            movies_list.append(discord.app_commands.Choice(name=movie["title"], value=movie["id"]))

        return movies_list

    @suggest.autocomplete("seance")
    async def autocomplete_seance(self, interaction: discord.Interaction, seance: str) -> list[discord.app_commands.Choice[int]]:
        liste = []
        seances = await newBDD.getSeances(interaction.guild_id)
        for s in seances:
            liste.append(discord.app_commands.Choice(name=s.title, value=s.id))
        return liste


async def setup(bot: MultiSpoon):
    await bot.add_cog(MovieCog(bot))
