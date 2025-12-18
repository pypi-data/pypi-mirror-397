#!/usr/bin/env python3
"""
Test script to check EdgeTTS voice availability and parameters.
"""

import asyncio
import sys
import os

# Add the speakub module to path (portable relative path)
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


async def test_edge_tts():
    """Test EdgeTTS functionality."""
    try:
        import edge_tts

        print("Edge TTS available, testing...")

        # Test getting voices
        print("Getting available voices...")
        voices = await edge_tts.list_voices()
        zh_tw_voices = [v for v in voices if v.get('Locale') == 'zh-TW']

        print(f"Available zh-TW voices: {len(zh_tw_voices)}")
        for voice in zh_tw_voices:
            print(f"  - {voice.get('ShortName')}: {voice.get('FriendlyName')}")

        # Check if HsiaoChenNeural exists
        hsiao_chen = [
            v for v in zh_tw_voices if 'HsiaoChen' in v.get('ShortName', '')]
        if hsiao_chen:
            voice_name = hsiao_chen[0].get('ShortName')
            print(f"Using voice: {voice_name}")
        else:
            print("HsiaoChenNeural not found, using first available:")
            voice_name = zh_tw_voices[0].get(
                'ShortName') if zh_tw_voices else None
            if voice_name:
                print(f"  - {voice_name}")
            else:
                print("No zh-TW voices available!")
                return

        # Test synthesis
        print("Testing synthesis with parameters...")
        text = "測試"

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice_name,
            rate="+0%",
            pitch="+0Hz",
            volume="+0%"
        )

        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
                print(f"Received audio chunk: {len(chunk['data'])} bytes")

        print(f"Total audio data: {len(audio_data)} bytes")
        if len(audio_data) == 0:
            print("ERROR: No audio data received!")
        else:
            print("SUCCESS: Audio data received")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing Edge TTS...")
if __name__ == "__main__":
    print("Testing Edge TTS...")
    asyncio.run(test_edge_tts())
