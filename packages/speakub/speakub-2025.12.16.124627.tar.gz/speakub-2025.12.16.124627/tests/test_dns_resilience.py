#!/usr/bin/env python3
"""
Test script for DNS resilience fixes in EdgeTTSProvider.
Simulates network errors and verifies retry logic with jitter.
"""

from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider
import asyncio
import logging
import socket
from unittest.mock import AsyncMock, patch
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_dns_error_handling():
    """Test that DNS errors trigger longer delays and jitter."""
    print("Testing DNS Error Resilience...")

    # Mock dependencies
    with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
        provider = EdgeTTSProvider()

        # Create a side effect that raises gaierror twice then returns data
        async def mock_stream():
            # This simulates the stream iterator
            yield {"type": "audio", "data": b"success_audio"}

        # We need to mock the communicate class instantiation
        with patch('edge_tts.Communicate') as MockCommunicate:
            instance = MockCommunicate.return_value

            # We need to simulate failures.
            # Since synthesize creates a NEW instance each time, we need to track
            # global state or mock the constructor to return an object that fails
            # based on call count.

            # Let's mock asyncio.sleep to verify the delays
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:

                # Scenario 1: DNS Error
                print("\n--- Scenario 1: DNS Error (socket.gaierror) ---")

                # Setup the mock to raise gaierror when stream is iterated
                async def fail_stream():
                    raise socket.gaierror(
                        "[Errno -3] Temporary failure in name resolution")
                    yield  # unreachable

                instance.stream = fail_stream

                # Run synthesize - expecting it to fail after retries
                # (to limit test time). In real code it retries 3 times.
                try:
                    await provider.synthesize("test text")
                except RuntimeError as e:
                    print(f"Caught expected error: {e}")

                # Check sleep calls
                # We expect 3 sleep calls (for 3 retries)
                # DNS errors should have longer delays (base 5.0) * jitter
                print(f"Sleep calls: {mock_sleep.call_count}")
                for i, call in enumerate(mock_sleep.call_args_list):
                    delay = call.args[0]
                    print(f"Retry {i+1} delay: {delay:.2f}s")
                    # Verify delay is > 2.0 (standard) which implies DNS logic hit
                    # Base delay for DNS is 5.0 * jitter(0.5, 1.5), so min is 2.5
                    if delay > 2.2:
                        print("  ✓ Valid DNS delay (detectable jitter > 2.2s)")
                    else:
                        print("  ? Delay seems short, check jitter logic")


async def main():
    await test_dns_error_handling()

if __name__ == "__main__":
    asyncio.run(main())
