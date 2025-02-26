#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Combines video, audio, and subtitles into final output.
"""

import os
import logging
import subprocess
import tempfile
import random
from datetime import datetime

logger = logging.getLogger(__name__)

def compose_final_video(video_files, audio_file, subtitle_file, output_path=None, resolution=(1920, 1080)):
    """
    Combine video, audio, and subtitles into final output video.
    
    Args:
        video_files (list): List of video file paths
        audio_file (str): Path to audio file
        subtitle_file (str): Path to subtitle file
        output_path (str, optional): Path to save final video
        resolution (tuple): Output video resolution (width, height)
    
    Returns:
        str: Path to final video
    """
    if not video_files:
        logger.error("No video files provided for composition")
        return None
    
    if not os.path.exists(audio_file):
        logger.error(f"Audio file not found: {audio_file}")
        return None
    
    if not os.path.exists(subtitle_file):
        logger.warning(f"Subtitle file not found: {subtitle_file}")
        subtitle_file = None
    
    if not output_path:
        output_dir = os.path.join('data', 'output')
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"final_video_{timestamp}.mp4")
    
    try:
        # Create temp directory for intermediate files
        temp_dir = tempfile.mkdtemp()
        
        # Step 1: Create concatenated video file
        concat_video_path = _concatenate_videos(video_files, temp_dir, resolution)
        if not concat_video_path:
            raise Exception("Failed to concatenate videos")
        
        # Step 2: Add audio to video
        video_with_audio = _add_audio_to_video(concat_video_path, audio_file, temp_dir)
        if not video_with_audio:
            raise Exception("Failed to add audio to video")
        
        # Step 3: Add subtitles if available
        if subtitle_file:
            final_video = _add_subtitles_to_video(video_with_audio, subtitle_file, output_path)
        else:
            # If no subtitles, just copy the video with audio
            final_video = output_path
            with open(video_with_audio, 'rb') as src, open(final_video, 'wb') as dst:
                dst.write(src.read())
        
        logger.info(f"Final video composition complete: {final_video}")
        return final_video
    
    except Exception as e:
        logger.error(f"Error composing final video: {e}")
        return None
    finally:
        # Clean up temporary files
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

def _concatenate_videos(video_files, temp_dir, resolution):
    """
    Concatenate multiple video files into one.
    
    Args:
        video_files (list): List of video file paths
        temp_dir (str): Temporary directory for processing
        resolution (tuple): Output video resolution (width, height)
    
    Returns:
        str: Path to concatenated video
    """
    if len(video_files) == 1:
        # If only one video, just resize it
        output_path = os.path.join(temp_dir, "concat_video.mp4")
        subprocess.run([
            'ffmpeg', '-y', '-i', video_files[0],
            '-vf', f'scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,pad={resolution[0]}:{resolution[1]}:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            output_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    
    # For multiple videos, create a concat file
    concat_file_path = os.path.join(temp_dir, "concat_list.txt")
    processed_videos = []
    
    try:
        # Process each video to consistent format and resolution
        for i, video_path in enumerate(video_files):
            processed_path = os.path.join(temp_dir, f"video_{i}.mp4")
            
            # Standardize video: resize, set framerate, etc.
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path,
                '-vf', f'scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,pad={resolution[0]}:{resolution[1]}:(ow-iw)/2:(oh-ih)/2',
                '-r', '30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                processed_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            processed_videos.append(processed_path)
        
        # Create concat file
        with open(concat_file_path, 'w') as f:
            for video in processed_videos:
                f.write(f"file '{video}'\n")
        
        # Concatenate videos
        output_path = os.path.join(temp_dir, "concat_video.mp4")
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_file_path, '-c', 'copy',
            output_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error concatenating videos: {e}")
        # If concat fails, return the first processed video
        return processed_videos[0] if processed_videos else None

def _add_audio_to_video(video_path, audio_path, temp_dir):
    """
    Add audio to video file.
    
    Args:
        video_path (str): Path to video file
        audio_path (str): Path to audio file
        temp_dir (str): Temporary directory for processing
    
    Returns:
        str: Path to video with audio
    """
    output_path = os.path.join(temp_dir, "video_with_audio.mp4")
    
    try:
        # Get video duration
        video_duration_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', video_path
        ]
        video_duration = float(subprocess.check_output(video_duration_cmd).decode('utf-8').strip())
        
        # Get audio duration
        audio_duration_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        audio_duration = float(subprocess.check_output(audio_duration_cmd).decode('utf-8').strip())
        
        # Choose appropriate method based on duration comparison
        if abs(video_duration - audio_duration) < 2.0:
            # Durations are close enough, simple merge
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path, '-i', audio_path,
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-shortest', output_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        elif video_duration > audio_duration:
            # Video is longer, loop audio or extend with silence
            temp_audio = os.path.join(temp_dir, "extended_audio.mp3")
            
            if audio_duration < video_duration / 2:
                # Loop audio if it's significantly shorter
                subprocess.run([
                    'ffmpeg', '-y', '-stream_loop', '-1', '-i', audio_path,
                    '-t', str(video_duration), '-c', 'copy', temp_audio
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                # Add silence to the end
                subprocess.run([
                    'ffmpeg', '-y', '-i', audio_path,
                    '-af', f'apad=pad_dur={video_duration-audio_duration}',
                    temp_audio
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Merge video with extended audio
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path, '-i', temp_audio,
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-shortest', output_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        else:
            # Audio is longer, speed up or trim video
            speed_ratio = audio_duration / video_duration
            
            if speed_ratio < 1.5:
                # Slow down video slightly
                subprocess.run([
                    'ffmpeg', '-y', '-i', video_path, '-i', audio_path,
                    '-filter_complex', f'[0:v]setpts={speed_ratio}*PTS[v]',
                    '-map', '[v]', '-map', '1:a', '-c:a', 'copy',
                    output_path
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                # Loop video content to match audio duration
                temp_video = os.path.join(temp_dir, "looped_video.mp4")
                
                # Calculate number of loops needed
                loops = int(audio_duration / video_duration) + 1
                
                # Create concat file for looping
                loop_file = os.path.join(temp_dir, "loop_list.txt")
                with open(loop_file, 'w') as f:
                    for _ in range(loops):
                        f.write(f"file '{video_path}'\n")
                
                # Create looped video
                subprocess.run([
                    'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                    '-i', loop_file, '-c', 'copy', temp_video
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Merge looped video with audio
                subprocess.run([
                    'ffmpeg', '-y', '-i', temp_video, '-i', audio_path,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-shortest', output_path
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding audio to video: {e}")
        return video_path  # Return original video on error

def _add_subtitles_to_video(video_path, subtitle_path, output_path):
    """
    Add subtitles to video file.
    
    Args:
        video_path (str): Path to video file
        subtitle_path (str): Path to subtitle file
        output_path (str): Path to save final video
    
    Returns:
        str: Path to video with subtitles
    """
    try:
        # Configure subtitle style
        subtitle_style = "FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,Bold=1,Italic=0,Alignment=2"
        
        # Add subtitles
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f"subtitles={subtitle_path}:force_style='{subtitle_style}'",
            '-c:a', 'copy', output_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding subtitles: {e}")
        
        # If adding subtitles fails, just copy the video
        try:
            with open(video_path, 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())
            return output_path
        except:
            return video_path

def add_transition_effects(video_path, output_path=None, effect_type="fade"):
    """
    Add transition effects between scenes in a video.
    
    Args:
        video_path (str): Path to video file
        output_path (str, optional): Path to save processed video
        effect_type (str): Type of transition effect
    
    Returns:
        str: Path to video with transitions
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return None
    
    if not output_path:
        output_dir = os.path.join('data', 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"transition_{os.path.basename(video_path)}")
    
    try:
        # Different transition effects
        if effect_type == "fade":
            # Add fade in/out transitions
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path,
                '-vf', 'fade=t=in:st=0:d=1,fade=t=out:st=9:d=1',
                '-c:a', 'copy', output_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        elif effect_type == "wipe":
            # Add wipe transition effect
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path,
                '-vf', 'geq=lum=\'p(X,Y)\':a=\'st(1,pow(min(W/W,H/H),2)*(X/W-T/3)*(X/W-T/3)+(Y/H-0.5)*(Y/H-0.5));if(ld(1)>0.1*(T-3)*(T-3)+0.01,255,0)\'',
                '-c:a', 'copy', output_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        else:
            # Default: simple copy
            with open(video_path, 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())
        
        logger.info(f"Added {effect_type} transitions to video, saved to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding transitions: {e}")
        return video_path  # Return original video on error

def add_watermark(video_path, watermark_text, output_path=None):
    """
    Add watermark text to video.
    
    Args:
        video_path (str): Path to video file
        watermark_text (str): Text to use as watermark
        output_path (str, optional): Path to save watermarked video
    
    Returns:
        str: Path to watermarked video
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return None
    
    if not output_path:
        output_dir = os.path.join('data', 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"watermarked_{os.path.basename(video_path)}")
    
    try:
        # Add watermark text
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f"drawtext=text='{watermark_text}':x=W-tw-10:y=H-th-10:fontsize=24:fontcolor=white@0.5:box=1:boxcolor=black@0.2",
            '-c:a', 'copy', output_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.info(f"Added watermark to video, saved to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding watermark: {e}")
        return video_path  # Return original video on error 