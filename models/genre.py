from sqlmodel import Field, SQLModel


class Genre(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
