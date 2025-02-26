# Content Generation System

A comprehensive system for AI-driven content generation with hypnotic videos, synthesized speech, and dynamic composition.

## Overview

This content generation system integrates AI text generation with video processing, audio synthesis, and composition tools to create engaging multimedia content. The system can take user input in the form of labels or free-form prompts, generate appropriate content, and combine visual and audio elements into a final video output.

## Features

- **AI Content Generation**: Leverages advanced language models (Claude, GPT-4, DeepSeek) to generate text content
- **Video Processing**: Selects and processes videos from a categorized library based on semantic matching
- **Hypnotic Effects**: Applies visual effects to enhance engagement and create hypnotic experiences
- **Speech Synthesis**: Converts generated text to natural-sounding speech
- **Subtitle Generation**: Creates synchronized subtitles from text content
- **Final Composition**: Combines video, audio, and subtitles into cohesive output

## System Architecture

The system is organized into modular components:

```
content-generation-system/
├── .env                    <-- This is the file location
├── config/                 # Configuration files
│   ├── output/             # Generated outputs
│   ├── user_prompts/       # Saved user prompts
│   └── video_library/      # Video asset library
├── src/                    # Source code
│   ├── ai/                 # AI text generation
│   ├── audio/              # Audio processing
│   ├── composition/        # Final composition
│   ├── input/              # User input handling
│   ├── subtitles/          # Subtitle generation
│   └── video/              # Video processing
├── utils/                  # Utility modules
└── tests/                  # Test suite
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- FFmpeg (for video and audio processing)
- Required API keys for AI models

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/content-generation-system.git
   cd content-generation-system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys:
   - Create environment variables for API keys:
     ```
     BAIDU_API_KEY=your_baidu_api_key
     BAIDU_SECRET_KEY=your_baidu_secret_key
     ALIBABA_API_KEY=your_alibaba_api_key
     ZHIPU_API_KEY=your_zhipu_api_key
     MINIMAX_API_KEY=your_minimax_api_key
     ELEVENLABS_API_KEY=your_elevenlabs_api_key
     AZURE_SPEECH_KEY=your_azure_speech_key
     GOOGLE_TTS_KEY=your_google_tts_key
     ALIYUN_TTS_KEY=your_aliyun_tts_key
     ALIYUN_TTS_SECRET=your_aliyun_tts_secret
     XFYUN_APP_ID=your_xfyun_app_id
     XFYUN_API_KEY=your_xfyun_api_key
     XFYUN_API_SECRET=your_xfyun_api_secret
     DEEPSEEK_API_KEY=sk-9d20bc8f5ec0421296f993c68da45bcb
     DEVELOPMENT_MODE=false
     DOUBAO_API_KEY=3164430a-2fc8-4177-8f98-67dd0754c660
     ```

4. Initialize the database:
   ```bash
   python -c "from utils.db_connector import DatabaseConnector; DatabaseConnector().initialize_database()"
   ```

## Usage

### Running the System

```bash
python src/main.py
```

This will start the interactive prompt where you can:
1. Select from predefined labels to create content based on categories
2. Enter a custom prompt to generate content from scratch

### Example Workflow

1. User enters a prompt about meditation and mindfulness
2. System generates text content using the configured AI model
3. Speech is synthesized from the generated text
4. Videos are selected from the library based on semantic matching
5. Hypnotic effects are applied to the selected videos
6. Subtitles are generated from the text content
7. All elements are composed into a final video file

## Configuration

The system is highly configurable through JSON config files:

- `config/models.json`: AI model settings and parameters
- `config/video_categories.json`: Definitions of video categories
- `config/app_settings.json`: General application settings

## Extending the System

### Adding New Video Categories

1. Add a new entry to `config/video_categories.json`
2. Create a corresponding directory in `data/video_library/`
3. Populate with relevant video files

### Supporting New AI Models

1. Add model configuration to `config/models.json`
2. Implement a connector class in `src/ai/model_connector.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FFmpeg for video and audio processing capabilities
- [OpenAI](https://openai.com), [Anthropic](https://anthropic.com), and [DeepSeek](https://deepseek.com) for AI capabilities
- [ElevenLabs](https://elevenlabs.io) for text-to-speech technology 

# Creating a `.env` File for API Keys

Here's how to create the `.env` file for your API keys:

## 1. File Template

Create a new text file named `.env` (including the dot) in the project's root directory with the following content:

```
# Chinese AI Model API Keys
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
ALIBABA_API_KEY=your_alibaba_api_key
ZHIPU_API_KEY=your_zhipu_api_key
MINIMAX_API_KEY=your_minimax_api_key

# Speech Synthesis API Keys (Chinese options)
ALIYUN_TTS_KEY=your_aliyun_tts_key
ALIYUN_TTS_SECRET=your_aliyun_tts_secret
XFYUN_APP_ID=your_xfyun_app_id
XFYUN_API_KEY=your_xfyun_api_key
XFYUN_API_SECRET=your_xfyun_api_secret

# Optional: Development Mode (set to true to use mock responses)
DEVELOPMENT_MODE=false

# Essential API Keys
DEEPSEEK_API_KEY=sk-9d20bc8f5ec0421296f993c68da45bcb   # Your DeepSeek API key for text generation

# One of the following speech synthesis options (choose one):
ELEVENLABS_API_KEY=your_elevenlabs_api_key    # Best quality option (if you have it)
# OR
AZURE_SPEECH_KEY=your_azure_speech_key        # Microsoft Azure alternative
# OR
XFYUN_APP_ID=your_xfyun_app_id                # Chinese TTS option
XFYUN_API_KEY=your_xfyun_api_key
XFYUN_API_SECRET=your_xfyun_api_secret

# DouBao API Key for both text generation and speech synthesis
DOUBAO_API_KEY=3164430a-2fc8-4177-8f98-67dd0754c660
```

## 2. Getting API Keys

Here's how to obtain the necessary API keys:

### Essential Keys (at least one required)
- **Claude API Key**: Sign up at [Anthropic](https://www.anthropic.com/product)
- **GPT-4 API Key**: Sign up at [OpenAI](https://platform.openai.com/signup)
- **DeepSeek API Key**: Sign up at [DeepSeek](https://platform.deepseek.ai/)

### Speech Synthesis (at least one recommended)
- **ElevenLabs API Key**: Sign up at [ElevenLabs](https://beta.elevenlabs.io/)
- **Azure Speech Key**: Create a Speech resource in [Azure Portal](https://portal.azure.com/)
- **Google TTS Key**: Get API key from [Google Cloud Console](https://console.cloud.google.com/)

## 3. Development Mode

For testing without valid API keys, you can set:
```
DEVELOPMENT_MODE=true
```

This will use mock responses instead of making actual API calls.

## 4. Security Notes

- Never commit your `.env` file to version control
- Keep your API keys confidential
- Some services have usage limits and charges based on API usage

## 5. Verification

To verify your `.env` file is being loaded correctly, run:

```python:README.md
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CLAUDE_API_KEY loaded:', bool(os.getenv('CLAUDE_API_KEY')));"
```

This should output `CLAUDE_API_KEY loaded: True` if successful. 

# Important Security Note

I notice you've shared your actual DeepSeek API key in the message. For security reasons, you should never share API keys in public messages or commit them to public repositories.

## Updating Your `.env` File

Here's how to add your DeepSeek API key to your `.env` file safely:

```
# AI Model API Keys
DEEPSEEK_API_KEY=sk-9d20bc8f5ec0421296f993c68da45bcb
# Add other API keys as needed
```

## Security Recommendations

1. **Reset this key**: Since you've shared it in this conversation, you should consider generating a new API key from DeepSeek
2. **Keep keys private**: Never share API keys in messages, emails, or public repositories
3. **Use environment variables**: The `.env` file should be in your `.gitignore` to prevent accidental commits

## Using DeepSeek as Default

Your `config/models.json` file should have DeepSeek configured as follows:

```json:README.md
"default_model": "deepseek",
"models": {
    "deepseek": {
        "name": "DeepSeek Chat",
        "provider": "deepseek",
        "api_endpoint": "https://api.deepseek.com/v1/chat/completions",
        "model_id": "deepseek-chat",
        "max_tokens": 8192,
        "temperature": 0.7,
        "description": "DeepSeek's powerful bilingual model with strong Chinese capabilities"
    },
    // Other models...
}
```

This configuration will ensure that your system uses the DeepSeek model by default for content generation. 