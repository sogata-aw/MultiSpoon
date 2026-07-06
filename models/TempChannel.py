from sqlmodel import Field, SQLModel


class TempChannel(SQLModel, table=True):
    __tablename__ = "Temp_Channel"
    id: int = Field(primary_key=True)
    guild_id: int = Field(foreign_key="guild.id")
    name: str
    category: str
    type: str
    duree: str
