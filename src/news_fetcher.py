import feedparser
import time
from datetime import datetime, timedelta
import re

class NewsFetcher:
    def __init__(self):
        self.feeds = {
            "Times of India": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
            "NDTV": "https://feeds.feedburner.com/ndtvnews-top-stories",
            "The Hindu": "https://www.thehindu.com/news/national/feeder/default.rss",
            "Indian Express": "https://indianexpress.com/feed/",
            "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
            "CNN World": "http://rss.cnn.com/rss/edition_world.rss",
            "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
            # Add more as needed
        }

    def clean_html(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext.strip()

    def fetch_news(self, hours_back=24):
        news_items = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        for source, url in self.feeds.items():
            try:
                print(f"Fetching {source}...")
                feed = feedparser.parse(url)
                
                for entry in feed.entries:
                    # Parse published time
                    published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
                    if published_parsed:
                        published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
                        
                        if published_dt > cutoff_time:
                            summary = self.clean_html(entry.get("summary", ""))
                            title = entry.get("title", "")
                            
                            # Basic deduplication check (very simple)
                            if not any(item['title'] == title for item in news_items):
                                news_items.append({
                                    "source": source,
                                    "title": title,
                                    "summary": summary,
                                    "link": entry.get("link", ""),
                                    "published": published_dt.strftime("%Y-%m-%d %H:%M:%S")
                                })
            except Exception as e:
                print(f"Error fetching {source}: {e}")

        return news_items

if __name__ == "__main__":
    fetcher = NewsFetcher()
    news = fetcher.fetch_news(hours_back=12)
    print(f"Fetched {len(news)} news items.")
    for item in news[:5]:
        print(f"[{item['source']}] {item['title']}")
