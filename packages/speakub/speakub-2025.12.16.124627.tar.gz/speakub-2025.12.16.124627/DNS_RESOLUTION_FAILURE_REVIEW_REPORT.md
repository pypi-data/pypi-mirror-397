# Edge-TTS DNS Resolution Failure Analysis Report (23:32 Incident)

## Executive Summary

This report analyzes a series of synthesis failure events that occurred at 23:32 on the evening of 2025-11-29. The incident began with a DNS resolution error, and due to the system's retry mechanism initiating retries for multiple batch items within a short time, it ultimately triggered a 401 Unauthorized error from the Edge TTS server side (identified by the system as rate limiting).

## Incident Analysis

### Error Sequence
1. **Initial Trigger Point (23:32:17)**: The system failed when attempting to connect to `api.msedgeservices.com`.
    * `socket.gaierror: [Errno -3] Temporary failure in name resolution`
    * This indicates that the DNS service could not resolve the domain name at that time, belonging to a temporary network failure.

2. **Domino Effect (23:32:17 - 23:32:18)**:
    * Due to being in `smooth` mode and performing batch preload, the system concurrently initiated multiple synthesis tasks (logs show indices 97, 94, 93, 95, 96, 92 failing almost simultaneously).
    * Each failed task triggered independent retry logic.
    * Although there was a simple `retry_delay`, since all tasks failed almost simultaneously and entered retry, they initiated requests again almost simultaneously after the delay (thundering herd effect).

3. **Server Blocking (23:32:49)**:
    * After multiple DNS failure retries, the network may have briefly recovered or requests were sent out.
    * Edge TTS server returned `401 Invalid response status`.
    * This is usually because too many requests from the same IP within a short time (retry storm), triggering Microsoft's anti-abuse mechanism.
    * The system correctly identified this as rate limiting and activated protection mechanism (reducing batch size to 5).

### Root Cause
1. **Lack of DNS-Specific Handling**: `socket.gaierror` was treated as general network error, retry interval (2 seconds) is too short for DNS failure recovery. DNS failures usually need several seconds or even tens of seconds to recover.
2. **Lack of Retry Jitter**: Multiple concurrent tasks use the same fixed retry interval, causing them to retry synchronously, forming traffic spikes.

## Current Implementation Review

### Retry Logic Analysis

```python
# Current retry implementation in EdgeTTSProvider.synthesize()
max_retries = 3
retry_delay = 2.0  # Start from 2 seconds

for attempt in range(max_retries + 1):
    try:
        # ... synthesis logic ...
    except (asyncio.TimeoutError, socket.gaierror) as e:
        if attempt < max_retries:
            logger.warning(f"Network error... will retry in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
```

**Advantages:**
- Captures DNS resolution errors (`socket.gaierror`)
- Implements exponential backoff
- Includes aiohttp-specific exception handling

**Disadvantages:**
- No DNS-specific recovery strategy
- Fixed retry delays do not consider DNS propagation time
- No circuit breaker for continuous failures
- Limited diagnostic information for DNS issues

### Network Error Handling Distribution

Network error handling is inconsistent across the codebase:

- **EdgeTTSProvider**: Comprehensive retry logic with 3 retries
- **TTS Runners**: Network errors cause immediate failure/interruption
- **Pre-synthesis Workers**: Log network errors but workers continue
- **Error Handler**: Classifies network errors but no specific recovery

## Identified Issues and Risks

### Critical Issues

1. **Ineffective DNS Retry Strategy**
   - DNS propagation may require 30-60 seconds globally
   - Current maximum retry time: approximately 14 seconds (2+4+8)
   - DNS failures persist beyond retry window

2. **Cascading Failure Risk**
   - No circuit breaker pattern implemented
   - Multiple consecutive items fail simultaneously
   - System continues attempting doomed operations

3. **Poor Error Diagnostic Capability**
   - Limited visibility into DNS resolution status
   - No network connectivity health checks
   - Generic error messages unhelpful for troubleshooting

### Performance and Reliability Risks

4. **Resource Waste**
   - Repeated failed DNS lookups consume system resources
   - Thread blocking during DNS resolution attempts
   - Unnecessary DNS infrastructure load

5. **User Experience Degradation**
   - Multiple synthesis failures within short time window
   - No graceful degradation during network issues
   - Sudden playback interruptions without recovery options

## Recommended Solutions

### Phase 1: Immediate Improvements (High Priority)

#### 1. DNS-Specific Error Handling

```python
async def _handle_dns_error(self, error: socket.gaierror, attempt: int) -> bool:
    """
    Handle DNS resolution errors with appropriate retry strategy.

    Returns True if should retry, False if should fail immediately.
    """
    # Check if this is a temporary DNS failure
    if "[Errno -3]" in str(error) or "Temporary failure in name resolution" in str(error):
        # Implement DNS-specific retry with longer delays
        dns_retry_delays = [5.0, 15.0, 30.0]  # DNS propagation time

        if attempt < len(dns_retry_delays):
            delay = dns_retry_delays[attempt]
            logger.warning(f"DNS resolution failed, will retry in {delay} seconds (attempt {attempt + 1})")
            await asyncio.sleep(delay)
            return True

    return False
```

#### 2. Circuit Breaker Pattern

```python
class NetworkCircuitBreaker:
    """Circuit breaker for network operations to prevent cascading failures."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenException()

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
```

#### 3. Network Health Monitoring

```python
class NetworkHealthMonitor:
    """Monitor network connectivity and DNS resolution health."""

    def __init__(self):
        self.dns_cache = {}
        self.last_dns_check = 0
        self.dns_check_interval = 30.0  # Check DNS every 30 seconds

    async def check_dns_resolution(self, hostname: str) -> bool:
        """Check if hostname DNS resolution is working."""
        current_time = time.time()

        # Use cached result if recent
        if hostname in self.dns_cache:
            cached_time, cached_result = self.dns_cache[hostname]
            if current_time - cached_time < self.dns_check_interval:
                return cached_result

        try:
            # Quick DNS resolution check
            await asyncio.get_event_loop().getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
            result = True
        except socket.gaierror:
            result = False

        # Cache result
        self.dns_cache[hostname] = (current_time, result)
        return result

    async def is_network_available(self) -> bool:
        """Check basic network connectivity."""
        try:
            # Try resolving a reliable hostname
            await self.check_dns_resolution("8.8.8.8")  # Google DNS
            return True
        except:
            return False
```

### Phase 2: Advanced Reliability Features (Medium Priority)

#### 4. Adaptive Retry Strategy

```python
class AdaptiveRetryStrategy:
    """Adaptive retry strategy based on error patterns and system state."""

    def __init__(self):
        self.error_history = []
        self.max_history_size = 10

    def calculate_retry_delay(self, error: Exception, attempt: int) -> float:
        """Calculate adaptive retry delay based on error type and history."""

        error_type = type(error).__name__

        # DNS errors need longer delays
        if "gaierror" in error_type:
            base_delays = [5.0, 15.0, 45.0, 90.0]
        elif "timeout" in error_type:
            base_delays = [2.0, 5.0, 10.0, 20.0]
        else:
            base_delays = [1.0, 2.0, 4.0, 8.0]

        # Adjust based on recent error patterns
        recent_errors = [e for e in self.error_history[-5:] if type(e).__name__ == error_type]
        error_frequency = len(recent_errors) / min(5, len(self.error_history))

        # Increase delay if errors are frequent
        if error_frequency > 0.6:  # 60% of recent errors are this type
            delay_multiplier = 2.0
        else:
            delay_multiplier = 1.0

        delay = base_delays[min(attempt, len(base_delays) - 1)] * delay_multiplier

        # Record this error
        self.error_history.append(error)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)

        return delay
```

#### 5. Fallback Mechanisms

```python
class TTSFallbackManager:
    """Manage fallback strategies when primary TTS fails."""

    def __init__(self):
        self.fallback_engines = ["gtts", "nanmai"]  # In order of preference
        self.network_fallback_enabled = True

    async def attempt_fallback_synthesis(self, text: str, primary_error: Exception) -> Optional[bytes]:
        """Attempt synthesis using fallback engines when network fails."""

        if not self.network_fallback_enabled:
            return None

        # Only use fallback for network-related errors
        if not self._is_network_error(primary_error):
            return None

        for engine_name in self.fallback_engines:
            try:
                # Attempt synthesis with fallback engine
                fallback_audio = await self._synthesize_with_fallback_engine(text, engine_name)
                if fallback_audio:
                    logger.info(f"Successfully used {engine_name} as fallback for network failure")
                    return fallback_audio
            except Exception as e:
                logger.debug(f"Fallback engine {engine_name} also failed: {e}")
                continue

        return None

    def _is_network_error(self, error: Exception) -> bool:
        """Check if error is network-related."""
        network_indicators = ["gaierror", "timeout", "connection", "network"]
        error_str = str(error).lower() + type(error).__name__.lower()

        return any(indicator in error_str for indicator in network_indicators)
```

### Phase 3: Monitoring and Observability (Low Priority)

#### 6. Enhanced Error Logging and Metrics

```python
class NetworkErrorMetrics:
    """Collect and report network error metrics."""

    def __init__(self):
        self.error_counts = {}
        self.response_times = []
        self.dns_resolution_times = []

    def record_dns_error(self, hostname: str, error: Exception, resolution_time: float):
        """Record DNS resolution error and timing."""
        key = f"dns_error_{hostname}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        self.dns_resolution_times.append(resolution_time)

        logger.warning(
            f"DNS resolution failed for {hostname}: {error} "
            f"(resolution time: {resolution_time:.3f}s, "
            f"total failures: {self.error_counts[key]})",
            extra={
                "component": "network_monitor",
                "hostname": hostname,
                "error_type": type(error).__name__,
                "resolution_time": resolution_time,
                "failure_count": self.error_counts[key]
            }
        )
```

## Implementation Recommendations

### Immediate Actions (Weeks 1-2)

1. **Implement DNS-specific retry logic** with longer delays
2. **Add circuit breaker pattern** to EdgeTTSProvider
3. **Enhance error logging** with more diagnostic information
4. **Add basic network health checks** before synthesis attempts

### Short-term Improvements (Month 1)

1. **Implement adaptive retry strategy** based on error patterns
2. **Add fallback engine support** for network failures
3. **Create network monitoring dashboard** for administrators
4. **Add configurable retry behavior** options

### Long-term Enhancements (Months 2-3)

1. **Implement comprehensive network recovery architecture**
2. **Add predictive failure detection** using machine learning
3. **Build offline TTS cache** for commonly used content
4. **Develop network-aware scheduling** for TTS operations

## Risk Mitigation

### Business Impact

- **Reduced TTS Failures**: DNS-specific handling should reduce failed syntheses by 60-80%
- **Improved User Experience**: Circuit breaker prevents cascading failures
- **Better Diagnostics**: Enhanced logging enables faster problem resolution
- **Operational Resilience**: Fallback mechanisms ensure service continuity

### Technical Risks

- **Performance Overhead**: Additional network checks may increase latency (mitigated by caching)
- **Increased Complexity**: More complex error handling requires additional testing
- **Resource Usage**: Circuit breaker state management adds minimal memory overhead

## Success Metrics

1. **DNS Failure Recovery Rate**: Target >90% recovery within 2 minutes
2. **Average Recovery Time**: Target <30 seconds for temporary network issues
3. **User-side Error Reduction**: Target 70% reduction in TTS synthesis failures
4. **System Stability**: Target <5% of sessions affected by network issues

## Conclusion

The DNS resolution failure incident highlighted the need for more sophisticated network error handling in the SpeakUB TTS system. The recommended improvements will significantly enhance system reliability and user experience while providing better diagnostics for network-related issues.

**Priority Classification:**
- **Phase 1 (Critical)**: Required for immediate stability
- **Phase 2 (Important)**: Significant reliability improvements
- **Phase 3 (Enhancement)**: Long-term operational excellence

**Estimated Implementation Effort:**
- Phase 1: 2-3 weeks development + 1 week testing
- Phase 2: 3-4 weeks development + 2 weeks testing
- Phase 3: 4-6 weeks development + 3 weeks testing

**Recommendation**: Begin Phase 1 immediately to address current DNS resolution issues, then proceed to Phase 2 for comprehensive network resilience.

## Solution

The following fixes have been implemented in `speakub/tts/edge_tts_provider.py`:

1. **Intelligent DNS Error Identification**:
    * Explicitly capture `socket.gaierror` and `aiohttp.ClientConnectorDNSError`.
    * Distinguish them from general network timeouts.

2. **Extended DNS Retry Delays**:
    * For DNS errors, base wait time increased from 2 seconds to 5 seconds.
    * This gives the OS DNS resolver more buffer time to recover.

3. **Introduction of Random Jitter**:
    * Add `random.uniform(0.5, 1.5)` random factor to all retry wait times.
    * For example, original 2-second wait now becomes between 1.0s ~ 3.0s.
    * This effectively distributes concurrent task retry timings and avoids thundering herd effect.

4. **Error Type Differentiation**:
    * Keep 401 errors as rate limiting trigger, as this is indeed a server-side service denial signal.
    * But significantly reduce the likelihood of triggering 401 through optimized client retry logic.

## Expected Effects
After the fix, when similar transient DNS failures occur:
* Tasks will retry in a distributed manner, not simultaneously hitting the server.
* Longer wait times reduce ineffective DNS queries.
* Significantly reduce the risk of server blocking due to network jitter.

---
*Report Generation Time*: 2025-11-29
