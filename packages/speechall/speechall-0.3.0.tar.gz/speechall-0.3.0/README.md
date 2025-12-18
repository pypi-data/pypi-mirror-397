# Speechall Python SDK

Python SDK for the [Speechall API](https://speechall.com) - A powerful speech-to-text transcription service supporting multiple AI models and providers.

[![PyPI version](https://badge.fury.io/py/speechall.svg)](https://badge.fury.io/py/speechall)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features

- **Multiple AI Models**: Access various speech-to-text models from different providers (OpenAI Whisper, and more)
- **Flexible Input**: Transcribe local audio files or remote URLs
- **Rich Output Formats**: Get results in text, JSON, SRT, or VTT formats
- **Speaker Diarization**: Identify and separate different speakers in audio
- **Custom Vocabulary**: Improve accuracy with domain-specific terms
- **Replacement Rules**: Apply custom text transformations to transcriptions
- **Language Support**: Auto-detect languages or specify from a wide range of supported languages
- **Async Support**: Built with async/await support using httpx

## Installation

```bash
pip install speechall
```

## Quick Start

### Basic Transcription

```python
import os
from speechall import SpeechallApi

# Initialize the client
client = SpeechallApi(token=os.getenv("SPEECHALL_API_TOKEN"))

# Transcribe a local audio file
with open("audio.mp3", "rb") as audio_file:
    audio_data = audio_file.read()

response = client.speech_to_text.transcribe(
    model="openai.whisper-1",
    request=audio_data,
    language="en",
    output_format="json",
    punctuation=True
)

print(response.text)
```

### Transcribe Remote Audio

```python
from speechall import SpeechallApi

client = SpeechallApi(token=os.getenv("SPEECHALL_API_TOKEN"))

response = client.speech_to_text.transcribe_remote(
    file_url="https://example.com/audio.mp3",
    model="openai.whisper-1",
    language="auto",  # Auto-detect language
    output_format="json"
)

print(response.text)
```

## Advanced Features

### Speaker Diarization

Identify different speakers in your audio:

```python
response = client.speech_to_text.transcribe(
    model="openai.whisper-1",
    request=audio_data,
    language="en",
    output_format="json",
    diarization=True,
    speakers_expected=2
)

for segment in response.segments:
    print(f"[Speaker {segment.speaker}] {segment.text}")
```

### Custom Vocabulary

Improve accuracy for specific terms:

```python
response = client.speech_to_text.transcribe(
    model="openai.whisper-1",
    request=audio_data,
    language="en",
    output_format="json",
    custom_vocabulary=["Kubernetes", "API", "Docker", "microservices"]
)
```

### Replacement Rules

Apply custom text transformations:

```python
from speechall import ReplacementRule, ExactRule

replacement_rules = [
    ReplacementRule(
        rule=ExactRule(find="API", replace="Application Programming Interface")
    )
]

response = client.speech_to_text.transcribe_remote(
    file_url="https://example.com/audio.mp3",
    model="openai.whisper-1",
    language="en",
    output_format="json",
    replacement_ruleset=replacement_rules
)
```

### List Available Models

```python
models = client.speech_to_text.list_speech_to_text_models()

for model in models:
    print(f"{model.model_identifier}: {model.display_name}")
    print(f"  Provider: {model.provider}")
```

## Configuration

### Authentication

Get your API token from [speechall.com](https://speechall.com) and set it as an environment variable:

```bash
export SPEECHALL_API_TOKEN="your-token-here"
```

Or pass it directly when initializing the client:

```python
from speechall import SpeechallApi

client = SpeechallApi(token="your-token-here")
```

### Output Formats

- `text`: Plain text transcription
- `json`: JSON with detailed information (segments, timestamps, metadata)
- `json_text`: JSON with simplified text output
- `srt`: SubRip subtitle format
- `vtt`: WebVTT subtitle format

### Language Codes

Use ISO 639-1 language codes (e.g., `en`, `es`, `fr`, `de`) or `auto` for automatic detection.

## API Reference

### Client Classes

- **`SpeechallApi`**: Main client for the Speechall API
- **`AsyncSpeechallApi`**: Async client for the Speechall API

### Main Methods

#### `speech_to_text.transcribe()`

Transcribe a local audio file.

**Parameters:**
- `model` (str): Model identifier (e.g., "openai.whisper-1")
- `request` (bytes): Audio file content
- `language` (str): Language code or "auto"
- `output_format` (str): Output format (text, json, srt, vtt)
- `punctuation` (bool): Enable automatic punctuation
- `diarization` (bool): Enable speaker identification
- `speakers_expected` (int, optional): Expected number of speakers
- `custom_vocabulary` (list, optional): List of custom terms
- `initial_prompt` (str, optional): Context prompt for the model
- `temperature` (float, optional): Model temperature (0.0-1.0)

#### `speech_to_text.transcribe_remote()`

Transcribe audio from a URL.

**Parameters:** Same as `transcribe()` but with `file_url` instead of `request`

#### `speech_to_text.list_speech_to_text_models()`

List all available models.

## Examples

Check out the [examples](./examples) directory for more detailed usage examples:

- [transcribe_local_file.py](./examples/transcribe_local_file.py) - Transcribe local audio files
- [transcribe_remote_file.py](./examples/transcribe_remote_file.py) - Transcribe remote audio URLs

## Requirements

- Python 3.8+
- httpx >= 0.27.0
- pydantic >= 2.0.0
- typing-extensions >= 4.0.0

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy .
```

## Support

- Documentation: [docs.speechall.com](https://docs.speechall.com)
- GitHub: [github.com/speechall/speechall-python-sdk](https://github.com/speechall/speechall-python-sdk)
- Issues: [github.com/speechall/speechall-python-sdk/issues](https://github.com/speechall/speechall-python-sdk/issues)

## License

MIT License - see LICENSE file for details
