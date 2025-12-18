# OVOS TTS Plugin - ElevenLabs

An OVOS TTS plugin that uses [ElevenLabs](https://elevenlabs.io/) as the text-to-speech backend.

## Installation

```bash
pip install ovos-tts-plugin-elevenlabs
```

## Configuration

Add the following to your OVOS configuration (`~/.config/mycroft/mycroft.conf`):

```json
{
  "tts": {
    "module": "ovos-tts-plugin-elevenlabs",
    "ovos-tts-plugin-elevenlabs": {
      "api_key": "your-elevenlabs-api-key",
      "voice_id": "21m00Tcm4TlvDq8ikWAM"
    }
  }
}
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | string | **required** | Your ElevenLabs API key |
| `voice_id` | string | `21m00Tcm4TlvDq8ikWAM` | The voice ID to use (default is "Rachel") |
| `model_id` | string | `eleven_monolingual_v1` | The model to use for synthesis |
| `stability` | float | `0.5` | Voice stability (0.0 to 1.0) |
| `similarity_boost` | float | `0.5` | Similarity boost (0.0 to 1.0) |
| `style` | float | `0.0` | Style exaggeration (0.0 to 1.0) |
| `use_speaker_boost` | bool | `true` | Enable speaker boost |

## Getting an API Key

1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Navigate to your profile settings
3. Copy your API key

## Finding Voice IDs

You can find available voices and their IDs through:
- The ElevenLabs web interface
- The ElevenLabs API: `GET https://api.elevenlabs.io/v1/voices`

Some popular default voice IDs:
- `21m00Tcm4TlvDq8ikWAM` - Rachel (default)
- `AZnzlk1XvdvUeBnXmlld` - Domi
- `EXAVITQu4vr4xnSDxMaL` - Bella
- `ErXwobaYiN019PkySvjV` - Antoni
- `MF3mGyEYCl7XYWbV9V6O` - Elli

## Models

Available models:
- `eleven_monolingual_v1` - English only, fast
- `eleven_multilingual_v1` - Multiple languages
- `eleven_multilingual_v2` - Improved multilingual support
- `eleven_turbo_v2` - Fast, lower latency
