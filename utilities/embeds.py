import discord

from models.Movie import Movie
from models.Seance import Seance


async def embed_aide(option: str, dico: dict[str, str]):
    embed = discord.Embed(title=option, colour=discord.Colour.from_str("#68cd67"))
    for value in dico:
        embed.add_field(name=value, value=dico[value], inline=False)
    return embed


async def embed_add(title: str, guild: discord.Guild):
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


def embed_link(title: str, guild: discord.Guild, channel: discord.TextChannel):
    embed = discord.Embed(title=title, color=discord.Colour.yellow())
    embed.set_thumbnail(url=guild.icon)
    embed.set_author(name=guild.name)
    embed.add_field(name="Nom du serveur", value=guild.name, inline=False)
    embed.add_field(name="Salon du serveur", value=channel.name, inline=False)
    return embed

def embed_log(title: str, user: discord.User):
    embed = discord.Embed(title="", description=title, color=discord.Colour.green(), timestamp=discord.utils.utcnow())
    embed.set_author(name=user.name, icon_url=user.display_avatar)
    embed.set_footer(text=f"ID: {user.id}")
    return embed

def embed_search(search, movies):
    embed = discord.Embed(title=f"Film trouvé concernant '{search}'", description="Cliquez sur le titre pour en savoir plus")
    for movie in movies:
        embed.add_field(name=f"{movie["title"]} ({movie["release_date"][:4]})", value=f"[Voir la fiche](https://www.themoviedb.org/movie/{movie["id"]})")
    return embed

def embed_movie(title: str, image: str, description: str, genres: dict, user: discord.User, notes: str=""):
    embed = discord.Embed(title=title)
    embed.set_author(name=f"Proposé par {user.name}", icon_url=user.display_avatar)
    embed.set_image(url=f"https://images.tmdb.org/t/p/original/{image}")
    embed.add_field(name="Genres :", value=', '.join(genre["name"] for genre in genres), inline=False)
    embed.add_field(name="Description :", value=description, inline=False)
    if notes:
        embed.add_field(name="Notes :", value=notes, inline=False)
    return embed

def embed_seance(bot, seance: Seance, movies: list[Movie]):
    embed = discord.Embed(title=seance.title)

    for movie in movies:
        user = bot.get_user(movie.proposed_by)
        embed.add_field(name=movie.title, value=f"Proposé par {user.display_name}")

    return embed
