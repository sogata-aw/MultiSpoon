from sqlmodel import Field, SQLModel


class TriggeredChannel(SQLModel, table=True):
    __tablename__ = "Triggered_Voice_Channel"
    voice_channel_id: int = Field(primary_key=True)
    guild_id: int = Field(foreign_key="guild.id", primary_key=True)
