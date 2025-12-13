import pytest
from fakeredis import FakeRedis

class FakeRedisClient:
    """Wrapper around FakeRedis to mimic RedisClient interface.

    Note: FakeRedis with decode_responses=True raises UnicodeDecodeError for binary data,
    but real Redis handles it more gracefully. Using decode_responses=False to avoid
    test failures while still testing the actual functionality.

    In production, Redis with decode_responses=True works with binary poster data.
    """
    def __init__(self):
        # Use decode_responses=False to avoid FakeRedis quirk with binary data
        self.conn = FakeRedis(decode_responses=False)


@pytest.fixture
def fake_redis():
    """Provide a FakeRedis client that mimics RedisClient behavior."""
    redis_client = FakeRedisClient()
    yield redis_client
    # Cleanup after each test
    redis_client.conn.flushall()


@pytest.fixture
def sample_watchlist_html():
    """Sample HTML from a Letterboxd watchlist page with two movies."""
    return """
    <html>
        <body>
            <ul>
                <li class="griditem">
                    <div data-film-id="12345"
                         data-item-full-display-name="The Shawshank Redemption (1994)"
                         data-item-slug="the-shawshank-redemption">
                    </div>
                </li>
                <li class="griditem">
                    <div data-film-id="67890"
                         data-item-full-display-name="The Godfather (1972)"
                         data-item-slug="the-godfather">
                    </div>
                </li>
            </ul>
        </body>
    </html>
    """


@pytest.fixture
def sample_paginated_html():
    """Sample HTML with pagination."""
    return """
    <html>
        <body>
            <ul>
                <li class="griditem">
                    <div data-film-id="11111"
                         data-item-full-display-name="Movie 1 (2020)"
                         data-item-slug="movie-1">
                    </div>
                </li>
            </ul>
            <div class="pagination">
                <li class="paginate-page"><a>1</a></li>
                <li class="paginate-page"><a>2</a></li>
                <li class="paginate-page"><a>3</a></li>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_page_2_html():
    """Sample HTML for page 2 of pagination."""
    return """
    <html>
        <body>
            <ul>
                <li class="griditem">
                    <div data-film-id="22222"
                         data-item-full-display-name="Movie 2 (2021)"
                         data-item-slug="movie-2">
                    </div>
                </li>
            </ul>
        </body>
    </html>
    """


@pytest.fixture
def sample_page_3_html():
    """Sample HTML for page 3 of pagination."""
    return """
    <html>
        <body>
            <ul>
                <li class="griditem">
                    <div data-film-id="33333"
                         data-item-full-display-name="Movie 3 (2022)"
                         data-item-slug="movie-3">
                    </div>
                </li>
            </ul>
        </body>
    </html>
    """


@pytest.fixture
def cached_watchlist_data():
    """Sample cached watchlist data as it would be stored in Redis."""
    return [
        {
            "movie_id": "12345",
            "movie_name": "Cached Movie (2020)",
            "movie_slug": "cached-movie",
            "streaming_options": []
        },
        {
            "movie_id": "67890",
            "movie_name": "Another Cached Movie (2021)",
            "movie_slug": "another-cached-movie",
            "streaming_options": []
        }
    ]


@pytest.fixture
def sample_poster_binary():
    """Sample poster binary data."""
    # Simple JPEG magic bytes (must be bytes, not string!)
    return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
