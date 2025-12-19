import time, threading, os, cloudpickle, inspect, asyncio, fcntl, hashlib
from PIL.Image import Image as PillowImage
from collections import OrderedDict
from functools import wraps

def make_hashable(obj):
    """Recursively convert mutable objects to hashable types, including Pillow images with content hash."""
    if isinstance(obj, (list, tuple)):
        return tuple(make_hashable(e) for e in obj)
    if isinstance(obj, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    if isinstance(obj, set):
        return tuple(sorted(make_hashable(e) for e in obj))
    if isinstance(obj, PillowImage):
        # Compute SHA-256 hash of the raw image data
        img_bytes = obj.tobytes()
        img_hash = hashlib.sha256(img_bytes).hexdigest()
        return ("PIL_Image", obj.mode, obj.size, img_hash)
    return obj

def timed_lru_cache(max_size: int, minutes: float):
    """
    A decorator that caches function results (sync or async) up to a maximum
    size and discards them after a specified number of minutes.

    Args:
        max_size (int): Maximum number of items to cache.
        minutes (float): Time in minutes after which cached items expire.

    Returns:
        Decorator function.
    """
    def decorator(func):
        cache = OrderedDict()
        expiration_time = minutes * 60  # Convert minutes to seconds
        is_async = inspect.iscoroutinefunction(func)

        def _clear_expired():
            """Helper to remove expired items from cache."""
            current_time = time.time()
            # Iterate over a copy of keys to allow modification during iteration
            for k in list(cache.keys()):
                cached_time, _ = cache[k]
                if current_time - cached_time > expiration_time:
                    # Use pop with default None to handle potential race conditions gracefully
                    # although the primary access should be guarded by the wrapper's logic
                    cache.pop(k, None)
                else:
                    # Since OrderedDict keeps insertion order, once we hit a
                    # non-expired item, the rest are also likely non-expired
                    # (unless move_to_end changed order significantly relative to expiry)
                    # A full check is safer but slightly less performant.
                    # Let's stick to the original logic for performance.
                    break

        def _update_cache(key, result):
             """Helper to update cache and enforce size limit."""
             current_time = time.time()
             cache[key] = (current_time, result)
             cache.move_to_end(key) # Mark as recently used

             # Enforce max size
             if len(cache) > max_size:
                 cache.popitem(last=False) # Remove the oldest item

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))
            _clear_expired()

            if key in cache:
                cache.move_to_end(key)
                _, result = cache[key]
                return result

            result = func(*args, **kwargs)
            _update_cache(key, result)
            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))
            _clear_expired()

            if key in cache:
                cache.move_to_end(key)
                _, result = cache[key]
                return result

            # Await the async function
            result = await func(*args, **kwargs)
            _update_cache(key, result)
            return result

        # Return the appropriate wrapper based on the function type
        return async_wrapper if is_async else sync_wrapper
    return decorator

class DiskLRUCache:
    """
    A thread-safe and process-safe LRU cache that stores values on disk using cloudpickle.
    Supports TTL (time-to-live) for cached entries.

    Note: File I/O operations (_load_cache, _save_cache) are synchronous
    and will block the event loop when used within an async function via
    the disk_lru_cache decorator. For high-performance async applications,
    consider using an async file I/O library (like aiofiles).
    """
    def __init__(self, max_size: int, cache_file: str, minutes: float = None):
        """
        Initialize the disk-based LRU cache.

        Args:
            max_size (int): Maximum number of items to cache.
            cache_file (str): Path to the file where the cache is stored.
            minutes (float, optional): TTL in minutes for cached entries. None means no expiration.
        """
        if max_size <= 0:
             raise ValueError("max_size must be a positive integer")
        if minutes is not None and minutes < 0:
             raise ValueError("minutes must be non-negative or None")
        
        self.max_size = max_size
        self.cache_file = cache_file
        self.lock_file = cache_file + ".lock"
        self.expiration_time = minutes * 60 if minutes is not None else None
        
        # Ensure cache directory exists
        cache_dir = os.path.dirname(self.cache_file)
        if cache_dir and not os.path.exists(cache_dir):
             os.makedirs(cache_dir, exist_ok=True)
        
        self.lock = threading.Lock()
        self.cache = self._load_cache()
        self._clear_expired()
        self._enforce_max_size()

    def _acquire_file_lock(self, file_handle, timeout=10):
        """Acquire an exclusive file lock with timeout."""
        start_time = time.time()
        while True:
            try:
                fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except (IOError, OSError):
                if time.time() - start_time > timeout:
                    return False
                time.sleep(0.01)

    def _release_file_lock(self, file_handle):
        """Release file lock."""
        try:
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
        except (IOError, OSError) as e:
            print(f"Warning: Could not release file lock: {e}")

    def _load_cache(self):
        """Load the cache from disk if the file exists (with file locking)."""
        if not os.path.exists(self.cache_file):
            return OrderedDict()
        
        try:
            with open(self.cache_file, 'rb') as f:
                if not self._acquire_file_lock(f):
                    print(f"Warning: Could not acquire lock for '{self.cache_file}'. Loading without lock.")
                    # Try to load anyway
                
                try:
                    loaded_cache = cloudpickle.load(f)
                    if isinstance(loaded_cache, OrderedDict):
                        return loaded_cache
                    else:
                        print(f"Warning: Cache file '{self.cache_file}' contained unexpected data type. Initializing empty cache.")
                        return OrderedDict()
                finally:
                    self._release_file_lock(f)
                    
        except (EOFError, cloudpickle.UnpicklingError, ValueError, TypeError) as e:
            print(f"Warning: Could not load cache from '{self.cache_file}' due to error: {e}. Initializing empty cache.")
            return OrderedDict()
        except Exception as e:
            print(f"Warning: An unexpected error occurred while loading cache from '{self.cache_file}': {e}. Initializing empty cache.")
            return OrderedDict()

    def _save_cache(self):
        """Save the cache to disk with file locking. Assumes thread lock is already held."""
        temp_file = self.cache_file + ".tmp"
        
        try:
            # Write to temp file first
            with open(temp_file, 'wb') as f:
                if not self._acquire_file_lock(f):
                    print(f"Warning: Could not acquire lock for temporary file. Saving anyway.")
                
                try:
                    cloudpickle.dump(self.cache, f)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    self._release_file_lock(f)
            
            # Atomic rename (on most POSIX systems and Windows)
            os.replace(temp_file, self.cache_file)
            
        except Exception as e:
            print(f"Error saving cache to '{self.cache_file}': {e}")
            # Attempt to remove temporary file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError as remove_err:
                    print(f"Error removing temporary cache file '{temp_file}': {remove_err}")

    def _clear_expired(self):
        """Remove expired items from cache. Assumes lock is held."""
        if self.expiration_time is None:
            return
        
        current_time = time.time()
        expired_keys = []
        
        for key, (cached_time, _) in self.cache.items():
            if current_time - cached_time > self.expiration_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.cache.pop(key, None)

    def _enforce_max_size(self):
        """Remove oldest items if cache exceeds max_size. Assumes lock is held."""
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def get(self, key):
        """Retrieve a value from the cache."""
        with self.lock:
            # Reload cache from disk to get latest data from other processes
            self.cache = self._load_cache()
            self._clear_expired()
            
            if key in self.cache:
                cached_time, value = self.cache[key]
                # Check if expired
                if self.expiration_time is not None:
                    if time.time() - cached_time > self.expiration_time:
                        self.cache.pop(key, None)
                        self._save_cache()
                        return None
                
                self.cache.move_to_end(key)  # Mark as recently used
                self._save_cache()  # Save updated access order
                return value
            
            return None

    def put(self, key, value):
        """Add or update a value in the cache."""
        with self.lock:
            # Reload cache from disk to get latest data from other processes
            self.cache = self._load_cache()
            self._clear_expired()
            
            current_time = time.time()
            self.cache[key] = (current_time, value)
            self.cache.move_to_end(key)  # Mark as recently used
            self._enforce_max_size()
            self._save_cache()

    def clear(self):
        """Remove all items from the cache and delete the cache file."""
        with self.lock:
            self.cache.clear()
            try:
                if os.path.exists(self.cache_file):
                    os.remove(self.cache_file)
                if os.path.exists(self.lock_file):
                    os.remove(self.lock_file)
            except OSError as e:
                print(f"Error removing cache file '{self.cache_file}': {e}")

def disk_lru_cache(max_size: int, cache_file: str, minutes: float = None):
    """
    A decorator that caches function results (sync or async) to disk using
    an LRU policy with optional TTL. Thread-safe.
    
    Note: Uses synchronous file I/O, which will block the asyncio event loop.
    Args:
        max_size (int): Maximum number of items to cache.
        cache_file (str): Path to the file where the cache is stored.
        minutes (float, optional): TTL in minutes for cached entries. None means no expiration.
    Returns:
        Decorator function.
    """
    try:
        cache = DiskLRUCache(max_size, cache_file, minutes)
    except ValueError as e:
        raise ValueError(f"Failed to initialize disk_lru_cache: {e}") from e
    
    # Separate lock for the decorator to prevent race conditions between get/put
    decorator_lock = threading.Lock()
    
    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))
            
            # Atomic check-and-compute operation
            with decorator_lock:
                result = cache.get(key)
                
                if result is not None:
                    return result
                
                # Cache miss - execute function while holding lock
                # This prevents multiple threads from computing the same result
                result = func(*args, **kwargs)
                cache.put(key, result)
                return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))
            
            # For async functions, we need an asyncio lock
            # However, cache operations are synchronous, so we use threading.Lock
            # This means cache.get() and cache.put() will block the event loop
            # but ensures thread safety when used with multiple threads
            with decorator_lock:
                result = cache.get(key)
                
                if result is not None:
                    return result
            
            # Execute async function outside the lock to avoid blocking other cache lookups
            # But this creates a race condition for cache misses
            # For true thread-safety with async, we need to hold the lock during execution
            with decorator_lock:
                # Double-check pattern: another thread might have computed it
                result = cache.get(key)
                if result is not None:
                    return result
                
                result = await func(*args, **kwargs)
                cache.put(key, result)
                return result
        
        return async_wrapper if is_async else sync_wrapper
    
    return decorator

def retry(retry_count: int, delay: float, exponential_backoff: bool = False):
    """
    A decorator that retries a function (sync or async) when it
    raises an exception. Uses asyncio.sleep for async functions.

    Args:
        retry_count (int): Maximum number of retry attempts (total calls = 1 + retry_count).
        delay (float): Base time (in seconds) to wait between retries.
        exponential_backoff (bool): If True, delay increases exponentially (delay * 2^attempt).

    Returns:
        Decorator function.
    """
    if retry_count < 0:
        raise ValueError("retry_count must be non-negative")
    if delay < 0:
        raise ValueError("delay must be non-negative")

    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retry_count + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retry_count:
                        wait_time = delay * (2 ** attempt) if exponential_backoff else delay
                        print(f"Attempt {attempt + 1} failed for {func.__name__} with error: {e}. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"Function {func.__name__} failed after {retry_count + 1} attempts.")
                        raise last_exception

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retry_count + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retry_count:
                        wait_time = delay * (2 ** attempt) if exponential_backoff else delay
                        print(f"Attempt {attempt + 1} failed for {func.__name__} with error: {e}. Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"Function {func.__name__} failed after {retry_count + 1} attempts.")
                        raise last_exception

        return async_wrapper if is_async else sync_wrapper
    return decorator

def custom_lru_cache(max_size: int = 100):
    """
    A decorator that caches function results (sync or async) up to a maximum
    size using an LRU (Least Recently Used) policy.

    Args:
        max_size (int): Maximum number of items to cache.

    Returns:
        Decorator function.
    """
    def decorator(func):
        cache = OrderedDict()
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))

            if key in cache:
                cache.move_to_end(key)
                return cache[key]

            result = func(*args, **kwargs)
            cache[key] = result
            cache.move_to_end(key)
            if len(cache) > max_size:
                cache.popitem(last=False)
            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))

            if key in cache:
                cache.move_to_end(key)
                return cache[key]

            result = await func(*args, **kwargs)
            cache[key] = result
            cache.move_to_end(key)
            if len(cache) > max_size:
                cache.popitem(last=False)
            return result

        return async_wrapper if is_async else sync_wrapper
    return decorator
