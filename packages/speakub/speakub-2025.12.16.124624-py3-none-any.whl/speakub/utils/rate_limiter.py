#!/usr/bin/env python3
"""
Rate Limiter - Request throttling protection for SpeakUB TTS operations.
Phase 2: Implement request throttling protection for TTS APIs
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket-based rate limiter for API request throttling.

    Implements token bucket algorithm to prevent overwhelming TTS APIs
    and reduce the risk of rate limit violations.
    """

    def __init__(self, requests_per_minute: int = 60, burst_limit: int = 10):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
            burst_limit: Maximum burst requests allowed
        """
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit

        # Convert to requests per second for token bucket
        self.requests_per_second = requests_per_minute / 60.0

        # Token bucket state
        self.tokens = burst_limit
        self.last_refill = time.time()
        self.max_tokens = burst_limit

        # Track recent requests for sliding window rate limiting
        self.request_times = deque(maxlen=requests_per_minute)

        # Rate limiting statistics
        self.total_requests = 0
        self.throttled_requests = 0
        self.average_wait_time = 0.0

        # Adaptive rate limiting
        self.consecutive_failures = 0
        self.backoff_multiplier = 1.0

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.requests_per_second

        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill = now

    def _calculate_wait_time(self) -> float:
        """Calculate wait time when rate limited."""
        # Simple backoff: wait until next token is available
        tokens_needed = 1.0
        if self.tokens < tokens_needed:
            tokens_deficit = tokens_needed - self.tokens
            wait_time = tokens_deficit / self.requests_per_second
            return wait_time

        return 0.0

    def wait_if_needed(self) -> float:
        """
        Wait if rate limited and return wait time.

        Returns:
            Wait time in seconds (0 if no wait needed)
        """
        wait_time = 0.0

        if self.is_rate_limited():
            wait_time = self._calculate_wait_time()

            if wait_time > 0:
                logger.debug(
                    f"Rate limiting: waiting {wait_time:.2f}s before next request"
                )
                time.sleep(wait_time)
                self.throttled_requests += 1

        return wait_time

    async def wait_if_needed_async(self) -> float:
        """
        Async version: Wait if rate limited and return wait time.

        Returns:
            Wait time in seconds (0 if no wait needed)
        """
        wait_time = 0.0

        if self.is_rate_limited():
            wait_time = self._calculate_wait_time()

            if wait_time > 0:
                logger.debug(
                    f"Async rate limiting: waiting {wait_time:.2f}s before next request"
                )
                await asyncio.sleep(wait_time)
                self.throttled_requests += 1

        return wait_time

    def is_rate_limited(self) -> bool:
        """
        Check if current request would be rate limited.

        Returns:
            True if rate limited, False otherwise
        """
        self._refill_tokens()

        # Check token bucket
        if self.tokens >= 1.0:
            return False

        # Also check sliding window (last minute)
        now = time.time()
        # Remove requests older than 1 minute
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()

        # Check if we've exceeded per-minute limit
        if len(self.request_times) >= self.requests_per_minute:
            return True

        return False

    def record_request(self) -> None:
        """Record a successful request."""
        now = time.time()
        self.request_times.append(now)
        self.total_requests += 1

        # Update tokens
        self._refill_tokens()
        if self.tokens >= 1.0:
            self.tokens -= 1.0

        # Reset consecutive failures on success
        self.consecutive_failures = 0
        self.backoff_multiplier = max(
            1.0, self.backoff_multiplier * 0.9
        )  # Reduce backoff

    def record_failure(self) -> None:
        """Record a failed request (rate limit or API error)."""
        self.consecutive_failures += 1

        # Increase backoff on consecutive failures
        if self.consecutive_failures >= 3:
            self.backoff_multiplier = min(5.0, self.backoff_multiplier * 1.2)
            logger.warning(
                f"Increasing rate limit backoff: {self.backoff_multiplier:.2f}x"
            )

    def get_stats(self) -> Dict:
        """
        Get rate limiter statistics.

        Returns:
            Dictionary with rate limiting stats
        """
        now = time.time()
        # Calculate requests in last minute
        recent_requests = sum(1 for t in self.request_times if now - t <= 60)

        return {
            "total_requests": self.total_requests,
            "throttled_requests": self.throttled_requests,
            "current_tokens": self.tokens,
            "max_tokens": self.max_tokens,
            "requests_per_second": self.requests_per_second,
            "requests_per_minute": self.requests_per_minute,
            "recent_requests_1min": recent_requests,
            "consecutive_failures": self.consecutive_failures,
            "backoff_multiplier": self.backoff_multiplier,
            "throttle_percentage": (
                self.throttled_requests / max(1, self.total_requests)
            )
            * 100,
        }


class ServiceRateLimiter:
    """
    Service-specific rate limiter with different limits per TTS provider.
    Phase 2: Request throttling protection for TTS APIs
    """

    def __init__(self):
        # Default rate limits (requests per minute)
        self.default_limits = {
            "edge-tts": (300, 20),  # 300 req/min, burst 20
            # 60 req/min, burst 5 (more conservative)
            "gtts": (60, 5),
            # 30 req/min, burst 3 (very conservative)
            "nanmai": (30, 3),
            "default": (60, 10),  # 60 req/min, burst 10
        }

        # Per-service rate limiters
        self.limiters: Dict[str, RateLimiter] = {}

    def get_limiter(self, service_name: str) -> RateLimiter:
        """
        Get or create rate limiter for a service.

        Args:
            service_name: Name of the TTS service

        Returns:
            RateLimiter instance for the service
        """
        if service_name not in self.limiters:
            req_per_min, burst = self.default_limits.get(
                service_name, self.default_limits["default"]
            )
            self.limiters[service_name] = RateLimiter(req_per_min, burst)
            logger.debug(
                f"Created rate limiter for {service_name}: {req_per_min} req/min"
            )

        return self.limiters[service_name]

    def wait_for_service(self, service_name: str) -> float:
        """
        Wait if needed for service rate limiting.

        Args:
            service_name: Name of the TTS service

        Returns:
            Wait time in seconds
        """
        limiter = self.get_limiter(service_name)
        wait_time = limiter.wait_if_needed()
        if wait_time > 0:
            logger.info(f"Rate limited {service_name}, waited {wait_time:.2f}s")
        return wait_time

    async def wait_for_service_async(self, service_name: str) -> float:
        """
        Async wait if needed for service rate limiting.

        Args:
            service_name: Name of the TTS service

        Returns:
            Wait time in seconds
        """
        limiter = self.get_limiter(service_name)
        wait_time = await limiter.wait_if_needed_async()
        if wait_time > 0:
            logger.info(f"Async rate limited {service_name}, waited {wait_time:.2f}s")
        return wait_time

    def record_service_request(self, service_name: str) -> None:
        """
        Record a successful request for a service.

        Args:
            service_name: Name of the TTS service
        """
        limiter = self.get_limiter(service_name)
        limiter.record_request()

    def record_service_failure(self, service_name: str) -> None:
        """
        Record a failed request for a service.

        Args:
            service_name: Name of the TTS service
        """
        limiter = self.get_limiter(service_name)
        limiter.record_failure()

    def get_service_stats(self, service_name: str = None) -> Dict:
        """
        Get rate limiting statistics.

        Args:
            service_name: Specific service name, or None for all

        Returns:
            Dictionary with rate limiting stats
        """
        if service_name:
            limiter = self.limiters.get(service_name)
            if limiter:
                return {service_name: limiter.get_stats()}
            return {}

        # All services
        return {name: limiter.get_stats() for name, limiter in self.limiters.items()}


# Global service rate limiter instance
_service_rate_limiter = ServiceRateLimiter()


def get_service_rate_limiter() -> ServiceRateLimiter:
    """Get the global service rate limiter instance."""
    return _service_rate_limiter


def rate_limited(service_name: str):
    """
    Decorator to apply rate limiting to TTS service calls.
    Phase 2: Request throttling protection decorator
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            limiter = get_service_rate_limiter()
            await limiter.wait_for_service_async(service_name)

            try:
                result = await func(*args, **kwargs)
                limiter.record_service_request(service_name)
                return result
            except Exception as e:
                limiter.record_service_failure(service_name)
                raise e

        def sync_wrapper(*args, **kwargs):
            limiter = get_service_rate_limiter()
            limiter.wait_for_service(service_name)

            try:
                result = func(*args, **kwargs)
                limiter.record_service_request(service_name)
                return result
            except Exception as e:
                limiter.record_service_failure(service_name)
                raise e

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
