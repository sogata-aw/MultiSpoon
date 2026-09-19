import discord


def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    return discord.app_commands.check(predicate)

def is_me():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == 649268058652672051

    return discord.app_commands.check(predicate)
