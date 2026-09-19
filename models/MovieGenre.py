from sqlmodel import Field, SQLModel


class MovieGenre(SQLModel, table=True):
    __tablename__ = "Movie_Genre"
    movie_id: int = Field(default=None, primary_key=True, foreign_key='movie.id')
    genre_id: int = Field(default=None, primary_key=True, foreign_key='genre.id')
