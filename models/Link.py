from sqlmodel import SQLModel, Field


class Link(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    channel_id: int
    guild_id: int = Field(default=None, foreign_key='guild.id')
    linked_channel_id: int
    linked_guild_id: int