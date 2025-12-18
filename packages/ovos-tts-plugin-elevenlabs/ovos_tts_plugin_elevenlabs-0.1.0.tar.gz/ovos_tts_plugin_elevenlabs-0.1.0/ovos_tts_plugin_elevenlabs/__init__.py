import logging

import requests
from ovos_plugin_manager.templates.tts import TTS

LOG = logging.getLogger(__name__)


class ElevenLabsTTSPlugin(TTS):
    """OVOS TTS plugin for ElevenLabs text-to-speech API."""

    API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

    def __init__(self, *args, **kwargs):
        LOG.info("ElevenLabsTTSPlugin: Initializing...")
        # ElevenLabs returns mp3 by default
        super().__init__(*args, **kwargs, audio_ext="mp3", ssml_tags=[])

        LOG.debug(f"ElevenLabsTTSPlugin: Config received: {self.config}")

        # Configuration options
        self.api_key = self.config.get("api_key")
        self.voice_id = self.config.get("voice_id", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel
        self.model_id = self.config.get("model_id", "eleven_monolingual_v1")
        self.stability = self.config.get("stability", 0.5)
        self.similarity_boost = self.config.get("similarity_boost", 0.5)
        self.style = self.config.get("style", 0.0)
        self.use_speaker_boost = self.config.get("use_speaker_boost", True)

        if not self.api_key:
            LOG.error("ElevenLabsTTSPlugin: No API key found in config!")
            raise ValueError("ElevenLabs API key is required. Set 'api_key' in config.")

        LOG.info(f"ElevenLabsTTSPlugin: Loaded successfully with voice_id={self.voice_id}")

    def get_tts(self, sentence, wav_file):
        """Generate TTS audio using ElevenLabs API.

        Args:
            sentence: Text to synthesize
            wav_file: Output file path (will be mp3 despite the name)

        Returns:
            Tuple of (audio_file_path, None)
        """
        url = f"{self.API_URL}/{self.voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        payload = {
            "text": sentence,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
                "style": self.style,
                "use_speaker_boost": self.use_speaker_boost
            }
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        with open(wav_file, "wb") as f:
            f.write(response.content)

        return wav_file, None

    @property
    def available_languages(self):
        """Return languages supported by ElevenLabs.

        ElevenLabs supports multiple languages depending on the model used.
        The multilingual models support many languages.
        """
        return {
            "en", "en-us", "en-gb",
            "de", "de-de",
            "es", "es-es",
            "fr", "fr-fr",
            "it", "it-it",
            "pt", "pt-br", "pt-pt",
            "pl", "pl-pl",
            "hi", "hi-in",
            "ja", "ja-jp",
            "ko", "ko-kr",
            "zh", "zh-cn",
            "nl", "nl-nl",
            "sv", "sv-se",
            "tr", "tr-tr",
            "ru", "ru-ru",
            "ar", "ar-sa",
            "cs", "cs-cz",
            "da", "da-dk",
            "fi", "fi-fi",
            "el", "el-gr",
            "he", "he-il",
            "hu", "hu-hu",
            "id", "id-id",
            "no", "no-no",
            "ro", "ro-ro",
            "sk", "sk-sk",
            "uk", "uk-ua",
            "vi", "vi-vn"
        }


# Configuration metadata for OVOS plugin manager
ElevenLabsTTSPluginConfig = {
    "en-us": [{
        "lang": "en-us",
        "display_name": "ElevenLabs TTS",
        "priority": 50,
        "offline": False,
        "api_key": "",  # Required
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel (default)
        "model_id": "eleven_monolingual_v1",
        "stability": 0.5,
        "similarity_boost": 0.5,
        "style": 0.0,
        "use_speaker_boost": True
    }]
}
