import discord
from discord.ext import commands

class AideSelect(discord.ui.Select):
    def __init__(self):
        options =[
            discord.SelectOption(label="Modération",emoji=":tools:"),
            discord.SelectOption(label="Musique", emoji=":musical_note:")
        ]
        super().__init__(placeholder="Choisissez une option", max_values=1, min_values=1,options=options)

class AideSelectView(discord.ui.View):
    def __init__(self,timeout = 180):
        super().__init__(timeout= 180)
        self.add_item(AideSelect())

