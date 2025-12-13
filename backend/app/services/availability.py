# site is down, lets mock it
from app.services.letterboxd import LetterboxdMovieItem
from app.services.cache import RedisClient
from app.models.motn import MOTNMovieSearchResults, StreamingOption
from typing import List
import httpx
import json
import re
import logging

logger = logging.getLogger("app")


class StreamingAvailabilityService:
    """Handles all requests to the movieofthenight API, including a redis cache."""

    def __init__(self, bearer_token: str, streaming_options_ttl : int ,cache = None):
        self.bearer_token = bearer_token
        self.streaming_options_ttl = streaming_options_ttl
        self.cache = cache or RedisClient()

    def _separate_title_from_year(self, title: str):
        """
        Extracts the movie title and year from a string.

        Args:
            title: A string containing the movie title, possibly with a year

        Returns:
            A tuple (title, year) where:
            - title: The movie title without the year
            - year: The year as a string, or None if no year found
        """
        # Match (year) at the end, where year is 4 digits
        match = re.search(r"\s*\((\d{4})\)\s*$", title)

        if match:
            year = match.group(1)
            clean_title = title[: match.start()].strip()
            return (clean_title, year)
        else:
            return (title.strip(), None)

    async def _search_availability_by_ID(
        self, letterboxd_id: str, country: str
    ) -> List[StreamingOption] | None:
        """Query the movieofthenight API by searching via title.
        The title is taken from the letterboxd id.

        Args:
            letterboxd_id (str): The letterboxd movie id.
            country (str): Country code, eg. "de" (ISO 3166-1 alpha-2).

        Raises:
            FileNotFoundError: No movie found for given movie id.
            FileNotFoundError: Empty search results from movieofthenight API.
            ConnectionRefusedError: Could not reach movie of the night.

        Returns:
            List[StreamingOption] | None: Most fitting search result from the movieofthenight API
        """

        logger.debug(f"Search cache for name of {letterboxd_id=}")
        cached_item = self.cache.conn.get(f"movie:{letterboxd_id}")
        if cached_item is not None:  # this should never fail if not called outside app
            movie = LetterboxdMovieItem(**json.loads(cached_item))
            logger.info(f"Cache hit for {letterboxd_id=} {movie.movie_name}")
        else:
            logger.error(f"LetterboxMovieItem for {letterboxd_id=} unexpectedly not found in cache")
            raise FileNotFoundError

        # Query Movieofthenight.com for streaming options, search by title
        async with httpx.AsyncClient() as client:
            title, year = self._separate_title_from_year(movie.movie_name)
            logger.debug(f"Query MOTN for {title, year}")
            motn_response = await client.get(
                "https://streaming-availability.p.rapidapi.com/shows/search/title",
                params={"title": title, "country": country},
                headers={"X-RapidAPI-Key": self.bearer_token},
                timeout=10.0,
            )
            response_json = json.loads(motn_response.text)

            if motn_response.status_code in (400, 403, 404) or response_json == []:
                logger.error(f"MOTN returned {motn_response.status_code=}")
                logger.error(f"{motn_response.text=}")
                raise FileNotFoundError(
                    "Could not find motn-movie for given letterboxd-id."
                )
            if motn_response.status_code in (500, 503):
                logger.error(f"MOTN returned {motn_response.status_code=}")
                logger.error(f"{motn_response.text=}")
                raise ConnectionRefusedError("Could not reach movieofthenight.")
            if motn_response.status_code == 429:
                logger.error(f"MOTN returned {motn_response.status_code=}")
                logger.error(f"{motn_response.text=}")
                raise PermissionError(
                    "Exceeded API Rate Limit"
                )

            logger.debug(f"Found {len(response_json)} results for {movie.movie_name}")
            parsed_response = MOTNMovieSearchResults(results=response_json)
            logger.debug(parsed_response)
            # Check for search results
            if not len(parsed_response.results) >= 1: 
                logger.debug(f"Skip {title}, no search results")
                return 

            # Select first result (most relevant) that matches release year
            for result in parsed_response.results:
                if result.releaseYear == int(year):
                    logger.debug("Fitting year and title: %s", result.streamingOptions)
                    options_for_country =  getattr(result.streamingOptions, country, None)
                    if options_for_country is not None:
                        return options_for_country
            
            raise FileNotFoundError(
                "Could not find motn-movie for given letterboxd-id."
            )

    async def get_availability_for_movie(
        self, letterboxd_id: str, country: str = "de"
    ) -> List[StreamingOption]:
        """Get all streaming options listed by the movieofthenight API for a given country and the letterboxd movie id.

        Args:
            letterboxd_id (str): letterboxd movie id.
            country (str, optional): Country code (ISO 3166-1 alpha-2). Defaults to "de".

        Returns:
            list: List of streaming options for the given movie.
        """
        # first check for cache of availabilities
        logger.debug(f"Get streaming_options for {letterboxd_id}")
        av_cache = self.cache.conn.get(f"streaming_options:{letterboxd_id}")
        if av_cache is not None:
            logger.debug(f"Streaming options retrieved from cache for {letterboxd_id}")
            return json.loads(av_cache)
        # cache failed, get streaming options by letterboxd id (which is used to retrieve movie name from redis)
        streaming_options : List[StreamingOption] = await self._search_availability_by_ID(
            letterboxd_id=letterboxd_id, country=country
        )
        logger.debug(streaming_options)

        self.cache.conn.set(f"streaming_options:{letterboxd_id}", json.dumps([option.model_dump() for option in streaming_options]), ex=self.streaming_options_ttl)
        return streaming_options
