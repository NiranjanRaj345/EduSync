from upstash_redis import Redis
import logging
import time
import asyncio
from flask import current_app
from functools import wraps

logger = logging.getLogger(__name__)

def retry_on_error(retries=3, delay=0.1):
    """Decorator to retry Redis operations on failure"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(f"Redis operation failed (attempt {attempt + 1}/{retries}): {str(e)}")
                    if attempt < retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
            logger.error(f"Redis operation failed after {retries} attempts: {str(last_error)}")
            raise last_error
        return wrapper
    return decorator

class RedisManager:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls._instance.initialized = False
            cls._instance.client = None
        return cls._instance

    def __init__(self):
        self.client = None

    def init_app(self, app):
        """Initialize Redis with Flask application context"""
        try:
            self.client = Redis(
                url=app.config['UPSTASH_REDIS_REST_URL'],
                token=app.config['UPSTASH_REDIS_REST_TOKEN']
            )
            self.initialized = True
            logger.info("Redis client initialized successfully with connection pooling")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {str(e)}")
            raise

    def _ensure_initialized(self):
        """Ensure Redis client is initialized"""
        if not self.initialized:
            raise RuntimeError("Redis client not initialized. Call init_app() first.")

    async def _execute_redis_command(self, command, *args, **kwargs):
        """Execute Redis command and handle non-coroutine results"""
        try:
            command_name = command.__name__ if hasattr(command, '__name__') else str(command)
            logger.debug(f"Executing Redis command: {command_name}, args: {args}, kwargs: {kwargs}")
            
            result = command(*args, **kwargs)
            if asyncio.iscoroutine(result):
                result = await result
                
            logger.debug(f"Redis command result: {command_name} -> {result}")
            return result
        except Exception as e:
            logger.error(f"Redis command failed: {command_name}, error: {str(e)}")
            raise

    @retry_on_error()
    async def ping(self):
        """Test Redis connection with retry"""
        self._ensure_initialized()
        result = await self._execute_redis_command(self.client.ping)
        return result == "PONG"

    @retry_on_error()
    async def get(self, key):
        """Get value for key with retry"""
        self._ensure_initialized()
        return await self._execute_redis_command(self.client.get, key)

    @retry_on_error()
    async def set(self, key, value, ex=None):
        """Set key-value pair with retry"""
        self._ensure_initialized()
        return await self._execute_redis_command(self.client.set, key, value, ex=ex)

    @retry_on_error()
    async def delete(self, key):
        """Delete a key with retry"""
        self._ensure_initialized()
        return await self._execute_redis_command(self.client.delete, key)

    @retry_on_error()
    async def exists(self, key):
        """Check if key exists with retry"""
        self._ensure_initialized()
        return await self._execute_redis_command(self.client.exists, key)

    @retry_on_error()
    async def increment(self, key):
        """Increment value for key with retry"""
        self._ensure_initialized()
        return await self._execute_redis_command(self.client.incr, key)

    @retry_on_error()
    async def set_expiry(self, key, seconds):
        """Set expiration for key with retry"""
        self._ensure_initialized()
        return await self._execute_redis_command(self.client.expire, key, seconds)

    @retry_on_error()
    async def acquire_lock(self, lock_key, expiry=10):
        """Acquire a distributed lock"""
        self._ensure_initialized()
        return await self._execute_redis_command(
            self.client.set,
            f"lock:{lock_key}",
            "1",
            nx=True,
            ex=expiry
        )

    @retry_on_error()
    async def release_lock(self, lock_key):
        """Release a distributed lock"""
        self._ensure_initialized()
        return await self._execute_redis_command(self.client.delete, f"lock:{lock_key}")

    async def recreate_session(self, old_sid, new_sid, data, expiry=86400):
        """Atomically recreate a session with a new ID"""
        self._ensure_initialized()
        try:
            # Try to acquire lock
            lock_acquired = await self.acquire_lock(f"session_recreate:{old_sid}")
            if not lock_acquired:
                return False

            # Copy data to new session and delete old one
            set_result = await self.set(new_sid, data, ex=expiry)
            del_result = await self.delete(old_sid)
            return set_result and del_result is not None
        finally:
            # Always release the lock
            await self.release_lock(f"session_recreate:{old_sid}")
