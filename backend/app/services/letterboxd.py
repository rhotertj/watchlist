from bs4 import BeautifulSoup
import httpx
import logging
import json
from typing import List
from app.models.letterboxd import LetterboxdMovieItem
from app.services.cache import RedisClient

logger = logging.getLogger("app")

class LetterboxdService:
    """Handles all requests to letterboxd, including a redis cache."""

    def __init__(self, watchlist_cache_ttl, poster_cache_ttl, cache = None):
        self.poster_cache_ttl = poster_cache_ttl
        self.watchlist_cache_ttl = watchlist_cache_ttl
        self.cache = cache or RedisClient()

    async def get_poster_by_movie(self, movie_slug: str, movie_id: str):
        """Crawl the poster of the given letterboxd movie.

        Args:
            movie_slug (str): Letterboxd movie slug.
            movie_id (str): Letterboxd movie id.

        Raises:
            FileNotFoundError: The poster could not be found.
            ConnectionRefusedError: Letterboxd could not be reached.

        Returns:
            binary: The jpg image binary.
        """
        logger.debug(f"Get poster for {movie_id} and {movie_slug}")
        if None in (movie_id, movie_slug):
            return
        cache_response = self.cache.conn.get(f"poster:{movie_id}")
        if cache_response is not None:
            logging.debug(f"Cache hit for poster of {movie_slug}")
            return cache_response

        poster_url = f"https://a.ltrbxd.com/resized/film-poster/{'/'.join(movie_id)}/{movie_id}-{movie_slug}-0-460-0-690-crop.jpg"

        async with httpx.AsyncClient() as client:
            letterboxd_response = await client.get(poster_url)
            if letterboxd_response.status_code in (403, 404):
                logger.error(f"poster of {movie_slug} returned {letterboxd_response.status_code}")
                raise FileNotFoundError("Could not find poster for given movie.")
            if letterboxd_response.status_code in (500, 503):
                logger.error(f"poster of {movie_slug} returned {letterboxd_response.status_code}")
                raise ConnectionRefusedError("Could not reach letterboxd.")
            
            logger.debug(f"Set cache poster for {movie_slug}")
            self.cache.conn.set(
                f"poster:{movie_id}",
                ex=self.poster_cache_ttl,
                value=letterboxd_response.content,
            )

        return letterboxd_response.content

    def _extract_movies_from_page(
        self, response: httpx.Response
    ) -> tuple[List[LetterboxdMovieItem], BeautifulSoup]:
        """Parses html from the Letterboxd watchlist page and extracts all movies and their metadata.

        Args:
            response (httpx.Response): The response for the watchlist request.

        Returns:
            tuple[List[LetterboxdMovieItem], BeautifulSoup]: The parsed html and the movies from the page.
        """
        soup = BeautifulSoup(response.text, "html.parser")
        movie_data_items = soup.find_all("li", class_="griditem")
        movie_items = []
        for item in movie_data_items:
            movie = LetterboxdMovieItem(
                movie_id=item.find("div").get("data-film-id"),
                movie_name=item.find("div").get("data-item-full-display-name"),
                movie_slug=item.find("div").get("data-item-slug"),
                streaming_options=[],
            )
            movie_items.append(movie)

            self.cache.conn.set(
                f"movie:{movie.movie_id}", value=json.dumps(movie.model_dump())
            )  # TODO: Consider using redis pipelines

        return movie_items, soup

    async def get_watchlist_by_username(self, username: str) -> List[LetterboxdMovieItem] | None:
        """Scrapes the letterboxd watchlist page for movies for the given username.
        Also handles pagination for longer watchlists.

        Args:
            username (str): Owner of the watchlist.

        Raises:
            FileNotFoundError: Watchlist could not be found for the given username.

        Returns:
            List[LetterboxdMovieItem] | None:  The watchlist for the given username.
        """
        if username == "":
            return []

        cache_response = self.cache.conn.get(f"watchlist:{username}")
        if cache_response is not None:
            logger.info(f"Cache hit for {username}")
            cache_response_json = json.loads(cache_response)
            reconstructed_models = [LetterboxdMovieItem(**data) for data in cache_response_json]
            return reconstructed_models

        watchlist_url = f"https://letterboxd.com/{username}/watchlist/"
        logger.info(f"Get watchlist from {watchlist_url}")

        movie_items = []
        async with httpx.AsyncClient() as client:
            letterboxd_response = await client.get(watchlist_url)
            if letterboxd_response.status_code != 200:
                raise FileNotFoundError("Error accessing letterboxd")

            page_movie_items, page_one_soup = self._extract_movies_from_page(
                letterboxd_response
            )
            movie_items.extend(page_movie_items)

            num_pages = len(page_one_soup.find_all("li", class_="paginate-page"))

            for i in range(2, num_pages + 1):  # TODO: can be parallelized
                page_response = await client.get(f"{watchlist_url}page/{i}/")
                page_movie_items, _ = self._extract_movies_from_page(page_response)
                movie_items.extend(page_movie_items)

        self.cache.conn.set(
            f"watchlist:{username}",
            ex=self.watchlist_cache_ttl,
            value=json.dumps([item.model_dump() for item in movie_items]),
        )

        return movie_items
