import discord
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import (
    Guild,
    Link,
    Movie,
    Role,
    Seance,
    TempChannel,
    TriggerChannel,
    TriggeredChannel,
    Verified,
    WhiteList,
)

engine = create_async_engine("sqlite+aiosqlite:///spoon.db")
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

#----------------------GUILD-----------------------------

async def add_guild(guild: discord.Guild):
    async with async_session() as session :
        new_guild = Guild(id=guild.id, name=guild.name)
        session.add(new_guild)
        await session.commit()

async def update_guild(guild: Guild):
    async with async_session() as session :
        session.add(guild)
        await session.commit()
        await session.refresh(guild)

async def delete_guild(guild_id: int):
    async with async_session() as session :
        guild_to_remove = await session.get(Guild, guild_id)
        await session.delete(guild_to_remove)
        await session.commit()

async def get_all_guilds():
    async with async_session() as session :
        result = await session.exec(select(Guild))
        return result.all()

async def get_guild_by_id(id: int):
    async with async_session() as session :
        return await session.get(Guild, id)

#----------------------VERIFIED-----------------------------

async def is_user_verified(user_id: int, guild_id: int):
    async with async_session() as session :
        return await session.get(Verified, (user_id,guild_id))

async def add_verified(user_id: int, guild_id: int):
    async with async_session() as session :
        verified = Verified(user_id=user_id, guild_id=guild_id)
        session.add(verified)
        await session.commit()

#----------------------TEMP_CHANNELS-----------------------------

async def get_temp_channel_by_guild_id(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(TempChannel).where(TempChannel.guild_id == guild_id))
        return result.all()

async def get_temp_channel(channel_id: int):
    async with async_session() as session :
        return await session.get(TempChannel, channel_id)

async def add_temp_channel(channel_id: int, guild_id: int, name: str, category: str, type: str, duree: str):
    async with async_session() as session :
        channel = TempChannel(id=channel_id, guild_id=guild_id, name=name, category=category, type=type, duree=duree)
        session.add(channel)
        await session.commit()

async def delete_temp_channel(channel: TempChannel):
    async with async_session() as session :
        await session.delete(channel)
        await session.commit()

#----------------------WHITE_LIST-----------------------------

async def add_to_whitelist(channel_id: int, guild_id: int):
    async with async_session() as session :
        new_channel = WhiteList(channel_id=channel_id, guild_id=guild_id)
        session.add(new_channel)
        await session.commit()

async def get_white_channel(channel_id, guild_id):
    async with async_session() as session :
        return await session.get(WhiteList, (channel_id, guild_id))

async def get_whitelist_by_guild_id(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(WhiteList).where(WhiteList.guild_id == guild_id))
        return result.all()

async def delete_channel_from_whitelist(channel: WhiteList):
    async with async_session() as session :
        await session.delete(channel)
        await session.commit()

#----------------------TEMP_ROLES-----------------------------

async def get_temp_roles_by_guild_id(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(Role).where(Role.guild_id == guild_id))
        return result.all()

async def get_temp_role(role_id: int):
    async with async_session() as session :
        return await session.get(Role, role_id)

async def add_temp_role(role_id: int, guild_id: int, name: str, duree: str):
    async with async_session() as session :
        role = Role(id=role_id, guild_id=guild_id, name=name, duree=duree)
        session.add(role)
        await session.commit()


async def delete_temp_role(role: Role):
    async with async_session() as session :
        await session.delete(role)
        await session.commit()

#----------------------TRIGGER_CHANNELS-----------------------------

async def get_trigger_channel_by_guild_id(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(TriggerChannel).where(TriggerChannel.guild_id == guild_id))
        return result.all()

async def get_trigger_channel(channel_id: int, guild_id: int):
    async with async_session() as session :
        return await session.get(TriggerChannel, (channel_id, guild_id))

async def add_trigger_channel(channel_id: int, guild_id: int):
    async with async_session() as session :
        new_channel = TriggerChannel(channel_id=channel_id, guild_id=guild_id)
        session.add(new_channel)
        await session.commit()

async def delete_trigger_channel(channel: TriggerChannel):
    async with async_session() as session :
        await session.delete(channel)
        await session.commit()

#----------------------TRIGGERED_CHANNELS-----------------------------

async def add_triggered_channel(channel_id: int, guild_id: int):
    async with async_session() as session :
        new_channel = TriggeredChannel(voice_channel_id=channel_id, guild_id=guild_id)
        session.add(new_channel)
        await session.commit()

async def get_triggered_channel_by_guild_id(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(TriggeredChannel).where(TriggeredChannel.guild_id == guild_id))
        return result.all()

async def delete_trigger_voice_channel(channel_id: int):
    async with async_session() as session :
        result = await session.exec(select(TriggeredChannel).where(TriggeredChannel.voice_channel_id == channel_id))
        channel_to_remove = result.one()
        await session.delete(channel_to_remove)
        await session.commit()

#----------------------LINK-----------------------------

async def add_link(channel_id: int, guild_id: int, linked_channel_id: int, linked_guild_id: int):
    async with async_session() as session :
        new_link = Link(channel_id=channel_id, guild_id=guild_id, linked_channel_id=linked_channel_id, linked_guild_id=linked_guild_id)
        session.add(new_link)
        await session.commit()

async def get_link(channel_id: int, guild_id: int, linked_channel_id: int, linked_guild_id):
    async with async_session() as session :
        result = await session.exec(select(Link).where(Link.guild_id == guild_id).where(Link.channel_id == channel_id).where(Link.linked_channel_id == channel_id).where(Link.linked_guild_id == linked_guild_id))
        return result.first()

async def get_links(channel_id: int, guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(Link).where(Link.guild_id == guild_id).where(Link.channel_id == channel_id))
        return result.all()

async def get_links_by_guild_id(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(Link).where(Link.guild_id == guild_id))
        return result.all()

async def delete_link(link: Link):
    async with async_session() as session :
        await session.delete(link)
        await session.commit()


#----------------------SEANCE-----------------------------

async def add_seance(guild_id: int, title: str, date: str, nb_proposal: int):
    async with async_session() as session:
        seance = Seance(guild_id=guild_id, title=title, date=date, nb_proposal=nb_proposal)
        session.add(seance)
        await session.commit()

async def get_seance(id: int):
    async with async_session() as session :
        return await session.get(Seance, id)

async def get_seances(guild_id):
    async with async_session() as session :
        response = await session.exec(select(Seance).where(Seance.guild_id == guild_id))
        return response.all()

async def delete_seance(seance: Seance):
    async with async_session() as session :
        await session.delete(seance)
        await session.commit()


#----------------------MOVIE-----------------------------

async def add_movie(seance_id: int, tmdb_id: int, title: str, description: str, image: str, proposed_by: int, note: str = ""):
    async with async_session() as session:
        movie = Movie(seance_id=seance_id, tmdb_id=tmdb_id, title=title, description=description, image=image, proposed_by=proposed_by, note=note)
        session.add(movie)
        await session.commit()

async def get_movie(movie_id: int):
    async with async_session() as session:
        return await session.get(Movie, movie_id)

async def get_movies_by_seance(seance_id: int):
    async with async_session() as session:
        response = await session.exec(select(Movie).where(Movie.seance_id == seance_id))
        return response.all()

async def get_movies_by_seance_and_user(seance_id: int, user: int):
    async with async_session() as session:
        response = await session.exec(select(Movie).where(Movie.seance_id == seance_id).where(Movie.proposed_by == user))
        return response.all()

async def get_movie_by_tmdb_id(tmbd_id: int):
    async with async_session() as session:
        response = await session.exec(select(Movie).where(Movie.tmdb_id == tmbd_id))
        return response.first()

async def delete_movie(movie: Movie):
    async with async_session() as session :
        await session.delete(movie)
        await session.commit()
