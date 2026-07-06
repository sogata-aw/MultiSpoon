from sqlmodel import SQLModel, Field


class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    guild_id: int = Field(default=None, foreign_key='guild.id')
    name: str
    duree: str