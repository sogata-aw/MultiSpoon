import discord.ui


class SupportView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.add_item(discord.ui.Button(label="Rejoindre le serveur", style=discord.ButtonStyle.blurple, disabled=False,
                                        url="https://discord.gg/aeCDNDByH8"))
