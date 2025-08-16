import datetime
import json

import discord
from pydantic import BaseModel


class LoggerData(BaseModel):
    level: str
    format: str


class ChannelData(BaseModel):
    name: str
    id: int
    categorie: int
    type: str
    duree: str


class RoleData(BaseModel):
    name: str
    id: int
    duree: str


class GuildData(BaseModel):
    id: int
    verificationChannel: int = 0
    roleBefore: int = 0
    roleAfter: int = 0
    inVerification: list[str] = []
    alreadyVerified: list[int] = []
    channelToCheck: list[int] = []
    timeout: int = 300
    nbEssais: int = 3
    logChannel: int = 0
    tempChannels: list[ChannelData] = []
    tempRoles: list[RoleData] = []
    tempVoiceChannels: list[int] = []


guilds = {}


def load_guilds() -> dict[str, GuildData]:
    loading = {}
    with open("./data/guilds.json", "r") as json_data:
        data = json.load(json_data)
        for k in data.keys():
            loading[k] = GuildData.model_validate(data[k])

    return loading


def save_guilds(data: dict[str, GuildData]):
    with open("./data/guilds.json", "w") as json_data:
        json.dump(serialize_guilds(data), json_data, indent=4)


def load_commands():
    with open("./data/commands.json", "r") as json_data:
        return json.load(json_data)


def serialize_guilds(data: dict[str, GuildData]) -> dict:
    result = {}
    for k in data.keys():
        result[k] = data[k].model_dump()
    return result


def add_temp_channel(data: dict[str, GuildData], interaction: discord.Interaction, salon: discord.abc.GuildChannel, nom: str, typesalon: str, categorie: discord.CategoryChannel = None, duree: datetime.datetime = None):
    data[interaction.guild.name].tempChannels.append(ChannelData.model_validate({
        "name": nom.replace(' ', '-'),
        "id": salon.id,
        "categorie": categorie.id if categorie is not None else None,
        "type": typesalon,
        "duree": duree.strftime("%Y-%m-%d %H:%M:%S:%f")
    }))
    save_guilds(data)


def add_temp_role(data: dict[str, GuildData], interaction: discord.Interaction, nom: str, duree: datetime.datetime,
                  role: discord.Role):
    data[interaction.guild.name].tempRoles.append(RoleData.model_validate({
        "name": nom,
        "id": role.id,
        "duree": duree.strftime("%Y-%m-%d %H:%M:%S:%f")
    }))
    save_guilds(data)


async def add_guild(data: dict[str, GuildData], guild: discord.Guild):
    data[guild.name] = GuildData.model_validate({
        "id": guild.id
    })
    save_guilds(data)


async def remove_guild(data, guild):
    del data[guild.name]
    save_guilds(data)
