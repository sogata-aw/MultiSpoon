import json

from pydantic import BaseModel
from typing import Optional

class LoggerData(BaseModel):
    level: str
    format: str


class ChannelData(BaseModel):
    name: str
    id: int
    categorie: Optional[int]
    type: str
    duree: str


class RoleData(BaseModel):
    name: str
    id: int
    duree: str

class LinkData(BaseModel):
    guild: int
    channel: int

class GuildData(BaseModel):
    name: str
    id: int
    verificationChannel: int = 0
    roleBefore: int = 0
    roleAfter: int = 0
    alreadyVerified: list[int] = []
    channelToCheck: list[int] = []
    timeout: int = 300
    logChannel: int = 0
    tempChannels: list[ChannelData] = []
    tempRoles: list[RoleData] = []
    tempVoiceChannels: list[int] = []
    whiteListActive: bool = False
    onCreateChannel: bool = False
    whiteList: list[int] = []
    associatedWith: dict[int, list[LinkData]] = {}
    spoonPot: int = 0

guilds = {}


def load_guilds() -> dict[int, GuildData]:
    loading = {}
    with open("./data/guilds.json", "r") as json_data:
        data = json.load(json_data)
        for k in data.keys():
            loading[int(k)] = GuildData.model_validate(data[k])

    return loading

def load_commands():
    with open("./data/commands.json", "r") as json_data:
        return json.load(json_data)
