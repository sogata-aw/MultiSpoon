import discord


class SalonsView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Précédent", style=discord.ButtonStyle.gray, emoji="⏮️", disabled=True)
    async def button_previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.message.content == "test 2":
            button.disabled = True
            self.children[1].disabled = False
        await interaction.response.edit_message(content="test", view=self)

    @discord.ui.button(label="Suivant", style=discord.ButtonStyle.gray, emoji="⏭️")
    async def button_next(self, interaction, button):
        if interaction.message.content == "test":
            button.disabled = True
            self.children[0].disabled = False
        await interaction.response.edit_message(content=f"test 2", view=self)
