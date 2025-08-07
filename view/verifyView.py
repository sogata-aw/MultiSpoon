import discord.ui
from cogs.moderation import ModerationCog

class VerifyView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="Verifier", style=discord.ButtonStyle.green, emoji="✅", disabled=False)
    async def button_verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self.bot.get_cog("ModerationCog")

        #Invocation de la commande
        await cog.verify.callback(cog, interaction)
