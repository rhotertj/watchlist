import redis
from app.config import settings


class Singleton(type):
    """
    An metaclass for singleton purpose. Every singleton class should inherit from this class by 'metaclass=Singleton'.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisClient(metaclass=Singleton):
    """Connection pooled Redis client that can be used from services to efficiently cache and retrieve data.
    """
    def __init__(self, host: int | None = None, port: int | None = None, password: int | None = None):
        self.pool = redis.ConnectionPool(
            host=host or settings.REDIS_HOST,
            port=port or settings.REDIS_PORT,
            password=password or settings.REDIS_PASSWORD,
        )

    @property
    def conn(self):
        if not hasattr(self, "_conn"):
            self.getConnection()
        return self._conn

    def getConnection(self):
        self._conn = redis.Redis(connection_pool=self.pool, decode_responses=True)
