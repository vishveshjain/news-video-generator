import asyncio
import edge_tts

async def test_tts():
    text = "Hello world. This is a test."
    voice = "en-IN-NeerjaNeural"
    communicate = edge_tts.Communicate(text, voice)
    
    submaker = edge_tts.SubMaker()
    
    print(f"Testing voice: {voice}")
    async for chunk in communicate.stream():
        # print(f"Chunk type: {chunk['type']}")
        if chunk['type'] == 'WordBoundary' or chunk['type'] == 'SentenceBoundary':
            print(f"  Feeding {chunk['type']}")
            submaker.feed(chunk)
            
    print("Generated SRT:")
    print(submaker.get_srt())

if __name__ == "__main__":
    asyncio.run(test_tts())
