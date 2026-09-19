import discord

from cogs import seance
import newBDD


class SuggestView(discord.ui.View):
    def __init__(self, bot, embed, seance, movie):
        super().__init__(timeout=300)
        self.bot = bot
        self.embed = embed
        self.seance = seance
        self.movie = movie

    @discord.ui.button(label="Proposer ce film", style=discord.ButtonStyle.green, emoji="✅", disabled=False)
    async def suggest(self, interaction: discord.Interaction, button: discord.ui.Button):
        await newBDD.addMovie(self.seance, self.movie["id"], self.movie["title"], self.movie["overview"], self.movie["poster_path"], interaction.user.id)
        await interaction.response.send_message(embed=self.embed)

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.green, emoji="❌", disabled=False)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.delete_original_response()
