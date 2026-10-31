from sqlmodel import Field, SQLModel


class WhiteList(SQLModel, table=True):
    __tablename__ = "White_List"
    channel_id: int = Field(primary_key=True)
    guild_id: int = Field(foreign_key="guild.id", primary_key=True)
