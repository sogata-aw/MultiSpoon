from sqlmodel import Field, SQLModel


class Movie(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    seance_id: int = Field(default=None, foreign_key='seance.id')
    tmdb_id: int
    title: str
    description: str
    image: str
    proposed_by: int
    note: str
