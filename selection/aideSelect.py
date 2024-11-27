from typing import Any

import discord

from utilities import embeds as e
from utilities import settings as s


class AideSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Modération", emoji="🛠️"),
            discord.SelectOption(label="Musique", emoji="🎵")
        ]
        super().__init__(placeholder="Choisissez une option", max_values=1, min_values=1, options=options)
        self.settings = s.loading()

    async def callback(self, interaction: discord.Interaction) -> Any:
        embed = None
        if self.values[0] == "Modération":
            embed = await e.embed_aide(self.values[0], self.settings["commands"]["moderation"])
        elif self.values[0] == "Musique":
            embed = await e.embed_aide(self.values[0], self.settings["commands"]["music"])
        await interaction.response.edit_message(embed=embed)


class AideSelectView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(AideSelect())
