import discord.ui
import newBDD


class LinkView(discord.ui.View):
    def __init__(self, bot, channel, message):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel: discord.TextChannel = channel  #Channel that send the request
        self.message = message

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green, emoji="✅", disabled=False)
    async def button_accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=discord.Embed(title=":x: Vous devez être administrateur pour accepter la demande", color=discord.Colour.red()), ephemeral=True)
            return

        await newBDD.addLink(interaction.channel_id, interaction.guild_id, self.channel.id, self.channel.id)
        await newBDD.addLink(self.channel.id, self.channel.id, interaction.channel_id, interaction.guild_id,)

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="✅ Les salons ont été associé",
                color=discord.Colour.green()
            ),
            view=None
        )
        await self.message.edit(
            embed=discord.Embed(
                title="✅ Les salons ont été associé",
                color=discord.Colour.green()
            ),
            delete_after=15
        )

    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.red, emoji="❌", disabled=False)
    async def button_refuse(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=discord.Embed(title=":x: Vous devez être administrateur pour refuser la demande", color=discord.Colour.red()), ephemeral=True)
            return
        await interaction.response.edit_message(embed=discord.Embed(title=":x: La demande a bien été refusé", color=discord.Colour.red()), view=None, delete_after=15)
        await self.message.edit(embed=discord.Embed(title=":x: La demande a été refusé", color=discord.Colour.red()))

    async def on_timeout(self):
        try:
            await self.message.edit(embed=discord.Embed(title=":warning: La demande a expiré", color=discord.Colour.yellow()), delete_after=15)
        except discord.errors.NotFound:
            return
