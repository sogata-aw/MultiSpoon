import discord
from discord.ext import commands

import newBDD
from bot import MultiSpoon
from utilities.permissions import is_admin


class SpoonPotCog(commands.GroupCog, group_name="spoon_pot"):
    def __init__(self, bot):
        self.bot: MultiSpoon = bot
        self.bot.tree.error(coro=self.bot.on_app_command_error)

    @is_admin()
    @discord.app_commands.guild_only()
    @discord.app_commands.command(name="set", description="Permet de définir un salon en tant que pot de cuillière")
    async def set_command(self, interaction: discord.Interaction, salon: discord.TextChannel):
        guild = await newBDD.getGuildById(interaction.guild.id)
        guild.spoon_pot = salon.id
        await newBDD.updateGuild(guild)

        await salon.send(embed=discord.Embed(title=":warning: ATTENTION ! N'ENVOYEZ PAS DE MESSAGE", description="Ce salon est là pour vous protéger des bots, tout message envoyé dans ce salon résultera en un ban de la personne", color=discord.Color.red()))
        await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le salon a été configuré comme Pot de cuillères. Tout nouveau message dans ce salon résultera en un bannissement.", color=discord.Color.green()))

    @is_admin()
    @discord.app_commands.guild_only()
    @discord.app_commands.command(name="remove", description="Permet de désactiver le pot de cuillères")
    async def remove_command(self, interaction: discord.Interaction):
        guild = await newBDD.getGuildById(interaction.guild.id)
        guild.spoon_pot = 0
        await newBDD.updateGuild(guild)

        await interaction.response.send_message(embed=discord.Embed(
            title=":white_check_mark: Le pot de cuillière a été désactivé. Les membres peuvent de nouveau discuter dans ce salon",
            color=discord.Color.green()))


async def setup(bot: MultiSpoon):
    await bot.add_cog(SpoonPotCog(bot))
