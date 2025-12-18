#!/usr/bin/env python3
"""
Test script for punctuation content pause handling
Tests text processing and playback logic for content containing punctuation paragraphs
"""

import asyncio
import time
import threading
from typing import List, Tuple, Union

# Mock related modules


class MockPlaylistManager:
    """Mock playlist manager"""

    def __init__(self):
        self.playlist: List[Union[Tuple[str, int],
                                  Tuple[str, int, Union[bytes, str]]]] = []
        self.current_index = 0
        self.lock = threading.Lock()

    def add_item(self, text: str, line_num: int):
        """Add item to playlist"""
        self.playlist.append((text, line_num))

    def get_current_item(self):
        """Get current item"""
        if 0 <= self.current_index < len(self.playlist):
            return self.playlist[self.current_index]
        return None

    def update_item_at(self, index: int, item):
        """Update item at specified index"""
        if 0 <= index < len(self.playlist):
            self.playlist[index] = item

    def advance_index(self):
        """Advance to next item"""
        self.current_index += 1

    def is_exhausted(self):
        """Check if exhausted"""
        return self.current_index >= len(self.playlist)

    def get_playlist_length(self):
        """Get playlist length"""
        return len(self.playlist)


class MockTTSIntegration:
    """Mock TTS integration"""

    def __init__(self):
        self.playlist_manager = MockPlaylistManager()
        self.tts_lock = threading.Lock()

    def prepare_playlist(self, text_lines: List[str]):
        """Prepare playlist"""
        for i, line in enumerate(text_lines):
            self.playlist_manager.add_item(line.strip(), i)


class TestPunctuationPause:
    """Test punctuation pause handling"""

    def __init__(self):
        self.integration = MockTTSIntegration()
        self.test_results = []

    def log(self, message: str):
        """Record test log"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        print(f"[{timestamp}] {message}")
        self.test_results.append(f"[{timestamp}] {message}")

    async def simulate_punctuation_pause(self, text_content: str) -> float:
        """Simulate punctuation content pause handling"""
        from speakub.utils.text_utils import analyze_punctuation_content

        pause_type, pause_duration = analyze_punctuation_content(text_content)

        if pause_duration > 0:
            self.log(
                f"Insert pause: {pause_type}, duration: {pause_duration:.1f}s")
            # Actually perform the pause
            start_time = time.time()
            await asyncio.sleep(pause_duration)
            actual_duration = time.time() - start_time
            self.log(
                f"Pause completed, actual duration: {actual_duration:.1f}s")
            return actual_duration
        else:
            self.log("No pause needed")
            return 0.0

    def simulate_content_filtering(self, text_lines: List[str]):
        """Simulate content filtering process"""
        self.log("Starting content filtering test...")

        for i, line in enumerate(text_lines):
            from speakub.utils.text_utils import is_speakable_content

            speakable, reason = is_speakable_content(line)
            if not speakable:
                self.log(f"Line {i}: '{line}' -> not speakable ({reason})")
                # Simulate marking as CONTENT_FILTERED
                self.integration.playlist_manager.update_item_at(
                    i, (line, i, b"CONTENT_FILTERED")
                )
            else:
                self.log(f"Line {i}: '{line}' -> speakable ({reason})")

    def simulate_playback_sync(self):
        """Simulate playback process (sync version, closer to actual implementation)"""
        self.log("Starting playback simulation (sync version)...")

        while not self.integration.playlist_manager.is_exhausted():
            current_item = self.integration.playlist_manager.get_current_item()

            if not current_item:
                break

            if len(current_item) == 3:
                text, line_num, audio = current_item

                if audio == b"CONTENT_FILTERED":
                    self.log(
                        f"Playing line {line_num}: punctuation content '{text}'")
                    # Simulate sync pause handling in actual runner
                    pause_type, pause_duration = self.simulate_punctuation_pause_sync(
                        text)
                    self.log(
                        f"Pause completed, type: {pause_type}, duration: {pause_duration:.1f}s")
                else:
                    self.log(
                        f"Playing line {line_num}: normal content '{text}' (simulated)")
                    # Simulate normal playback time (assume 0.1s per character)
                    play_time = len(text) * 0.1
                    import time
                    time.sleep(play_time)  # Use sync sleep
                    self.log(
                        f"Normal content playback completed, duration: {play_time:.1f}s")
            else:
                text, line_num = current_item
                self.log(
                    f"Playing line {line_num}: unprocessed content '{text}' (simulated)")
                play_time = len(text) * 0.1
                import time
                time.sleep(play_time)  # Use sync sleep
                self.log(
                    f"Content playback completed, duration: {play_time:.1f}s")

            # Advance to next item
            self.integration.playlist_manager.advance_index()

        self.log("Playback simulation completed")

    def simulate_punctuation_pause_sync(self, text_content: str) -> tuple[str, float]:
        """Simulate punctuation content pause handling (sync version)"""
        from speakub.utils.text_utils import analyze_punctuation_content

        pause_type, pause_duration = analyze_punctuation_content(text_content)

        if pause_duration > 0:
            self.log(
                f"Preparing to insert pause: {pause_type}, duration: {pause_duration:.1f}s")
            # Use sync sleep to simulate actual runner behavior
            import time
            time.sleep(pause_duration)
            return pause_type, pause_duration
        else:
            self.log("No pause needed")
            return "none", 0.0

    def run_test(self):
        """Run complete test"""
        # Test text - simulating article with punctuation paragraphs
        test_text_lines = [
            "小雞雞這時候轉頭一看......",
            "!!???",
            "這時候小雞雞看到一隻大機機！！",
            "......",
            "他心裡想著：這是什麼情況？",
            "!!!",
            "最後小雞雞決定要面對現實。"
        ]

        self.log("=" * 60)
        self.log("Punctuation Content Pause Handling Test")
        self.log("=" * 60)
        self.log(f"Test text lines: {len(test_text_lines)}")
        for i, line in enumerate(test_text_lines):
            self.log(f"  Line {i}: '{line}'")
        self.log("")

        # Prepare playlist
        self.integration.prepare_playlist(test_text_lines)

        # Content filtering
        self.simulate_content_filtering(test_text_lines)
        self.log("")

        # Sync playback simulation (closer to actual implementation)
        self.simulate_playback_sync()

        # Summary
        self.log("")
        self.log("=" * 60)
        self.log("Test Summary")
        self.log("=" * 60)
        self.log(f"Total test items: {len(test_text_lines)}")
        filtered_count = sum(1 for item in self.integration.playlist_manager.playlist
                             if len(item) == 3 and item[2] == b"CONTENT_FILTERED")
        self.log(f"Filtered as punctuation content: {filtered_count}")
        self.log(f"Normal content: {len(test_text_lines) - filtered_count}")

        return self.test_results


def main():
    """Main function"""
    print("Punctuation Content Pause Handling Test Script")
    print("Test goal: Verify that punctuation paragraphs get 1.5s pause correctly")
    print("")

    tester = TestPunctuationPause()
    results = tester.run_test()

    print("\n" + "=" * 60)
    print("Test completed! Please check the output above to confirm:")
    print("1. Punctuation content is correctly identified and filtered")
    print("2. Punctuation content gets 1.5s fixed pause")
    print("3. Normal content plays normally")
    print("4. Overall playback rhythm matches original emotion")
    print("=" * 60)


if __name__ == "__main__":
    main()
