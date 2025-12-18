# -*- coding: utf-8 -*-
"""
Simple in-memory string cache using only @lru_cache + string server.
No SQLite, no shared memory, no complexity.
"""
import logging
import time
from functools import lru_cache
import torch
import numpy as np

logger = logging.getLogger(__name__)


# Track string server outage state (for Slack notifications)
_STRING_SERVER_OUTAGE_NOTIFIED = False
_STRING_SERVER_RECOVERY_NOTIFIED = False


# Module-level cache for string embeddings
# Key: (client_id, sentence_text) -> embedding_list
# This allows @lru_cache to work properly (doesn't work well with instance methods)
@lru_cache(maxsize=131072)  # Increased from 32768 (2^15) to 131072 (2^17) for better hit rates
def _cached_encode(client_id, sentence_text, client_encode_func_key):
    """
    Cached encoding function at module level with retry logic for string server outages.
    Will wait up to 10 minutes for the string server to come back online.
    
    Args:
        client_id: Unique ID for the string server client (for cache keying)
        sentence_text: String to encode
        client_encode_func_key: Key to retrieve the encode function (ignored, just for cache invalidation)
        
    Returns:
        list: Embedding vector as list of floats
    """
    global _STRING_SERVER_OUTAGE_NOTIFIED, _STRING_SERVER_RECOVERY_NOTIFIED
    
    # Get the string server client from the global registry
    client = _STRING_SERVER_CLIENTS.get(client_id)
    if client is None:
        raise RuntimeError(f"String server client {client_id} not found in registry")
    
    # Retry with exponential backoff for up to 10 minutes
    max_retry_time = 600.0  # 10 minutes
    base_delay = 1.0  # Start with 1 second
    max_delay = 30.0  # Cap at 30 seconds between retries
    
    attempt = 0
    retry_start = time.time()
    last_error = None
    
    while (time.time() - retry_start) < max_retry_time:
        try:
            # Try to encode via string server
            result = client.encode(sentence_text)
            
            # If we succeed and had previously notified about an outage, notify about recovery
            if _STRING_SERVER_OUTAGE_NOTIFIED and not _STRING_SERVER_RECOVERY_NOTIFIED:
                elapsed = time.time() - retry_start
                logger.info(f"✅ String server recovered after {elapsed:.1f}s")
                _send_slack_recovery_notification(elapsed)
                _STRING_SERVER_RECOVERY_NOTIFIED = True
                _STRING_SERVER_OUTAGE_NOTIFIED = False
            
            return result
            
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            
            # Check if it's a connection/timeout error (retriable)
            is_retriable = any(x in error_str for x in [
                'connection refused', 
                'connection error', 
                'timeout',
                'timed out',
                '503',
                'service unavailable',
                'max retries exceeded',
                'failed to establish'
            ])
            
            if not is_retriable:
                # Not a retriable error (e.g., bad data format) - fail immediately
                raise
            
            elapsed = time.time() - retry_start
            
            # Send Slack notification on first outage detection
            if not _STRING_SERVER_OUTAGE_NOTIFIED and attempt == 0:
                logger.error(f"🚨 String server outage detected: {error_str[:200]}")
                logger.error(f"   Will retry for up to 10 minutes...")
                _send_slack_outage_notification(error_str)
                _STRING_SERVER_OUTAGE_NOTIFIED = True
                _STRING_SERVER_RECOVERY_NOTIFIED = False
            
            # Check if we've exceeded max retry time
            if elapsed >= max_retry_time:
                logger.error(f"❌ String server failed after {elapsed:.1f}s (10 minute timeout): {error_str[:200]}")
                raise RuntimeError(
                    f"String server unavailable for {elapsed:.1f}s. "
                    f"Giving up after 10 minutes of retries. Last error: {error_str}"
                ) from last_error
            
            # Calculate exponential backoff delay (capped at max_delay)
            delay = min(base_delay * (1.5 ** attempt), max_delay)
            remaining = max_retry_time - elapsed
            
            # Log retry attempts periodically (every 5th attempt or every 60s)
            if attempt % 5 == 0 or attempt == 1 or elapsed % 60 < delay:
                logger.warning(
                    f"⚠️  String server retry attempt {attempt + 1} "
                    f"(elapsed: {elapsed:.1f}s, remaining: {remaining:.1f}s, "
                    f"next retry in {delay:.1f}s): {error_str[:100]}"
                )
            
            time.sleep(delay)
            attempt += 1


def _send_slack_outage_notification(error_str: str):
    """Send Slack notification about string server outage."""
    try:
        from slack import send_slack_message
        message = (
            "🚨 *String Server Outage Detected*\n"
            f"The string encoding server (taco.local:9000) is unreachable.\n"
            f"Error: `{error_str[:200]}`\n"
            f"Will retry for up to 10 minutes. Training is paused."
        )
        send_slack_message(message, throttle=False, skip_hostname_prefix=False)
    except Exception as e:
        logger.warning(f"Failed to send Slack notification: {e}")


def _send_slack_recovery_notification(downtime_seconds: float):
    """Send Slack notification about string server recovery."""
    try:
        from slack import send_slack_message
        message = (
            "✅ *String Server Recovered*\n"
            f"The string encoding server is back online after {downtime_seconds:.1f}s.\n"
            "Training will resume."
        )
        send_slack_message(message, throttle=False, skip_hostname_prefix=False)
    except Exception as e:
        logger.warning(f"Failed to send Slack notification: {e}")


# Global registry of string server clients (for module-level caching)
_STRING_SERVER_CLIENTS = {}
_NEXT_CLIENT_ID = [0]  # Use list for mutability


class SimpleStringCache:
    """
    Dead simple string cache:
    - @lru_cache for in-memory caching (131,072 entries)
    - String server for encoding with batch support
    - No SQLite, no shared memory, no files
    """
    def __init__(self, initial_values=None, debugName="simple_cache", string_columns=None, **kwargs):
        """
        Args:
            initial_values: Optional list of strings to pre-warm the cache
            debugName: Debug name for logging
            string_columns: Optional list of string column names (enables local cache lookup)
            **kwargs: Ignored (for compatibility with old StringCache interface)
        """
        self.debugName = debugName
        self._string_server_client = None
        self._client_id = None
        self._client_encode_func_key = None
        self._log_every_n_misses = 10000  # Log stats every 10,000 cache misses
        self._last_logged_misses = 0
        
        # Lazy initialization: Only initialize string server client if we have initial_values to pre-warm
        # Otherwise, initialize on first use (avoids initialization in DataLoader workers that may not need it)
        if initial_values and len(initial_values) > 0:
            self._ensure_string_client_initialized()
            logger.info(f"🔥 Pre-warming cache with {len(initial_values)} strings...")
            self._pre_warm_cache(initial_values, string_columns=string_columns)
    
    def _ensure_string_client_initialized(self):
        """Lazily initialize string server client on first use."""
        if self._string_server_client is not None:
            return  # Already initialized
        
        logger.info(f"SimpleStringCache ({self.debugName}): Initializing string server client...")
        from featrix.neural.string_codec import _init_string_server_client
        
        self._string_server_client = _init_string_server_client()
        if self._string_server_client is None:
            raise RuntimeError(
                "String server client not available. "
                "Set 'string_server_host' in config.json to 'taco', 'taco.local', or 'localhost'."
            )
        
        # Register client in global registry for module-level caching
        self._client_id = _NEXT_CLIENT_ID[0]
        _NEXT_CLIENT_ID[0] += 1
        _STRING_SERVER_CLIENTS[self._client_id] = self._string_server_client
        self._client_encode_func_key = id(self._string_server_client.encode)  # For cache invalidation
    
    def get_embedding_from_cache(self, sentence_text, add_if_missing=True, do_not_log_if_missing=False, batch_size=None):
        """
        Get embedding from cache (or encode via string server).
        
        Args:
            sentence_text: String to encode
            add_if_missing: Ignored (always encodes via server)
            do_not_log_if_missing: Ignored
            batch_size: Optional batch size for logging purposes
            
        Returns:
            torch.Tensor: Embedding vector (float32)
        """
        if sentence_text is None:
            sentence_text = ""
        if type(sentence_text) != str:
            sentence_text = str(sentence_text)
        
        sentence_text = sentence_text.strip()
        
        # Empty strings return None
        if not sentence_text:
            return None
        
        # Lazy initialization: Initialize string client on first use
        self._ensure_string_client_initialized()
        
        # Set batch_size context for logging (not part of cache key)
        old_batch_size = getattr(_cached_encode, '_current_batch_size', None)
        if batch_size is not None:
            _cached_encode._current_batch_size = batch_size
        
        try:
            # Encode via string server (using module-level cache)
            embedding_list = _cached_encode(self._client_id, sentence_text, self._client_encode_func_key)
            embedding = torch.tensor(embedding_list, dtype=torch.float32)
            
            # Periodic logging of cache stats
            info = _cached_encode.cache_info()  # pylint: disable=no-value-for-parameter
            if info.misses > 0 and (info.misses - self._last_logged_misses) >= self._log_every_n_misses:
                total = info.hits + info.misses
                hit_rate = info.hits / max(total, 1)
                logger.info(
                    f"📊 SimpleStringCache ({self.debugName}): "
                    f"{info.hits} hits, {info.misses} misses "
                    f"({hit_rate:.1%} hit rate), "
                    f"{info.currsize}/{info.maxsize} entries"
                )
                self._last_logged_misses = info.misses
            
            return embedding
        except Exception as e:
            logger.error(f"SimpleStringCache: Failed to encode '{sentence_text[:50]}...': {e}")
            return None
        finally:
            # Restore previous batch_size context
            if batch_size is not None:
                if old_batch_size is not None:
                    _cached_encode._current_batch_size = old_batch_size
                else:
                    if hasattr(_cached_encode, '_current_batch_size'):
                        delattr(_cached_encode, '_current_batch_size')
    
    def get_embeddings_batch(self, string_list):
        """
        Get embeddings for a batch of strings (much faster than one-at-a-time).
        Includes retry logic with up to 10 minutes wait for string server outages.
        
        Returns:
            List of torch.Tensor embeddings (or None for empty strings)
        """
        if not string_list:
            return []
        
        # Lazy initialization: Initialize string client on first use
        self._ensure_string_client_initialized()
        
        # Split into cached vs uncached
        results = [None] * len(string_list)
        uncached_indices = []
        uncached_strings = []
        
        for i, s in enumerate(string_list):
            if s is None or (isinstance(s, str) and not s.strip()):
                results[i] = None
                continue
            
            s_str = str(s).strip()
            # Check cache first (will be fast after @lru_cache warms up)
            # Note: We can't check cache without calling the method, so just collect uncached
            uncached_indices.append(i)
            uncached_strings.append(s_str)
        
        # Batch encode all uncached strings with retry logic
        if uncached_strings:
            max_retry_time = 600.0  # 10 minutes
            base_delay = 1.0
            max_delay = 30.0
            attempt = 0
            retry_start = time.time()
            last_error = None
            
            while (time.time() - retry_start) < max_retry_time:
                try:
                    embeddings = self._string_server_client.encode_batch(uncached_strings)
                    for idx, embedding_list in zip(uncached_indices, embeddings):
                        # Store in cache via get_embedding_from_cache (populates @lru_cache)
                        embedding = torch.tensor(embedding_list, dtype=torch.float32)
                        results[idx] = embedding
                    break  # Success - exit retry loop
                    
                except Exception as e:
                    last_error = e
                    error_str = str(e).lower()
                    
                    # Check if it's a connection/timeout error (retriable)
                    is_retriable = any(x in error_str for x in [
                        'connection refused', 
                        'connection error', 
                        'timeout',
                        'timed out',
                        '503',
                        'service unavailable',
                        'max retries exceeded',
                        'failed to establish'
                    ])
                    
                    if not is_retriable:
                        # Not retriable - fallback to one-at-a-time
                        logger.error(f"SimpleStringCache: Batch encoding failed with non-retriable error: {e}")
                        batch_size_for_logging = len(string_list)
                        for idx, s in zip(uncached_indices, uncached_strings):
                            results[idx] = self.get_embedding_from_cache(s, batch_size=batch_size_for_logging)
                        break
                    
                    elapsed = time.time() - retry_start
                    
                    # Check if we've exceeded max retry time
                    if elapsed >= max_retry_time:
                        logger.error(f"❌ Batch encoding failed after {elapsed:.1f}s (10 minute timeout): {error_str[:200]}")
                        # Fallback to one-at-a-time (which has its own retry logic)
                        logger.info(f"   Falling back to one-at-a-time encoding for {len(uncached_strings)} strings...")
                        batch_size_for_logging = len(string_list)
                        for idx, s in zip(uncached_indices, uncached_strings):
                            results[idx] = self.get_embedding_from_cache(s, batch_size=batch_size_for_logging)
                        break
                    
                    # Calculate exponential backoff delay (capped at max_delay)
                    delay = min(base_delay * (1.5 ** attempt), max_delay)
                    remaining = max_retry_time - elapsed
                    
                    # Log retry attempts periodically
                    if attempt % 5 == 0 or attempt == 1:
                        logger.warning(
                            f"⚠️  Batch encoding retry attempt {attempt + 1} "
                            f"(elapsed: {elapsed:.1f}s, remaining: {remaining:.1f}s, "
                            f"next retry in {delay:.1f}s): {error_str[:100]}"
                        )
                    
                    time.sleep(delay)
                    attempt += 1
        
        return results
    
    def _pre_warm_cache(self, string_list, string_columns=None):
        """
        Pre-warm the @lru_cache by encoding all strings via the string server.
        This populates the cache upfront to avoid cache misses during training.
        
        First tries to load from local string cache if string_columns are provided,
        then falls back to string server encoding for any remaining strings.
        
        Args:
            string_list: List of strings to pre-warm
            string_columns: Optional list of string column names (enables local cache lookup)
        """
        import time
        start_time = time.time()
        
        # Clean and deduplicate strings
        unique_strings = []
        seen = set()
        for s in string_list:
            if s is None:
                continue
            s_str = str(s).strip()
            if not s_str or s_str in seen:
                continue
            seen.add(s_str)
            unique_strings.append(s_str)
        
        if not unique_strings:
            logger.info(f"   No valid strings to pre-warm")
            return
        
        num_strings = len(unique_strings)
        logger.info(f"   Pre-warming {num_strings} unique strings (from {len(string_list)} total)...")
        
        # Try to warm up from local cache first if string_columns are provided
        if string_columns:
            try:
                from featrix.neural.local_string_cache import warm_up_simple_string_cache_from_local
                logger.info(f"🔍 Attempting to warm up from local string cache...")
                num_cached = warm_up_simple_string_cache_from_local(
                    self,
                    string_columns,
                    cache_dir=None  # Uses default {featrix_root}/strings_cache/
                )
                
                if num_cached > 0:
                    logger.info(f"✅ Loaded {num_cached} strings from local cache")
                    # Check which strings are now in cache by testing a sample
                    # We'll encode remaining strings via string server below
                    cache_info = _cached_encode.cache_info()  # pylint: disable=no-value-for-parameter
                    logger.info(f"   Cache now has {cache_info.currsize} entries")
            except Exception as e:
                logger.warning(f"⚠️  Failed to warm up from local cache: {e}")
                logger.info(f"   Falling back to string server encoding...")
        
        # For large datasets (>50k strings), use individual encoding to properly populate @lru_cache
        # This takes time upfront but saves massive network overhead during training
        if num_strings > 50000:
            logger.info(f"   Large dataset ({num_strings} strings) - pre-warming all via individual encoding...")
        
        try:
            # Encode each string via _cached_encode to populate the @lru_cache
            # The string server handles these quickly (2-3ms each based on logs)
            # and they'll all be cached for training
            # Note: strings already in cache from local cache will be hits, not misses
            cache_misses_before = _cached_encode.cache_info().misses  # pylint: disable=no-value-for-parameter
            cache_hits_before = _cached_encode.cache_info().hits  # pylint: disable=no-value-for-parameter
            
            # Progress logging for large datasets
            log_interval = max(1000, num_strings // 10)  # Log every 10% or 1000 strings, whichever is larger
            
            for i, s in enumerate(unique_strings, 1):
                # This will cache the result in @lru_cache (or use cached value if already loaded)
                _cached_encode(self._client_id, s, self._client_encode_func_key)
                
                # Progress logging for large datasets
                if num_strings > 10000 and i % log_interval == 0:
                    elapsed_so_far = time.time() - start_time
                    rate = i / max(elapsed_so_far, 0.001)
                    remaining = (num_strings - i) / max(rate, 1)
                    cache_info = _cached_encode.cache_info()  # pylint: disable=no-value-for-parameter
                    hits = cache_info.hits - cache_hits_before
                    misses = cache_info.misses - cache_misses_before
                    logger.info(f"   Progress: {i}/{num_strings} ({100*i//num_strings}%) - {rate:.0f} strings/sec - ETA: {remaining:.0f}s (cache: {hits} hits, {misses} misses)")
            
            elapsed = time.time() - start_time
            cache_misses_after = _cached_encode.cache_info().misses  # pylint: disable=no-value-for-parameter
            cache_hits_after = _cached_encode.cache_info().hits  # pylint: disable=no-value-for-parameter
            new_misses = cache_misses_after - cache_misses_before
            new_hits = cache_hits_after - cache_hits_before
            
            logger.info(f"✅ Pre-warmed {num_strings} strings in {elapsed:.1f}s ({num_strings/max(elapsed,0.001):.0f} strings/sec)")
            logger.info(f"   Cache populated: {new_misses} new entries from string server, {new_hits} hits from cache")
            
            # Log cache stats
            info = _cached_encode.cache_info()  # pylint: disable=no-value-for-parameter
            logger.info(f"📊 Cache stats: {info.currsize}/{info.maxsize} entries, {info.hits} hits, {info.misses} misses")
            
        except Exception as e:
            logger.error(f"⚠️  Pre-warming failed: {e}")
            logger.info(f"   Cache will warm up during normal usage")
    
    def run_batch(self, initial_values, string_columns=None):
        """Compatibility method for pre-warming"""
        if initial_values:
            self._pre_warm_cache(initial_values, string_columns=string_columns)
    
    def get_cache_stats(self):
        """Get cache hit/miss statistics from @lru_cache"""
        info = _cached_encode.cache_info()  # pylint: disable=no-value-for-parameter
        total = info.hits + info.misses
        hit_rate = info.hits / max(total, 1)
        return {
            'hits': info.hits,
            'misses': info.misses,
            'hit_rate': hit_rate,
            'current_size': info.currsize,
            'max_size': info.maxsize
        }
    
    def log_cache_stats(self):
        """Log current cache statistics"""
        stats = self.get_cache_stats()
        logger.info(
            f"📊 SimpleStringCache ({self.debugName}): "
            f"{stats['hits']} hits, {stats['misses']} misses "
            f"({stats['hit_rate']:.1%} hit rate), "
            f"{stats['current_size']}/{stats['max_size']} entries"
        )
    
    @property
    def filename(self):
        """Compatibility property - no file backing"""
        return None
