#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for iFlytek TTS API
Tests the WebSocket-based TTS service with the configured credentials
"""

import os
import sys
import time
import base64
import hashlib
import hmac
import json
from datetime import datetime
from urllib.parse import urlencode
import websocket
import threading
import ssl
import wave

# Import credentials from speech_synthesis_human.py
APP_ID = "0594314f"
API_KEY = "98cef15c6289d60dbe4185b909f6cfb9"
API_SECRET = "OTU1ODc4NjhkYTE1MzEyMmViNGQwY2Nm"
WS_URL = "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6"

# Set up logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
response_data = []
tts_complete = threading.Event()

def generate_signature(api_key, api_secret, host, path, date):
    """Generate authentication signature for the WebSocket connection"""
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    return authorization

def create_url():
    """Create WebSocket URL with authentication parameters"""
    url_parse = WS_URL.split("://")[1].split("/")
    host = url_parse[0]
    path = "/" + "/".join(url_parse[1:])
    
    # Create authentication parameters
    date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    authorization = generate_signature(API_KEY, API_SECRET, host, path, date)
    
    # Create full URL with parameters
    v = {
        "authorization": authorization,
        "date": date,
        "host": host
    }
    url = WS_URL + "?" + urlencode(v)
    return url

def on_message(ws, message):
    """Handle WebSocket message"""
    global response_data
    try:
        message = json.loads(message)
        header = message.get("header", {})
        status = header.get("status", 1)
        
        if status == 2:  # Final message
            logger.info("TTS process complete")
            tts_complete.set()
        
        payload = message.get("payload", {})
        audio = payload.get("audio", {})
        audio_data = audio.get("data")
        if audio_data:
            response_data.append(base64.b64decode(audio_data))
            logger.info(f"Received audio chunk: {len(response_data)} ({len(audio_data)} bytes)")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def on_error(ws, error):
    """Handle WebSocket error"""
    logger.error(f"WebSocket error: {error}")
    tts_complete.set()  # Signal to exit

def on_close(ws, close_status_code, close_msg):
    """Handle WebSocket close"""
    logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")

def on_open(ws):
    """Handle WebSocket open - send initial TTS request"""
    def run():
        logger.info("WebSocket connection established, sending TTS request")
        
        # TTS Request parameters
        tts_params = {
            "common": {
                "app_id": APP_ID
            },
            "business": {
                "aue": "raw",
                "vcn": "xiaofeng", # Voice name
                "speed": 50,       # Speed 0-100
                "volume": 50,      # Volume 0-100
                "pitch": 50,       # Pitch 0-100
                "tte": "UTF8"      # Text encoding
            },
            "data": {
                "status": 2,       # 2 for final data
                "text": base64.b64encode("这是一个智能语音合成的测试，如果能听到声音，表示接口工作正常。".encode("utf-8")).decode('utf-8')
            }
        }
        
        # Send request
        ws.send(json.dumps(tts_params))
        logger.info("TTS request sent, waiting for response")
    
    threading.Thread(target=run).start()

def test_tts(text=None, output_file="tts_test_output.wav"):
    """Test TTS functionality with the given text"""
    global response_data
    response_data = []
    tts_complete.clear()
    
    if text is None:
        text = "这是一个智能语音合成的测试，如果能听到声音，表示接口工作正常。"
    
    # Create WebSocket URL with authentication
    url = create_url()
    logger.info(f"Connecting to TTS service...")
    
    # Create WebSocket connection
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    
    # Start WebSocket connection in a separate thread
    ws_thread = threading.Thread(target=ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
    ws_thread.daemon = True
    ws_thread.start()
    
    # Wait for TTS to complete or timeout
    tts_complete.wait(timeout=30)
    ws.close()
    
    if not response_data:
        logger.error("No audio data received")
        return False
    
    # Save audio data to WAV file
    try:
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(16000)  # 16kHz
            wf.writeframes(b''.join(response_data))
        
        logger.info(f"Audio saved to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving audio: {e}")
        return False

if __name__ == "__main__":
    # Enable debug for websocket
    websocket.enableTrace(True)
    
    print("\n===== Testing iFlytek TTS API =====")
    print(f"APP_ID: {APP_ID}")
    print(f"API_KEY: {API_KEY[:5]}...{API_KEY[-4:]}")
    
    # Get custom text from command line if provided
    text = None
    if len(sys.argv) > 1:
        text = sys.argv[1]
        print(f"Using custom text: {text}")
    
    # Set output file
    output_file = os.path.join(os.path.dirname(__file__), "tts_test_output.wav")
    
    print("\nConnecting to iFlytek TTS service...")
    success = test_tts(text, output_file)
    
    if success:
        print(f"\n✅ Success! Audio file created at: {output_file}")
        
        # Try to play the audio
        try:
            import platform
            if platform.system() == 'Windows':
                os.system(f'start {output_file}')
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open {output_file}')
            else:  # Linux
                os.system(f'xdg-open {output_file}')
            print("Attempting to play the audio file...")
        except:
            print("Please open the audio file manually to listen to it.")
    else:
        print("\n❌ Failed to generate speech. Check the logs for details.")