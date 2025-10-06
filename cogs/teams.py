from bot import MultiSpoon

import discord
from discord.ext import commands

from classes.player import Player
from classes.team import Team
from utilities.teamMaker import convert_string, make_teams

class TeamsCogs(commands.GroupCog, group_name="team"):
    def __init__(self, bot: MultiSpoon):
        self.bot = bot
        self.bot.tree.error(coro=self.bot.on_app_command_error)

    @discord.app_commands.command(name="make", description="Génère des teams équilibré")
    @discord.app_commands.describe(joueurs="Bien mettre les joueurs dans ce format NAME:POWER,NAME:POWER, ...",
                                   limit="Nombre maximum de joueurs par team")
    async def make(self, interaction : discord.Interaction, joueurs : str, limit : int = 3):
        players_listr : list[list[str]] = convert_string(joueurs)
        players_converted : list[Player] = []
        try:
            for player in players_listr:
                players_converted.append(Player(player[0], int(player[1])))
            teams, exclude_players = make_teams(players_converted, limit)
            await interaction.response.send_message(str(teams) + " " + str(exclude_players))
        except ValueError:
            pass

async def setup(bot: MultiSpoon):
    await bot.add_cog(TeamsCogs(bot))