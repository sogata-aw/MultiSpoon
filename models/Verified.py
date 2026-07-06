from sqlmodel import SQLModel, Field

class Verified(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    guild_id: int = Field(foreign_key="guild.id", primary_key=True)
