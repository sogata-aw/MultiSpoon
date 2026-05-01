import discord
from discord.ext import commands

from bdd import LinkData
from bot import MultiSpoon
from utilities.embeds import embed_link
from view.linkView import LinkView


def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    return discord.app_commands.check(predicate)


class LinkCog(commands.GroupCog, group_name="interserveurs"):
    def __init__(self, bot: MultiSpoon):
        self.bot = bot
        self.bot.tree.error(coro=self.bot.on_app_command_error)

    @is_admin()
    @discord.app_commands.command(name="link", description="Permet de lier des salons entre eux")
    @discord.app_commands.describe(server_id="L'id du serveur du salon qui va recevoir les messages",
                                   channel_id="L'id du salon qui va recevoir les messages")
    async def link(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        guild = self.bot.get_guild(int(server_id))

        if not guild:
            await interaction.response.send_message(embed=discord.Embed(
                title=":warning: Le bot n'est pas présent dans le serveur du salon que vous souhaitez associer",
                color=discord.Colour.red()))
            return

        channel = guild.get_channel(int(channel_id))

        if not channel:
            await interaction.response.send_message(
                embed=discord.Embed(title=":warning: Le salon que vous souhaitez associer n'existe pas",
                                    color=discord.Colour.red()))
            return

        elif type(channel) != discord.TextChannel:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=":warning: Le salon que vous souhaitez associer n'est pas un salon textuel",
                    color=discord.Colour.red()))
            return

        data = LinkData.model_validate(
            {"guild": int(server_id), "channel": int(channel_id)})

        if interaction.channel.id not in self.bot.guilds_data[interaction.guild.id].associatedWith or data not in self.bot.guilds_data[interaction.guild.id].associatedWith[interaction.channel.id]:
            await interaction.response.send_message(
                embed=discord.Embed(title=":white_check_mark: Une demande a été envoyé dans le salon à associer",
                                    color=discord.Colour.green()))
            message = await interaction.original_response()
            await channel.send(embed=embed_link(":warning: Un serveur souhaite associer ce salon au sien !", interaction.guild, interaction.channel), view=LinkView(self.bot, interaction.channel, message))
            return
        await interaction.response.send_message(
            embed=discord.Embed(title=":warning: Le salon est déjà associé", color=discord.Colour.yellow()))

    @is_admin()
    @discord.app_commands.command(name="unlink")
    async def unlink(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        guild = self.bot.get_guild(int(server_id))
        if not guild:
            await interaction.response.send_message(embed=discord.Embed(
                title=":warning: Le bot n'est pas présent dans le serveur du salon que vous souhaitez associer",
                color=discord.Colour.red()))
            return

        channel = guild.get_channel(int(channel_id))

        if not channel:
            await interaction.response.send_message(
                embed=discord.Embed(title=":warning: Le salon que vous souhaitez associer n'existe pas",
                                    color=discord.Colour.red()))
            return

        key_to_remove = None
        for i in range(len(self.bot.guilds_data[interaction.guild.id].associatedWith[interaction.channel.id])):
            if self.bot.guilds_data[interaction.guild.id].associatedWith[interaction.channel.id][i].guild == guild.id and self.bot.guilds_data[interaction.guild.id].associatedWith[interaction.channel.id][i].channel == channel.id:
                key_to_remove = i
        if key_to_remove:
            self.bot.guilds_data[interaction.guild_id].associatedWith[interaction.channel_id].pop(key_to_remove)

        key_to_remove = None
        for i in range(len(self.bot.guilds_data[guild.id].associatedWith[channel.id])):
            if self.bot.guilds_data[guild.id].associatedWith[channel.id][i].guild == interaction.guild_id and self.bot.guilds_data[guild.id].associatedWith[channel.id][i].channel == interaction.channel_id:
                key_to_remove = i
        if key_to_remove:
            self.bot.guilds_data[guild.id].associatedWith[channel.id].pop(key_to_remove)
        await interaction.response.send_message(
            embed=discord.Embed(title=":white_check_mark: Les salons ont été dissociés",
                                color=discord.Colour.green()))


async def setup(bot):
    await bot.add_cog(LinkCog(bot))
