import discord
import bdd


async def set_timeout(interaction: discord.Interaction, sec: int, guilds: dict[str, bdd.GuildData]):
    if sec < 30:
        await interaction.response.send_message(
            embed=discord.Embed(title=":warning: Le temps est invalide ! Il doit être supérieur à 30 secondes",
                                color=discord.Colour.yellow()))
    else:
        guilds[interaction.guild.name].timeout = sec
        await interaction.response.send_message(
            embed=discord.Embed(title="✅ Le temps avant expiration du captcha a été mis à jour",
                                color=discord.Color.green()))


async def set_role_before(interaction: discord.Interaction, role: discord.Role, guilds: dict[str, bdd.GuildData]):
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(
            embed=discord.Embed(title=":warning: Le rôle sélectionné n'est pas valide", color=discord.Colour.yellow()))
    else:
        guilds[interaction.guild.name].roleBefore = role.id
        await interaction.response.send_message(
            embed=discord.Embed(title="✅ Le rôle d'arrivée a été mis à jour", color=discord.Color.green()))


async def set_role_after(interaction: discord.Interaction, role: discord.Role, guilds: dict[str, bdd.GuildData]):
    if role is None or not isinstance(role, discord.Role):
        await interaction.response.send_message(
            embed=discord.Embed(title=":warning: Le rôle sélectionné n'est pas valide", color=discord.Colour.yellow()))
    else:
        guilds[interaction.guild.name].roleAfter = role.id
        await interaction.response.send_message(
            embed=discord.Embed(title="✅ Le rôle après vérification a été mis à jour", color=discord.Color.green()))


async def set_verification_channel(interaction: discord.Interaction, channel: discord.abc.GuildChannel, guilds: dict[str, bdd.GuildData]):
    if channel is None or not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message(
            embed=discord.Embed(title=":warning: Le salon selectionné n'est pas valide", color=discord.Colour.yellow()))
    else:
        guilds[interaction.guild.name].verificationChannel = channel.id
        await interaction.response.send_message(
            embed=discord.Embed(title="✅ Le salon des vérifications a été mis à jour", color=discord.Color.green()))
