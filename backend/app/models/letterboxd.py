from pydantic import BaseModel, computed_field, Field

class LetterboxdMovieItem(BaseModel):
    """
    A minimalistic model of Letterboxd movie information.
    """

    movie_id: str
    movie_name: str
    movie_slug: str
    streaming_options: list

    @computed_field
    @property
    def movie_url(self) -> str:
        return f"https://letterboxd.com/film/{self.movie_slug}"

class WatchlistQuery(BaseModel):
    username: str = Field(min_length=2, max_length=15, pattern="^[a-zA-Z0-9_-]+$")