from sqlmodel import Field, SQLModel


class Seance(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    guild_id: int = Field(default=None, foreign_key='guild.id')
    title: str
    date: str
    nb_proposal: int
