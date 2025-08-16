from typing import Any

import discord

import bdd
from utilities import embeds as e

class AideSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Modération", emoji="🛠️"),
            discord.SelectOption(label="Captcha", emoji="✅"),
            discord.SelectOption(label="Salon/Rôle", emoji="📁")
        ]
        super().__init__(placeholder="Choisissez une option", max_values=1, min_values=1, options=options)
        self.commands = bdd.load_commands()

    async def callback(self, interaction: discord.Interaction) -> Any:
        embed = None
        if self.values[0] == "Modération":
            embed = await e.embed_aide(self.values[0], self.commands["Mod\u00e9ration"])
        elif self.values[0] == "Captcha":
            embed = await e.embed_aide(self.values[0], self.commands["Captcha"])
        elif self.values[0] == "Salon/Rôle":
            embed = await e.embed_aide(self.values[0], self.commands["Salon/R\u00F4le"])

        await interaction.response.edit_message(embed=embed)


class AideSelectView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(AideSelect())
