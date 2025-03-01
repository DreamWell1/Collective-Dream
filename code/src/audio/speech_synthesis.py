#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Speech synthesis module with multiple fallbacks.
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
import subprocess
import wave
import array
import math
import random

# Configure logging
logger = logging.getLogger(__name__)

def generate_speech(text, output_path=None, language="en", slow=False):
    """
    Generate speech from text with multiple fallback options.
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file (if None, a temp file is created)
        language: Language code (default: "en")
        slow: Whether to generate slower speech
        
    Returns:
        Path to the generated audio file
    """
    # Create temp file if no output path provided
    if output_path is None:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            output_path = temp_file.name
    
    success = False
    
    # Try using gtts
    try:
        import gtts
        logger.info("Trying Google TTS...")
        tts = gtts.gTTS(text=text, lang=language, slow=slow)
        tts.save(output_path)
        logger.info(f"Successfully generated speech with Google TTS: {output_path}")
        success = True
    except ImportError:
        logger.warning("gtts not installed. Install with: pip install gtts")
        success = False
    except Exception as e:
        logger.warning(f"Google TTS failed: {str(e)}")
        success = False
    
    # If gtts failed, try pyttsx3
    if not success:
        try:
            import pyttsx3
            logger.info("Trying pyttsx3...")
            
            # Create a WAV file first
            wav_path = output_path.replace(".mp3", ".wav")
            
            engine = pyttsx3.init()
            engine.save_to_file(text, wav_path)
            engine.runAndWait()
            
            # Convert WAV to MP3 if possible
            try:
                from pydub import AudioSegment
                AudioSegment.from_wav(wav_path).export(output_path, format="mp3")
                os.remove(wav_path)  # Clean up WAV file
            except ImportError:
                # If pydub isn't available, just use the WAV file
                output_path = wav_path
            
            logger.info(f"Successfully generated speech with pyttsx3: {output_path}")
            success = True
        except ImportError:
            logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")
            success = False
        except Exception as e:
            logger.warning(f"pyttsx3 TTS failed: {str(e)}")
            success = False
    
    # If both failed, create a simple beep sound as last resort
    if not success:
        logger.warning("All TTS methods failed. Creating emergency beep sound.")
        output_path = create_beep_sound(output_path, text)
        success = True if output_path else False
    
    # Return the output path if successful, None otherwise
    if success:
        return output_path
    else:
        logger.error("All speech generation methods failed")
        return None

def create_beep_sound(output_path, text=None, duration=3):
    """Create a simple beep sound as an absolute last resort."""
    try:
        # Convert to .wav if the output is .mp3
        wav_path = output_path
        if output_path.lower().endswith(".mp3"):
            wav_path = output_path.replace(".mp3", ".wav")
        
        # Create a simple beep sound
        sample_rate = 44100
        
        # Calculate number of frames
        n_frames = int(duration * sample_rate)
        
        # Create the audio data array
        data = array.array('h')
        
        # Create a beep pattern based on text length if text is provided
        if text:
            # Create a unique pattern based on text to make it identifiable
            pattern = []
            text_hash = sum(ord(c) for c in text) % 100
            
            # Create a pattern of beeps
            for i in range(min(10, len(text) // 5 + 1)):
                freq = 440 + (text_hash + i * 50) % 400  # Frequency between 440-840 Hz
                length = 0.2 + (ord(text[i * 5 % len(text)]) % 10) / 30  # Length between 0.2-0.5s
                pattern.append((freq, length))
        else:
            # Default pattern if no text
            pattern = [(440, 0.3), (0, 0.1), (660, 0.3), (0, 0.1), (880, 0.3)]
        
        # Generate the audio data
        for freq, length in pattern:
            frames = int(length * sample_rate)
            
            if freq > 0:
                # Generate sine wave
                for i in range(frames):
                    value = int(32767 * math.sin(2 * math.pi * freq * i / sample_rate))
                    data.append(value)
            else:
                # Silence
                data.extend([0] * frames)
        
        # Write to a WAV file
        with wave.open(wav_path, 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            f.writeframes(data.tobytes())
        
        logger.info(f"Created emergency audio signal: {wav_path}")
        
        # Return the WAV path
        return wav_path
    except Exception as e:
        logger.error(f"Failed to create emergency audio: {str(e)}")
        return None

def install_missing_packages():
    """Install missing packages needed for TTS."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gtts", "pyttsx3", "pydub"])
        logger.info("Successfully installed required packages")
        return True
    except Exception as e:
        logger.error(f"Failed to install packages: {str(e)}")
        return False

# Test function
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Check if testing automatic package installation
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        print("Attempting to install required packages...")
        if install_missing_packages():
            print("Packages installed successfully")
        else:
            print("Failed to install packages. Please install manually:")
            print("pip install gtts pyttsx3 pydub")
        sys.exit(0)
    
    # Get text from command line arguments or use default
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "Hello, this is a test of the speech synthesis system."
    
    print(f"Generating speech for: '{text}'")
    output_path = generate_speech(text)
    
    if output_path:
        print(f"Speech generated successfully: {output_path}")
        
        # Try to play the audio if possible
        try:
            if sys.platform == "win32":
                os.system(f'start {output_path}')
            elif sys.platform == "darwin":  # macOS
                os.system(f'afplay {output_path}')
            else:  # Linux
                os.system(f'xdg-open {output_path}')
        except Exception as e:
            print(f"Could not play audio: {e}")
    else:
        print("Failed to generate speech")