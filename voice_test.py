import edge_tts
import asyncio

async def test_voice():
    """Test if the voice works with a simple text"""
    text = "Hello, this is a test."
    voice = "en-IN-NeerjaNeural"
    
    print(f"Testing voice: {voice}")
    print(f"Text: {text}")
    
    communicate = edge_tts.Communicate(text, voice)
    
    try:
        with open("test_output.mp3", "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                    print("Received audio chunk!")
        print("SUCCESS: Audio generated")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def list_indian_voices():
    """List available Indian English voices"""
    print("\nChecking available Indian English voices...")
    voices = await edge_tts.list_voices()
    indian_voices = [v for v in voices if 'en-IN' in v['ShortName']]
    
    print(f"Found {len(indian_voices)} Indian voices:")
    for v in indian_voices:
        print(f"  - {v['ShortName']} ({v['Gender']})")
    
    return indian_voices

if __name__ == "__main__":
    print("=" * 60)
    print("Edge-TTS Voice Test")
    print("=" * 60)
    
    # Test current voice
    result = asyncio.run(test_voice())
    
    # List available voices
    asyncio.run(list_indian_voices())
    
    if not result:
        print("\nTrying with US English voice as fallback...")
        async def test_us_voice():
            communicate = edge_tts.Communicate("Hello, this is a test.", "en-US-AriaNeural")
            with open("test_output_us.mp3", "wb") as file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        file.write(chunk["data"])
            print("US voice worked!")
        
        asyncio.run(test_us_voice())
