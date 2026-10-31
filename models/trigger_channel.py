from sqlmodel import Field, SQLModel


class TriggerChannel(SQLModel, table=True):
    __tablename__ = "Trigger_Voice_Channel"
    channel_id: int = Field(primary_key=True)
    guild_id: int = Field(foreign_key="guild.id", primary_key=True)
