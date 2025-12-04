import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.news_fetcher import NewsFetcher
from src.summarizer import Summarizer
from src.audio_gen import AudioGenerator
from src.video_gen import VideoGenerator
import time
from datetime import datetime
import json
import random

class NewsVideoGenerator:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.summarizer = Summarizer()
        self.audio_gen = AudioGenerator()
        self.video_gen = VideoGenerator()
        self.anchor_image = "assets/anchor.png"  # Default anchor image path
        self.history_file = "output/story_history.json"
        
        # Create history file if not exists
        os.makedirs("output", exist_ok=True)
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump({"used_titles": []}, f)
    
    def load_history(self):
        """Load used story titles from history file."""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                return set(data.get("used_titles", []))
        except:
            return set()
    
    def save_to_history(self, titles):
        """Save used story titles to history file."""
        try:
            history = self.load_history()
            history.update(titles)
            
            # Keep only last 100 titles to prevent file from growing too large
            history_list = list(history)[-100:]
            
            with open(self.history_file, 'w') as f:
                json.dump({"used_titles": history_list}, f, indent=2)
        except Exception as e:
            print(f"[WARN] Could not save history: {e}")

    def generate_news_video(self, hours_back=6, max_stories=15):
        """
        Main pipeline:
        1. Fetch latest news
        2. Summarize into script
        3. Generate audio
        4. Create video
        """
        try:
            print(f"\n{'='*60}")
            print(f"Starting News Video Generation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
            
            # Step 1: Fetch News
            print("[INFO] Fetching latest news...")
            news_items = self.news_fetcher.fetch_news(hours_back=hours_back)
            
            if not news_items:
                print("[WARN] No news items found.")
                return None
            
            print(f"[OK] Fetched {len(news_items)} news items.")
            
            # Filter out previously used stories
            used_titles = self.load_history()
            fresh_news = [item for item in news_items if item['title'] not in used_titles]
            
            if not fresh_news:
                print("[WARN] All stories have been used recently. Clearing history...")
                # Clear history if all stories have been used
                with open(self.history_file, 'w') as f:
                    json.dump({"used_titles": []}, f)
                fresh_news = news_items
            
            print(f"[INFO] {len(fresh_news)} fresh stories available (filtered {len(news_items) - len(fresh_news)} used stories)")
            
            # Shuffle to get random stories each time
            random.shuffle(fresh_news)
            
            # Step 2: Create Script
            print("\n[INFO] Creating news script...")
            script = self.summarizer.create_script(fresh_news, max_items=max_stories)
            print(f"[OK] Script created ({len(script)} characters)")
            
            # Step 3: Generate Audio
            print("\n[INFO] Generating audio...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_filename = f"news_{timestamp}.mp3"
            audio_path, subtitle_path = self.audio_gen.generate_audio(script, audio_filename)
            print(f"[OK] Audio saved: {audio_path}")
            print(f"[OK] Subtitles saved: {subtitle_path}")
            
            # Step 4: Create Video
            print("\n[INFO] Creating video...")
            video_filename = f"news_{timestamp}.mp4"
            
            if not os.path.exists(self.anchor_image):
                print(f"[WARN] Anchor image not found at {self.anchor_image}")
                print("   Please add an anchor image or use a placeholder.")
                print("   Skipping video generation for now.")
                return audio_path
            
            video_path = self.video_gen.create_video(
                audio_path=audio_path,
                anchor_image_path=self.anchor_image,
                headline_text="Latest News",
                output_filename=video_filename,
                subtitle_path=subtitle_path
            )
            print(f"[OK] Video saved: {video_path}")
            
            # Save used stories to history
            used_titles = [item['title'] for item in fresh_news[:max_stories]]
            self.save_to_history(used_titles)
            print(f"[INFO] Saved {len(used_titles)} story titles to history")
            
            # Generate YouTube Description
            try:
                with open("description_template.txt", "r", encoding="utf-8") as f:
                    template = f.read()
                
                headlines_list = ""
                for i, item in enumerate(fresh_news[:max_stories], 1):
                    headlines_list += f"{i}. {item['title']}\n"
                
                description = template.replace("{HEADLINES_LIST}", headlines_list)
                
                desc_filename = video_filename.replace(".mp4", ".txt")
                desc_path = os.path.join("output/videos", desc_filename)
                
                with open(desc_path, "w", encoding="utf-8") as f:
                    f.write(description)
                print(f"[OK] Description saved: {desc_path}")
            except Exception as e:
                print(f"[WARN] Could not generate description: {e}")

            print(f"\n{'='*60}")
            print("News video generated successfully!")
            print(f"{'='*60}\n")
            
            return video_path
            
        except Exception as e:
            print(f"[ERROR] Video generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_short_video(self, hours_back=6, max_stories=4):
        """
        Generate a 50-second portrait video for YouTube Shorts/Instagram Reels.
        Uses fewer stories and shorter summaries than the main video.
        """
        try:
            print(f"\n{'='*60}")
            print(f"Starting Short Video Generation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
            
            # Step 1: Fetch News (reuse same logic)
            print("[INFO] Fetching latest news for short...")
            news_items = self.news_fetcher.fetch_news(hours_back=hours_back)
            
            if not news_items:
                print("[WARN] No news items found.")
                return None
            
            print(f"[OK] Fetched {len(news_items)} news items.")
            
            # Filter and shuffle
            used_titles = self.load_history()
            fresh_news = [item for item in news_items if item['title'] not in used_titles]
            
            if not fresh_news:
                fresh_news = news_items
            
            random.shuffle(fresh_news)
            
            # Step 2: Create SHORT Script
            print("\n[INFO] Creating short news script...")
            script = self.summarizer.create_short_script(fresh_news, max_items=max_stories)
            print(f"[OK] Short script created ({len(script)} characters)")
            
            # Step 3: Generate Audio
            print("\n[INFO] Generating audio...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_filename = f"news_short_{timestamp}.mp3"
            audio_path, subtitle_path = self.audio_gen.generate_audio(script, audio_filename)
            print(f"[OK] Audio saved: {audio_path}")
            print(f"[OK] Subtitles saved: {subtitle_path}")
            
            # Step 4: Create PORTRAIT Video
            print("\n[INFO] Creating portrait video...")
            video_filename = f"news_short_{timestamp}.mp4"
            
            if not os.path.exists(self.anchor_image):
                print(f"[WARN] Anchor image not found")
                return audio_path
            
            # Use portrait video generator
            portrait_gen = VideoGenerator(output_dir="output/videos", orientation="portrait")
            
            video_path = portrait_gen.create_video(
                audio_path=audio_path,
                anchor_image_path=self.anchor_image,
                headline_text="Latest News",
                output_filename=video_filename,
                subtitle_path=subtitle_path
            )
            print(f"[OK] Short video saved: {video_path}")
            
            # Save to history
            used_titles = [item['title'] for item in fresh_news[:max_stories]]
            self.save_to_history(used_titles)
            print(f"[INFO] Saved {len(used_titles)} story titles to history")
            
            print(f"\n{'='*60}")
            print("Short video generated successfully!")
            print(f"{'='*60}\n")
            
            return video_path
            
        except Exception as e:
            print(f"[ERROR] Short video generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def run_continuous(self, interval_minutes=60):
        """
        Run the generator in a loop for 24/7 operation.
        """
        print("Starting 24/7 News Video Generator...")
        print(f"Update interval: {interval_minutes} minutes\n")
        
        while True:
            try:
                # Generate both landscape and portrait videos
                self.generate_news_video()
                self.generate_short_video()
                
                print(f"\nSleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                print("\n\nStopped by user.")
                break
            except Exception as e:
                print(f"[ERROR] Error in continuous loop: {e}")
                print("Waiting 5 minutes before retry...")
                time.sleep(300)

if __name__ == "__main__":
    generator = NewsVideoGenerator()
    
    # For testing, run once - generates both formats
    print("Running single generation test (both formats)...")
    generator.generate_news_video(hours_back=24, max_stories=15)
    generator.generate_short_video(hours_back=24, max_stories=4)
    
    # Uncomment below to run continuously
    # generator.run_continuous(interval_minutes=60)
