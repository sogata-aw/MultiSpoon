import discord


class VoteView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.add_item(discord.ui.Button(label="Voter sur Top.gg", style=discord.ButtonStyle.blurple, disabled=False,
                                        url="https://top.gg/bot/1230871183948251206/vote"))
