import discord


async def embed_aide(option: str, dico: dict[str, list[str]]):
    embed = discord.Embed(title=option, colour=discord.Colour.from_str("#68cd67"))
    for value in dico:
        embed.add_field(name=value, value=dico[value], inline=False)
    return embed


async def embed_add(title: str, guild: str):
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
