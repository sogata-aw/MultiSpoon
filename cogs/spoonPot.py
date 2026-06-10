import discord
from discord.ext import commands
from discord.types import embed

from bot import MultiSpoon


def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    return discord.app_commands.check(predicate)


class SpoonPotCog(commands.GroupCog, group_name="spoon_pot"):
    def __init__(self, bot):
        self.bot: MultiSpoon = bot
        self.bot.tree.error(coro=self.bot.on_app_command_error)

    @discord.app_commands.command(name="set", description="Permet de définir un salon en tant que pot de cuillière")
    @is_admin()
    async def set_command(self, interaction: discord.Interaction, salon: discord.TextChannel):
        channel = self.bot.get_channel(salon.id)
        if not channel:
            await interaction.response.send_message(embed=discord.Embed(title=":warning: Le salon sélectionné n'existe pas !", color=discord.Color.yellow()))
            return
        self.bot.guilds_data[interaction.guild.id].spoonPot = salon.id
        await salon.send(embed=discord.Embed(title=":warning: ATTENTION ! N'ENVOYEZ PAS DE MESSAGE", description="Ce salon est là pour vous protéger des bots, tout message envoyé dans ce salon résultera en un ban de la personne", color=discord.Color.red()))
        await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le salon a été configuré comme Pot de cuillères. Tout nouveau message dans ce salon résultera en un bannissement.", color=discord.Color.green()))

    @discord.app_commands.command(name="remove", description="Permet de désactiver le pot de cuillères")
    @is_admin()
    async def remove_command(self, interaction: discord.Interaction):
        self.bot.guilds_data[interaction.guild.id].spoonPot = 0
        await interaction.response.send_message(embed=discord.Embed(
            title=":white_check_mark: Le pot de cuillière a été désactivé. Les membres peuvent de nouveau discuter dans ce salon",
            color=discord.Color.green()))


async def setup(bot: MultiSpoon):
    await bot.add_cog(SpoonPotCog(bot))