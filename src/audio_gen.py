import asyncio
import edge_tts
from gtts import gTTS
import os

class AudioGenerator:
    def __init__(self, output_dir="output/audio", voice="en-US-AriaNeural"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Available voices
        # Female Indian English: en-IN-NeerjaNeural
        # Male Indian English: en-IN-PrabhatNeural
        # Female US English: en-US-AriaNeural
        # Male US English: en-US-GuyNeural
        self.voice = "en-IN-NeerjaNeural"  # Female Indian English

    async def generate_audio_async(self, text, filename):
        """Generate audio file and subtitles from text using edge-tts."""
        filepath = os.path.join(self.output_dir, filename)
        sub_filename = os.path.splitext(filename)[0] + ".srt"
        sub_filepath = os.path.join(self.output_dir, sub_filename)
        
        communicate = edge_tts.Communicate(text, self.voice)
        submaker = edge_tts.SubMaker()
        
        with open(filepath, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary" or chunk["type"] == "SentenceBoundary":
                    submaker.feed(chunk)
                    # print(f"Received Boundary: {chunk}")
                    
        with open(sub_filepath, "w", encoding="utf-8") as file:
            file.write(submaker.get_srt())
            
        return filepath, sub_filepath
    
    def generate_audio_gtts(self, text, filename):
        """Generate audio using Google TTS (fallback method)."""
        filepath = os.path.join(self.output_dir, filename)
        sub_filename = os.path.splitext(filename)[0] + ".srt"
        sub_filepath = os.path.join(self.output_dir, sub_filename)
        
        print("[INFO] Using Google TTS as fallback...")
        
        # Generate audio with gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filepath)
        
        # Create basic SRT file (simple approach - one subtitle for entire text)
        # Note: gTTS doesn't provide word-level timing, so we create a simple subtitle
        with open(sub_filepath, "w", encoding="utf-8") as file:
            # Estimate duration based on text length (rough: 150 words per minute)
            words = len(text.split())
            duration_seconds = int((words / 150) * 60)
            
            file.write("1\n")
            file.write("00:00:00,000 --> ")
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60
            file.write(f"{hours:02d}:{minutes:02d}:{seconds:02d},000\n")
            file.write(text + "\n")
        
        return filepath, sub_filepath

    def generate_audio(self, text, filename="news_audio.mp3"):
        """Synchronous wrapper for audio generation with automatic fallback."""
        try:
            # Try edge-tts first
            return asyncio.run(self.generate_audio_async(text, filename))
        except edge_tts.exceptions.NoAudioReceived:
            print("[WARN] Edge-TTS failed (NoAudioReceived), falling back to Google TTS...")
            return self.generate_audio_gtts(text, filename)
        except Exception as e:
            print(f"[WARN] Edge-TTS failed with error: {e}, falling back to Google TTS...")
            return self.generate_audio_gtts(text, filename)

    def set_voice(self, voice_name):
        """Change the TTS voice."""
        self.voice = voice_name

if __name__ == "__main__":
    # Test
    generator = AudioGenerator()
    
    test_script = """Good day, here are today's top headlines.
    
Story 1. From BBC. Global Leaders Meet for Climate Summit. World leaders gathered in Geneva today to discuss urgent climate action.

Story 2. From Times of India. India Launches New Space Mission. ISRO successfully launched a satellite into orbit early this morning.

That's all for now. Stay tuned for more updates."""
    
    print("Generating audio...")
    audio_path = generator.generate_audio(test_script, "test_news.mp3")
    print(f"Audio saved to: {audio_path}")
