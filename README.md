# News Video Generator

Automated 24/7 news video generator that fetches latest news from Indian and global sources, creates audio summaries, and generates video presentations.

## 📺 Demo Channel
Check out the generated videos on our YouTube channel: **[News Video Generator](https://www.youtube.com/@NewsVideoGeneratorr)**

## Features

- 📰 **Multi-Source News Aggregation**: Fetches from Times of India, NDTV, BBC, CNN, Al Jazeera, and more
- 🎙️ **High-Quality TTS**: Uses Edge TTS with Indian English female voice
- 🎬 **Automated Video Generation**: Creates professional news videos with anchor and overlays
- ⏰ **24/7 Operation**: Can run continuously with configurable intervals
- 🔄 **Auto-Update**: Refreshes content periodically

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### FFmpeg Requirement
MoviePy requires FFmpeg for video processing. Install it:

**Windows:**
- Download from https://ffmpeg.org/download.html
- Add to PATH

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Mac
brew install ffmpeg
```

## Project Structure

```
news-video-generator/
├── src/
│   ├── news_fetcher.py    # RSS feed aggregator
│   ├── summarizer.py      # Content processor
│   ├── audio_gen.py       # Text-to-speech engine
│   └── video_gen.py       # Video compositor
├── assets/
│   └── anchor.jpg         # Anchor image
├── output/
│   ├── audio/            # Generated audio files
│   └── videos/           # Generated video files
├── main.py               # Main orchestrator
└── requirements.txt
```

## Usage

### Single Generation (Test)
```bash
python main.py
```

### Continuous 24/7 Operation
Edit `main.py` and uncomment the last line:
```python
generator.run_continuous(interval_minutes=60)
```

Then run:
```bash
python main.py
```

## Configuration

### Change TTS Voice
In `src/audio_gen.py`, modify the voice:
```python
self.voice = "en-IN-NeerjaNeural"  # Female Indian English
# Other options:
# "en-IN-PrabhatNeural"  # Male Indian English
# "en-US-AriaNeural"     # Female US English
# "en-US-GuyNeural"      # Male US English
```

### Add News Sources
In `src/news_fetcher.py`, add to the `feeds` dictionary:
```python
self.feeds = {
    "Source Name": "RSS_FEED_URL",
    # ...
}
```

### Adjust Update Interval
In `main.py`:
```python
generator.run_continuous(interval_minutes=60)  # Change 60 to desired minutes
```

## Output

- **Audio**: `output/audio/news_YYYYMMDD_HHMMSS.mp3`
- **Video**: `output/videos/news_YYYYMMDD_HHMMSS.mp4`

## Customization

### Anchor Image
Replace `assets/anchor.jpg` with your preferred anchor image (recommended: 1920x1080 or portrait orientation)

### Video Style
Edit `src/video_gen.py` to customize:
- Background colors
- Text styles and positions
- Video dimensions
- Lower third design

## Requirements

- Python 3.8+
- FFmpeg
- Internet connection (for fetching news and TTS)

## License

Open source - feel free to modify and use as needed.

## Notes

- First run may take longer as it downloads TTS voices
- Video generation is CPU/GPU intensive
- Ensure stable internet for RSS feeds and TTS
- Default settings generate 4-5 minute videos with 10 news stories
