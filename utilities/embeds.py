import discord
from utilities import music as m

async def embed_aide(option, dico):
    embed = discord.Embed(title=option)
    for value in dico:
        embed.add_field(name=value, value=dico[value], inline=False)
    return embed


async def embed_musique(interaction, title: str, url: str, musique: m.Music) -> discord.Embed:
    embed = discord.Embed(title=title, url=url)
    embed.set_footer(text="requested by " + interaction.user.name)
    embed.set_image(url=musique.thumbnail_url)
    return embed


async def embed_request(interaction, raison):
    embed = discord.Embed(title="Quelqu'un demande l'activation du bot pour la musique")
    embed.add_field(name="Demandé par ", value=f"{interaction.user.mention}, {interaction.user.name}")
    embed.set_image(url=interaction.author.display_icon)
    embed.add_field(name="Sur le serveur ", value=interaction.guild.name)
    if raison is not None:
        embed.add_field(name="Raison :", value=raison)
    return embed


async def embed_add(title, guild):

    embed = discord.Embed(title=title, color=0x00ff00)
    embed.set_thumbnail(url=guild.icon)
    embed.set_author(name=guild.name)
    embed.add_field(name="Nom du serveur", value=guild.name, inline=False)
    embed.add_field(name="ID du serveur", value=guild.id, inline=False)
    embed.add_field(name="Propriétaire du serveur", value=f"{guild.owner},{guild.owner.mention}, {guild.owner_id}",
                    inline=False)
    embed.add_field(name="Nombre de membres", value=guild.member_count, inline=False)
    embed.set_footer(text=f"Date de création du serveur : {guild.created_at}")
    return embed
