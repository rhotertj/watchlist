from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from logging.config import dictConfig
from app.services.letterboxd import LetterboxdService
from app.models.letterboxd import LetterboxdMovieItem, WatchlistQuery
from app.models.motn import StreamingOption
from app.services.availability import StreamingAvailabilityService
from app.services.cache import RedisClient
from app.config import settings
from typing import List
from pydantic import ValidationError
from http import HTTPStatus

# Define the logging configuration

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOGLEVEL,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console"],
            "level": settings.LOGLEVEL,
            "propagate": False,
        },
    },
    "root": {"handlers": ["console"], "level": settings.LOGLEVEL},
}

dictConfig(log_config)


logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ = RedisClient()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
    if settings.FASTAPI_ALLOW_ORIGINS == "*"
    else [
        f"https://{settings.FASTAPI_ALLOW_ORIGINS}",
        f"http://{settings.FASTAPI_ALLOW_ORIGINS}",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/watchlist")
async def get_watchlist_for_username(
    username: str,
    service: LetterboxdService = Depends(
        lambda: LetterboxdService(
            watchlist_cache_ttl=settings.WATCHLIST_CACHE_TTL,
            poster_cache_ttl=settings.POSTER_CACHE_TTL,
        )
    ),
) -> List[LetterboxdMovieItem]:
    """Get the Letterboxd watchlist for a given username. The watchlist will be scraped or retrieved in redis cache.


    Args:
        username (str): The letterboxd username.
        service (LetterboxdService, optional): Letterboxd service object. Defaults to Depends(lambda: LetterboxdService()).

    Raises:
        HTTPException: 422, if username is invalid.
        HTTPException: 424, if letterboxd cannot be reached.
        HTTPException: 404, if users' watchlist cannot be found.

    Returns:
        List[LetterboxdMovieItem]: The watchlist as an array of movies.
    """
    logger.info(f"Get watchlist for {username}")

    try:
        query = WatchlistQuery(username=username)
    except ValidationError as e:
        logger.warning(f"Invalid username format: {username}")
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=f"Invalid username: {e.errors()[0]['msg']}",
        )

    try:
        watchlist = await service.get_watchlist_by_username(
            username=query.username.lower()
        )
    except ConnectionRefusedError:
        raise HTTPException(
            status_code=HTTPStatus.FAILED_DEPENDENCY,
            detail="Failed to reach Letterboxd",
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Watchlist not found"
        )

    return watchlist


@app.get("/api/poster/{movie_slug_id}", response_class=Response(media_type="image/jpg"))
async def get_poster_for_movie(
    movie_slug_id: str,
    service: LetterboxdService = Depends(
        lambda: LetterboxdService(
            watchlist_cache_ttl=settings.WATCHLIST_CACHE_TTL,
            poster_cache_ttl=settings.POSTER_CACHE_TTL,
        )
    ),
) -> Response:
    """Returns the poster for the given movie, scraped from letterboxd.
    Since letterboxd poster URLs are not straightforward, there is a medium chance this function fails.

    Args:
        movie_slug_id (str): Letterboxd movie slug.
        service (LetterboxdService, optional): Letterboxd service object. Defaults to Depends(lambda: LetterboxdService()).

    Raises:
        HTTPException: 424, if letterboxd cannot be reached.
        HTTPException: 404, if movies' poster cannot be found.

    Returns:
        Response: The movie poster as jpg.
    """
    try:
        movie_slug, movie_id = movie_slug_id.rsplit("-", 1)
        poster_binary = await service.get_poster_by_movie(movie_slug, movie_id)
    except ConnectionRefusedError:
        raise HTTPException(
            status_code=HTTPStatus.FAILED_DEPENDENCY,
            detail="Failed to reach Letterboxd",
        )
    except FileNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Poster not found")

    return Response(content=poster_binary, media_type="image/jpg")


@app.get("/api/availability", response_model=List[StreamingOption])
async def get_availability_for_movie(
    movie_id: str,
    service: StreamingAvailabilityService = Depends(
        lambda: StreamingAvailabilityService(
            bearer_token=settings.MOVIE_AVAILABILITY_API_KEY,
            streaming_options_ttl=settings.STREAMING_CACHE_TTL,
        )
    ),
):
    """Get the movieofthenight.com streamingOptions for the given movie.

    Args:
        movie_id (str): Letterboxd movie id.
        service (StreamingAvailabilityService, optional): StreamingAvailabilityService. Defaults to Depends(lambda: StreamingAvailabilityService()).

    Raises:
        HTTPException: HTTP 424 Failed Dependency (Cannot reach Letterboxd)
        HTTPException: HTTP 404 Not found on MOTN
        HTTPException: HTTP 429 Exceeded API Rate Limit

    Returns:
        _type_: _description_
    """
    logger.info(f"Get availability for {movie_id}")
    try:
        availability = await service.get_availability_for_movie(letterboxd_id=movie_id)
    except ConnectionRefusedError:
        raise HTTPException(
            status_code=HTTPStatus.FAILED_DEPENDENCY, detail="Failed to reach api."
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Movie could not be found."
        )
    except PermissionError:
        raise HTTPException(
            status_code=HTTPStatus.TOO_MANY_REQUESTS, detail="Exceeded api rate limit."
        )
    return availability
