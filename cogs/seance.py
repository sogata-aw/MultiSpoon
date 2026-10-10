from datetime import datetime

import discord
from discord.ext import commands

import newBDD
from bot import MultiSpoon
from utilities.embeds import embed_seance
from utilities.permissions import is_admin


class SeanceCog(commands.GroupCog, group_name="seance"):
    def __init__(self, bot: MultiSpoon):
        self.bot = bot
        self.bot.tree.error(self.bot.on_app_command_error)

    @discord.app_commands.guild_only()
    @is_admin()
    @discord.app_commands.command(name="créer", description="Créé une séance pour un film")
    async def create(self, interaction: discord.Interaction, titre:str, date: str, nb_propositions: int=1):
        await newBDD.addSeance(interaction.guild_id, titre, date, nb_propositions)
        await interaction.response.send_message(embed=discord.Embed(title=f":white_check_mark: La séance a été créé pour le {date}", color=discord.Color.green()))

    @discord.app_commands.guild_only()
    @is_admin()
    @discord.app_commands.command(name="supprimer", description="Supprime une séance et les films qui vont avec")
    async def delete(self, interaction: discord.Interaction, seance: int):
        s = await newBDD.getSeance(seance)
        movies = await newBDD.getMoviesBySeance(seance)
        for movie in movies:
            await newBDD.deleteMovie(movie)
        await newBDD.deleteSeance(s)

        await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: La séance a bien été supprimé"))

    @discord.app_commands.guild_only()
    @is_admin()
    @discord.app_commands.command(name="lister_films", description="Liste les films de la séance")
    async def list_movies(self, interaction: discord.Interaction, seance: int):
        seance_data = await newBDD.getSeance(seance)
        movies = await newBDD.getMoviesBySeance(seance)
        await interaction.response.send_message(embed=embed_seance(self.bot, seance_data, movies))

    @delete.autocomplete("seance")
    @list_movies.autocomplete("seance")
    async def autocomplete_seance(self, interaction: discord.Interaction, seance: str) -> list[discord.app_commands.Choice[int]]:
        liste = []
        seances = await newBDD.getSeances(interaction.guild_id)
        for s in seances:
            liste.append(discord.app_commands.Choice(name=s.title, value=s.id))
        return liste


async def setup(bot:MultiSpoon):
    await bot.add_cog(SeanceCog(bot))
