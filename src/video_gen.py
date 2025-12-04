"""
Video Generator using MoviePy.
Creates video with anchor image, audio, and text overlays.
"""

from moviepy import AudioFileClip, ImageClip, ColorClip, TextClip, CompositeVideoClip, VideoFileClip
from PIL import Image, ImageDraw, ImageFont
import os

class VideoGenerator:
    def __init__(self, output_dir="output/videos", orientation="landscape"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set dimensions based on orientation
        if orientation == "portrait":
            self.width = 1080
            self.height = 1920
        else:  # landscape
            self.width = 1920
            self.height = 1080
        
        self.orientation = orientation

    def create_video(self, audio_path, anchor_image_path, headline_text, output_filename="news_video.mp4", subtitle_path=None):
        """
        Create a video with:
        - Anchor image as background
        - Audio narration
        - Subtitles (optional)
        """
        try:
            # Load audio
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # Create animated anchor by cycling through images
            # Detect if we have multiple images in assets folder
            import os
            import glob
            
            # Get all anchor images
            anchor_dir = os.path.dirname(anchor_image_path)
            anchor_images = sorted(glob.glob(os.path.join(anchor_dir, "anchor*.png")))
            
            if len(anchor_images) > 1:
                print(f"  Found {len(anchor_images)} anchor images - creating animated anchor")
                # Create animation by cycling through images
                anchor_clips = []
                frame_duration = 0.3  # Each image shows for 0.3 seconds
                
                # Load and resize all images
                resized_images = []
                for img_path in anchor_images:
                    img = ImageClip(img_path)
                    # Resize to fit 1920x1080 while maintaining aspect ratio
                    img = img.resized(height=self.height)
                    if img.w > self.width:
                        img = img.resized(width=self.width)
                    img = img.with_position("center")
                    resized_images.append(img)
                
                # Create cycling animation
                current_time = 0
                while current_time < duration:
                    for img in resized_images:
                        if current_time >= duration:
                            break
                        # Calculate how long this frame should show
                        remaining = duration - current_time
                        frame_dur = min(frame_duration, remaining)
                        
                        clip = img.with_duration(frame_dur).with_start(current_time)
                        anchor_clips.append(clip)
                        current_time += frame_dur
                
                print(f"  Created {len(anchor_clips)} animation frames")
                
            else:
                # Single image - use static anchor
                print("  Using static anchor image")
                anchor_img = ImageClip(anchor_image_path).with_duration(duration)
                anchor_img = anchor_img.resized(height=self.height)
                if anchor_img.w > self.width:
                    anchor_img = anchor_img.resized(width=self.width)
                anchor_img = anchor_img.with_position("center")
                anchor_clips = [anchor_img]
            
            
            # Create background
            background = ColorClip(size=(self.width, self.height), 
                                   color=(20, 30, 50), 
                                   duration=duration)
            
            # Composite video - background + animated anchor clips
            video = CompositeVideoClip([
                background,
                *anchor_clips  # Unpack all anchor animation frames
            ])
            
            # Add audio
            video = video.with_audio(audio)
            
            # Write output
            temp_output = os.path.join(self.output_dir, "temp_" + output_filename)
            print(f"  Writing intermediate video to {temp_output}...")
            video.write_videofile(
                temp_output, 
                fps=24, 
                codec='libx264',
                audio_codec='aac',
                threads=4,
                preset='ultrafast',
                # logger=None
            )
            
            # Cleanup MoviePy objects
            audio.close()
            video.close()
            
            final_output = os.path.join(self.output_dir, output_filename)
            
            # 4. Burn subtitles if provided
            if subtitle_path and os.path.exists(subtitle_path):
                print(f"  Burning subtitles from {subtitle_path}...")
                try:
                    from moviepy.video.tools.subtitles import SubtitlesClip
                    from moviepy.video.VideoClip import TextClip
                    
                    # Generator function for subtitles
                    # Use absolute font path for Windows compatibility
                    font_path = "C:/Windows/Fonts/arial.ttf"
                    
                    def make_textclip(txt):
                        return TextClip(
                            text=txt,
                            font=font_path,
                            font_size=50,
                            color='white',
                            stroke_color='black',
                            stroke_width=2,
                            method='caption',
                            size=(int(1920*0.8), None), # Wrap text
                            text_align='center'
                        )
                        
                    # Manual SRT parser to avoid MoviePy parsing issues
                    def parse_srt(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        subtitles = []
                        blocks = content.strip().split('\n\n')
                        
                        for block in blocks:
                            lines = block.strip().split('\n')
                            if len(lines) >= 3:
                                # Parse timestamp 00:00:00,000 --> 00:00:00,000
                                times = lines[1].split(' --> ')
                                if len(times) != 2:
                                    continue
                                    
                                start_str = times[0].replace(',', '.')
                                end_str = times[1].replace(',', '.')
                                
                                def to_seconds(t):
                                    parts = t.split(':')
                                    return int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
                                
                                start = to_seconds(start_str)
                                end = to_seconds(end_str)
                                
                                # Parse text (join remaining lines)
                                text = '\n'.join(lines[2:])
                                subtitles.append(((start, end), text))
                        return subtitles

                    # Parse subtitles
                    subs_list = parse_srt(subtitle_path)
                    print(f"  Parsed {len(subs_list)} subtitles")
                    
                    # Re-load the video from temp file for compositing
                    video_for_composite = VideoFileClip(temp_output)
                    video_duration = video_for_composite.duration
                    
                    # Create subtitles clip
                    subtitles = SubtitlesClip(subs_list, make_textclip=make_textclip)
                    subtitles = subtitles.with_duration(video_duration)
                    
                    # Composite video with subtitles
                    # Position subtitles at the bottom (10% from bottom)
                    final_video = CompositeVideoClip([
                        video_for_composite,
                        subtitles.with_position(('center', video_for_composite.h * 0.85))
                    ])
                    
                    # Set duration explicitly
                    final_video = final_video.with_duration(video_duration)
                    
                    # Write final video
                    final_video.write_videofile(
                        final_output,
                        fps=24,
                        codec='libx264',
                        audio_codec='aac',
                        threads=4,
                        preset='ultrafast',
                        # logger=None
                    )
                    
                    # Cleanup
                    video_for_composite.close()
                    subtitles.close()
                    final_video.close()
                    
                    # Remove temp file
                    if os.path.exists(temp_output):
                        os.remove(temp_output)
                        
                    return final_output
                    
                except Exception as e:
                    print(f"Error burning subtitles with MoviePy: {e}")
                    # Fallback: Rename temp to final
                    print("  Renaming temp file to final output (without subtitles)...")
                    if os.path.exists(final_output):
                        os.remove(final_output)
                    os.rename(temp_output, final_output)
                    return final_output
            else:
                # Rename temp to final
                if os.path.exists(final_output):
                    os.remove(final_output)
                os.rename(temp_output, final_output)
                return final_output
            
        except Exception as e:
            print(f"Error creating video: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    # Test - requires audio file and anchor image
    generator = VideoGenerator()
    print("Video generator ready.")
    print("Use create_video() method to generate videos.")
