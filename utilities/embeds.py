import discord

async def embed_aide(option, dico):
    embed = discord.Embed(title=option)
    for value in dico:
        embed.add_field(name=value, value=dico[value], inline=False)
    return embed

async def embed_musique(ctx, title: str, url: str, settings: dict) -> discord.Embed:
    embed = discord.Embed(title=title, url=url)
    embed.set_footer(text="requested by " + ctx.author.name)
    embed.set_image(url=settings[ctx.guild.name]["query"][len(settings[ctx.guild.name]["query"]) - 1].thumbnail_url)
    return embed

async def embed_request(ctx, raison):
    embed = discord.Embed(title="Quelqu'un demande l'activation du bot pour la musique")
    embed.add_field(name="Demandé par ", value=f"{ctx.author.mention}, {ctx.author.name}")
    embed.set_image(url=ctx.author.display_icon)
    embed.add_field(name="Sur le serveur ", value=ctx.guild.name)
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