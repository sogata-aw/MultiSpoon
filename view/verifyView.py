import discord.ui

class VerifyView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="Verifier", style=discord.ButtonStyle.green, emoji="✅", disabled=False)
    async def button_verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self.bot.get_cog("ModerationCog")

        #Recréation du context
        ctx = await self.bot.get_context(interaction.message)
        ctx.author = interaction.user
        ctx.channel = interaction.channel
        ctx.guild = interaction.guild

        #Invocation de la commande
        await cog.verify(ctx)
