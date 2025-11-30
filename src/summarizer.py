"""
Content Summarizer module.
Converts news articles into detailed scripts for 4-5 minute videos.
"""

class Summarizer:
    def __init__(self):
        pass

    def create_script(self, news_items, max_items=15):
        """
        Create a news reading script from news items.
        Increased max_items to 15 and enhanced summaries for longer videos (4-5 mins target).
        """
        if not news_items:
            return ""
        
        script_parts = []
        
        # Intro
        script_parts.append("Good day, here are today's top headlines.")
        script_parts.append("")  # Pause
        
        # Process each news item
        for i, item in enumerate(news_items[:max_items], 1):
            script_parts.append(f"Story {i}.")
            script_parts.append(f"From {item['source']}.")
            script_parts.append(item['title'])
            
            # Enhanced summary - use more content for longer videos
            summary = item.get('summary', '')
            if summary:
                # Split into sentences and use first 3-4 sentences instead of 1-2
                sentences = summary.split('.')
                sentences = [s.strip() for s in sentences if s.strip()]
                
                # Use up to 4 sentences per story for more detail
                summary_text = '. '.join(sentences[:4])
                if summary_text and not summary_text.endswith('.'):
                    summary_text += '.'
                
                if summary_text:
                    script_parts.append(summary_text)
            
            script_parts.append("")  # Pause between stories
        
        # Outro
        script_parts.append("That's all for now.")
        script_parts.append("Stay tuned for more updates.")
        
        return "\n\n".join(script_parts)

if __name__ == "__main__":
    # Test
    summarizer = Summarizer()
    test_news = [
        {
            "source": "BBC",
            "title": "Global Leaders Meet for Climate Summit",
            "summary": "World leaders gathered in Geneva today to discuss urgent climate action. The summit aims to accelerate carbon reduction commitments. Over 100 nations are participating in the three-day event."
        },
        {
            "source": "Times of India",
            "title": "India Launches New Space Mission",
            "summary": "ISRO successfully launched a satellite into orbit early this morning. The mission is part of India's expanding space program."
        }
    ]
    
    script = summarizer.create_script(test_news)
    print(script)
