from moviepy import *

try:
    # Test TextClip with MoviePy 2.0 syntax
    # Create dummy SRT
    with open("test.srt", "w") as f:
        f.write("1\n00:00:00,000 --> 00:00:01,000\nHello\n\n2\n00:00:01,000 --> 00:00:02,000\nWorld\n\n")

    from moviepy.video.tools.subtitles import SubtitlesClip
    
    generator = lambda txt: TextClip(text=txt, font="C:/Windows/Fonts/arial.ttf", font_size=70, color='white', bg_color='black')
    
    # Test list input
    subs_list = [((0, 1), "Hello"), ((1, 2), "World")]
    subs = SubtitlesClip(subs_list, make_textclip=generator)
    
    # Create a simple color clip background
    color_clip = ColorClip(size=(640, 480), color=(0, 0, 255)).with_duration(2)
    
    final = CompositeVideoClip([color_clip, subs.with_position(('center', 'bottom'))])
    final.write_videofile("test_subs.mp4", fps=24)
    print("SubtitlesClip test passed!")
except Exception as e:
    print(f"TextClip test failed: {e}")
