import pytest
import httpx
import respx
import json
from app.services.letterboxd import LetterboxdService
from app.models.letterboxd import LetterboxdMovieItem


class TestGetWatchlistByUsername:
    """Tests for get_watchlist_by_username method."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_empty_username_returns_empty_list(self, fake_redis):
        """Empty username should return an empty list without making any requests."""
        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        result = await service.get_watchlist_by_username("")

        assert result == []
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_cache_hit_returns_cached_data(
        self, fake_redis, cached_watchlist_data
    ):
        """When watchlist is in cache, should return cached data without HTTP request."""
        username = "testuser"

        # Pre-populate cache (encode as bytes for FakeRedis with decode_responses=False)
        fake_redis.conn.set(
            f"watchlist:{username}", json.dumps(cached_watchlist_data).encode(), ex=3600
        )

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        result = await service.get_watchlist_by_username(username)

        assert len(result) == 2
        assert isinstance(result[0], LetterboxdMovieItem)
        assert result[0].movie_id == "12345"
        assert result[0].movie_name == "Cached Movie (2020)"
        assert result[1].movie_id == "67890"

    @pytest.mark.asyncio
    @pytest.mark.unit
    @respx.mock
    async def test_successful_watchlist_scrape(self, fake_redis, sample_watchlist_html):
        """Should successfully scrape watchlist and cache results."""
        username = "testuser"

        # Mock the HTTP response
        respx.get(f"https://letterboxd.com/{username}/watchlist/").mock(
            return_value=httpx.Response(200, text=sample_watchlist_html)
        )

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        result = await service.get_watchlist_by_username(username)

        # Verify results
        assert len(result) == 2
        assert result[0].movie_id == "12345"
        assert result[0].movie_name == "The Shawshank Redemption (1994)"
        assert result[0].movie_slug == "the-shawshank-redemption"
        assert result[1].movie_id == "67890"
        assert result[1].movie_name == "The Godfather (1972)"

        # Verify cache was populated (decode bytes from FakeRedis)
        cached_data = fake_redis.conn.get(f"watchlist:{username}")
        assert cached_data is not None
        cached_json = json.loads(cached_data.decode() if isinstance(cached_data, bytes) else cached_data)
        assert len(cached_json) == 2

        # Verify individual movies were cached
        movie_1 = fake_redis.conn.get("movie:12345")
        assert movie_1 is not None
        movie_1_json = json.loads(movie_1.decode() if isinstance(movie_1, bytes) else movie_1)
        assert movie_1_json["movie_name"] == "The Shawshank Redemption (1994)"

    @pytest.mark.asyncio
    @pytest.mark.unit
    @respx.mock
    async def test_404_raises_file_not_found(self, fake_redis):
        """Should raise FileNotFoundError when watchlist doesn't exist."""
        username = "nonexistent"

        respx.get(f"https://letterboxd.com/{username}/watchlist/").mock(
            return_value=httpx.Response(404, text="Not found")
        )

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        with pytest.raises(FileNotFoundError, match="Error accessing letterboxd"):
            await service.get_watchlist_by_username(username)

    @pytest.mark.asyncio
    @pytest.mark.unit
    @respx.mock
    async def test_pagination_handling(
        self, fake_redis, sample_paginated_html, sample_page_2_html, sample_page_3_html
    ):
        """Should handle pagination and fetch all pages."""
        username = "userwithlonglist"

        # Mock page 1 with pagination
        respx.get(f"https://letterboxd.com/{username}/watchlist/").mock(
            return_value=httpx.Response(200, text=sample_paginated_html)
        )

        # Mock page 2
        respx.get(f"https://letterboxd.com/{username}/watchlist/page/2/").mock(
            return_value=httpx.Response(200, text=sample_page_2_html)
        )

        # Mock page 3
        respx.get(f"https://letterboxd.com/{username}/watchlist/page/3/").mock(
            return_value=httpx.Response(200, text=sample_page_3_html)
        )

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        result = await service.get_watchlist_by_username(username)

        # Should have movies from all 3 pages
        assert len(result) == 3
        assert result[0].movie_id == "11111"
        assert result[0].movie_name == "Movie 1 (2020)"
        assert result[1].movie_id == "22222"
        assert result[1].movie_name == "Movie 2 (2021)"
        assert result[2].movie_id == "33333"
        assert result[2].movie_name == "Movie 3 (2022)"

    @pytest.mark.asyncio
    @pytest.mark.unit
    @respx.mock
    async def test_cache_ttl_is_respected(self, fake_redis, sample_watchlist_html):
        """Should set cache with correct TTL."""
        username = "testuser"
        cache_ttl = 1800  # 30 minutes

        respx.get(f"https://letterboxd.com/{username}/watchlist/").mock(
            return_value=httpx.Response(200, text=sample_watchlist_html)
        )

        service = LetterboxdService(
            watchlist_cache_ttl=cache_ttl, poster_cache_ttl=86400, cache=fake_redis
        )

        await service.get_watchlist_by_username(username)

        # Check TTL is set correctly
        ttl = fake_redis.conn.ttl(f"watchlist:{username}")
        assert ttl > 0
        assert ttl <= cache_ttl


class TestGetPosterByMovie:
    """Tests for get_poster_by_movie method."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_none_parameters_returns_none(self, fake_redis):
        """Should return None if movie_id or movie_slug is None."""
        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        result = await service.get_poster_by_movie(None, "12345")
        assert result is None

        result = await service.get_poster_by_movie("movie-slug", None)
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_cache_hit_returns_cached_poster(
        self, fake_redis, sample_poster_binary
    ):
        """Should return cached poster without making HTTP request."""
        movie_id = "12345"
        movie_slug = "test-movie"

        # Pre-populate cache
        fake_redis.conn.set(f"poster:{movie_id}", sample_poster_binary, ex=86400)

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        result = await service.get_poster_by_movie(movie_slug, movie_id)

        assert result == sample_poster_binary

    @pytest.mark.asyncio
    @pytest.mark.unit
    @respx.mock
    async def test_successful_poster_fetch(self, fake_redis, sample_poster_binary):
        """Should successfully fetch and cache poster."""
        movie_id = "12345"
        movie_slug = "the-shawshank-redemption"

        # Expected URL format
        expected_url = f"https://a.ltrbxd.com/resized/film-poster/1/2/3/4/5/12345-{movie_slug}-0-460-0-690-crop.jpg"

        respx.get(expected_url).mock(
            return_value=httpx.Response(
                200,
                content=sample_poster_binary,
                headers={"content-type": "image/jpeg"},
            )
        )

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        result = await service.get_poster_by_movie(movie_slug, movie_id)

        assert result == sample_poster_binary

        # Verify poster was cached
        cached_poster = fake_redis.conn.get(f"poster:{movie_id}")
        assert cached_poster == sample_poster_binary

    @pytest.mark.asyncio
    @pytest.mark.unit
    @respx.mock
    async def test_404_raises_file_not_found(self, fake_redis):
        """Should raise FileNotFoundError for 404 response."""
        movie_id = "99999"
        movie_slug = "nonexistent-movie"

        expected_url = f"https://a.ltrbxd.com/resized/film-poster/9/9/9/9/9/99999-{movie_slug}-0-460-0-690-crop.jpg"

        respx.get(expected_url).mock(return_value=httpx.Response(404))

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        with pytest.raises(FileNotFoundError, match="Could not find poster"):
            await service.get_poster_by_movie(movie_slug, movie_id)

    @pytest.mark.asyncio
    @pytest.mark.unit
    @respx.mock
    async def test_403_raises_file_not_found(self, fake_redis):
        """Should raise FileNotFoundError for 403 response."""
        movie_id = "99999"
        movie_slug = "forbidden-movie"

        expected_url = f"https://a.ltrbxd.com/resized/film-poster/9/9/9/9/9/99999-{movie_slug}-0-460-0-690-crop.jpg"

        respx.get(expected_url).mock(return_value=httpx.Response(403))

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        with pytest.raises(FileNotFoundError, match="Could not find poster"):
            await service.get_poster_by_movie(movie_slug, movie_id)

    @pytest.mark.asyncio
    @pytest.mark.unit
    @respx.mock
    async def test_500_raises_connection_refused(self, fake_redis):
        """Should raise ConnectionRefusedError for 500 response."""
        movie_id = "99999"
        movie_slug = "error-movie"

        expected_url = f"https://a.ltrbxd.com/resized/film-poster/9/9/9/9/9/99999-{movie_slug}-0-460-0-690-crop.jpg"

        respx.get(expected_url).mock(return_value=httpx.Response(500))

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        with pytest.raises(ConnectionRefusedError, match="Could not reach letterboxd"):
            await service.get_poster_by_movie(movie_slug, movie_id)

    @pytest.mark.asyncio
    @pytest.mark.unit
    @respx.mock
    async def test_poster_cache_ttl_is_respected(
        self, fake_redis, sample_poster_binary
    ):
        """Should set poster cache with correct TTL."""
        movie_id = "12345"
        movie_slug = "test-movie"
        poster_ttl = 7200  # 2 hours

        expected_url = f"https://a.ltrbxd.com/resized/film-poster/1/2/3/4/5/12345-{movie_slug}-0-460-0-690-crop.jpg"

        respx.get(expected_url).mock(
            return_value=httpx.Response(200, content=sample_poster_binary)
        )

        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=poster_ttl, cache=fake_redis
        )

        await service.get_poster_by_movie(movie_slug, movie_id)

        # Check TTL is set correctly
        ttl = fake_redis.conn.ttl(f"poster:{movie_id}")
        assert ttl > 0
        assert ttl <= poster_ttl


class TestExtractMoviesFromPage:
    """Tests for _extract_movies_from_page helper method."""

    @pytest.mark.unit
    def test_extract_movies_from_html(self, fake_redis, sample_watchlist_html):
        """Should correctly parse movies from HTML."""
        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        # Create a mock response
        response = httpx.Response(200, text=sample_watchlist_html)

        movies, soup = service._extract_movies_from_page(response)

        assert len(movies) == 2
        assert movies[0].movie_id == "12345"
        assert movies[0].movie_name == "The Shawshank Redemption (1994)"
        assert movies[0].movie_slug == "the-shawshank-redemption"
        assert movies[1].movie_id == "67890"
        assert movies[1].movie_name == "The Godfather (1972)"

        # Verify movies were cached individually (decode bytes from FakeRedis)
        cached_movie = fake_redis.conn.get("movie:12345")
        assert cached_movie is not None
        movie_data = json.loads(cached_movie.decode() if isinstance(cached_movie, bytes) else cached_movie)
        assert movie_data["movie_name"] == "The Shawshank Redemption (1994)"

    @pytest.mark.unit
    def test_extract_movies_from_empty_html(self, fake_redis):
        """Should handle HTML with no movies."""
        service = LetterboxdService(
            watchlist_cache_ttl=3600, poster_cache_ttl=86400, cache=fake_redis
        )

        empty_html = "<html><body><ul></ul></body></html>"
        response = httpx.Response(200, text=empty_html)

        movies, soup = service._extract_movies_from_page(response)

        assert len(movies) == 0
        assert isinstance(movies, list)
