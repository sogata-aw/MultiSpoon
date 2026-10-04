import discord
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.Guild import Guild
from models.Link import Link
from models.Movie import Movie
from models.Role import Role
from models.Seance import Seance
from models.TempChannel import TempChannel
from models.TriggerChannel import TriggerChannel
from models.TriggeredChannel import TriggeredChannel
from models.Verified import Verified
from models.WhiteList import WhiteList

engine = create_async_engine("sqlite+aiosqlite:///spoon.db")
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

#----------------------GUILD-----------------------------

async def addGuild(guild: discord.Guild):
    async with async_session() as session :
        new_guild = Guild(id=guild.id, name=guild.name)
        session.add(new_guild)
        await session.commit()

async def updateGuild(guild: Guild):
    async with async_session() as session :
        session.add(guild)
        await session.commit()
        await session.refresh(guild)

async def deleteGuild(guild_id: int):
    async with async_session() as session :
        guild_to_remove = await session.get(Guild, guild_id)
        await session.delete(guild_to_remove)
        await session.commit()

async def getAllGuilds():
    async with async_session() as session :
        result = await session.exec(select(Guild))
        return result.all()

async def getGuildById(id: int):
    async with async_session() as session :
        return await session.get(Guild, id)

#----------------------VERIFIED-----------------------------

async def isUserVerified(user_id: int, guild_id: int):
    async with async_session() as session :
        return await session.get(Verified, (user_id,guild_id))

async def addVerified(user_id: int, guild_id: int):
    async with async_session() as session :
        verified = Verified(user_id=user_id, guild_id=guild_id)
        session.add(verified)
        await session.commit()

#----------------------TEMP_CHANNELS-----------------------------

async def getTempChannelsByGuildId(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(TempChannel).where(TempChannel.guild_id == guild_id))
        return result.all()

async def getTempChannel(channel_id: int):
    async with async_session() as session :
        return await session.get(TempChannel, channel_id)

async def addTempChannel(channel_id: int, guild_id: int, name: str, category: str, type: str, duree: str):
    async with async_session() as session :
        channel = TempChannel(id=channel_id, guild_id=guild_id, name=name, category=category, type=type, duree=duree)
        session.add(channel)
        await session.commit()

async def deleteTempChannel(channel: TempChannel):
    async with async_session() as session :
        await session.delete(channel)
        await session.commit()

#----------------------WHITE_LIST-----------------------------

async def addToWhiteList(channel_id: int, guild_id: int):
    async with async_session() as session :
        new_channel = WhiteList(channel_id=channel_id, guild_id=guild_id)
        session.add(new_channel)
        await session.commit()

async def getWhiteChannel(channel_id, guild_id):
    async with async_session() as session :
        return await session.get(WhiteList, (channel_id, guild_id))

async def getWhiteListByGuildId(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(WhiteList).where(WhiteList.guild_id == guild_id))
        return result.all()

async def deleteChannelFromWhiteList(channel: WhiteList):
    async with async_session() as session :
        await session.delete(channel)
        await session.commit()

#----------------------TEMP_ROLES-----------------------------

async def getTempRolesByGuildId(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(Role).where(Role.guild_id == guild_id))
        return result.all()

async def getTempRole(role_id: int):
    async with async_session() as session :
        return await session.get(Role, role_id)

async def addTempRole(role_id: int, guild_id: int, name: str, duree: str):
    async with async_session() as session :
        role = Role(id=role_id, guild_id=guild_id, name=name, duree=duree)
        session.add(role)
        await session.commit()


async def deleteTempRole(role: Role):
    async with async_session() as session :
        await session.delete(role)
        await session.commit()

#----------------------TRIGGER_CHANNELS-----------------------------

async def getTriggerChannelByGuildId(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(TriggerChannel).where(TriggerChannel.guild_id == guild_id))
        return result.all()

async def getTriggerChannel(channel_id: int, guild_id: int):
    async with async_session() as session :
        return await session.get(TriggerChannel, (channel_id, guild_id))

async def addTriggerChannel(channel_id: int, guild_id: int):
    async with async_session() as session :
        new_channel = TriggerChannel(channel_id=channel_id, guild_id=guild_id)
        session.add(new_channel)
        await session.commit()

async def deleteTriggerChannel(channel: TriggerChannel):
    async with async_session() as session :
        await session.delete(channel)
        await session.commit()

#----------------------TRIGGERED_CHANNELS-----------------------------

async def addTriggeredChannel(channel_id: int, guild_id: int):
    async with async_session() as session :
        new_channel = TriggeredChannel(voice_channel_id=channel_id, guild_id=guild_id)
        session.add(new_channel)
        await session.commit()

async def getTriggeredChannelByGuildId(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(TriggeredChannel).where(TriggeredChannel.guild_id == guild_id))
        return result.all()

async def deleteTriggeredVoiceChannel(channel_id: int):
    async with async_session() as session :
        result = await session.exec(select(TriggeredChannel).where(TriggeredChannel.voice_channel_id == channel_id))
        channel_to_remove = result.one()
        await session.delete(channel_to_remove)
        await session.commit()

#----------------------LINK-----------------------------

async def addLink(channel_id: int, guild_id: int, linked_channel_id: int, linked_guild_id: int):
    async with async_session() as session :
        new_link = Link(channel_id=channel_id, guild_id=guild_id, linked_channel_id=linked_channel_id, linked_guild_id=linked_guild_id)
        session.add(new_link)
        await session.commit()

async def getLink(channel_id: int, guild_id: int, linked_channel_id: int, linked_guild_id):
    async with async_session() as session :
        result = await session.exec(select(Link).where(Link.guild_id == guild_id).where(Link.channel_id == channel_id).where(Link.linked_channel_id == channel_id).where(Link.linked_guild_id == linked_guild_id))
        return result.first()

async def getLinks(channel_id: int, guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(Link).where(Link.guild_id == guild_id).where(Link.channel_id == channel_id))
        return result.all()

async def getLinksByGuildId(guild_id: int):
    async with async_session() as session :
        result = await session.exec(select(Link).where(Link.guild_id == guild_id))
        return result.all()

async def deleteLink(link: Link):
    async with async_session() as session :
        await session.delete(link)
        await session.commit()


#----------------------SEANCE-----------------------------

async def addSeance(guild_id: int, title: str, date: str):
    async with async_session() as session:
        seance = Seance(guild_id=guild_id, title=title, date=date)
        session.add(seance)
        await session.commit()

async def getSeance(id: int):
    async with async_session() as session :
        return await session.get(Seance, id)

async def getSeances(guild_id):
    async with async_session() as session :
        response = await session.exec(select(Seance).where(Seance.guild_id == guild_id))
        return response.all()

async def deleteSeance(seance: Seance):
    async with async_session() as session :
        await session.delete(seance)
        await session.commit()


#----------------------MOVIE-----------------------------

async def addMovie(seance_id: int, tmdb_id: int, title: str, description: str, image: str, proposed_by: int, notes: str = ""):
    async with async_session() as session:
        movie = Movie(seance_id=seance_id, tmdb_id=tmdb_id, title=title, description=description, image=image, proposed_by=proposed_by, notes=notes)
        session.add(movie)
        await session.commit()

async def getMovie(movie_id: int):
    async with async_session() as session:
        return await session.get(Movie, movie_id)

async def getMoviesBySeance(seance_id: int):
    async with async_session() as session:
        response = await session.exec(select(Movie).where(Movie.seance_id == seance_id))
        return response.all()

async def getMovieBySeanceAndUser(seance_id: int, user: int):
    async with async_session() as session:
        response = await session.exec(select(Movie).where(Movie.seance_id == seance_id).where(Movie.proposed_by == user))
        return response.first()

async def deleteMovie(movie: Movie):
    async with async_session() as session :
        await session.delete(movie)
        await session.commit()
