import json

import discord
from pydantic import BaseModel

class ChannelData(BaseModel):
    name: str
    id: int
    categorie: int|None
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
    guilds = {}
    with open("./data/guilds.json", "r") as json_data:
        data = json.load(json_data)
        for k in data.keys():
            guilds[k] = GuildData.model_validate(data[k])

    return guilds

def save_guilds(guilds: dict[str, GuildData]):
    with open("./data/guilds.json", "w") as json_data:
        json.dump(serializeGuilds(guilds), json_data, indent=4)

def load_commands():
    with open("./data/commands.json", "r") as json_data:
        return json.load(json_data)

def serializeGuilds(guilds: dict[str, GuildData]) -> dict:
    result = {}
    for k in guilds.keys():
        result[k] = guilds[k].model_dump()
    return result

def add_temp_channel(guilds : dict[str, GuildData], interaction : discord.Interaction, salon: discord.abc.GuildChannel, nom: str, typesalon: str, categorie: discord.CategoryChannel = None, duree : str = None):
    guilds[interaction.guild.name].tempChannels.append(ChannelData.model_validate({
        "name": nom.replace(' ', '-'),
        "id": salon.id,
        "categorie": categorie.id if categorie is not None else None,
        "type": typesalon,
        "duree": duree.strftime("%Y-%m-%d %H:%M:%S:%f")
    }))
    save_guilds(guilds)

def add_temp_role(guilds : dict[str, GuildData], interaction : discord.Interaction, nom : str, duree : str, role : discord.Role):
    guilds[interaction.guild.name].tempRoles.append(RoleData.model_validate({
        "name": nom,
        "id": role.id,
        "duree": duree.strftime("%Y-%m-%d %H:%M:%S:%f")
    }))
    save_guilds(guilds)

async def add_guild(guilds : dict[str,GuildData], guild : discord.Guild):
    guilds[guild.name] = GuildData.model_validate({
        "id": guild.id
    })
    save_guilds(guilds)

async def remove_guild(guilds, guild):
    del guilds[guild.name]
    save_guilds(guilds)