import os
import sys
import numpy as np
import soundfile as sf

# ---------------------------------------------------------------------------
# Kitten TTS Configuration
# ---------------------------------------------------------------------------
KITTEN_MODELS = {
    "nano_v1": {
        "name": "KittenTTS Nano v1 (15M Params / 24MB - Ultra Fast)",
        "repo_id": "KittenML/kitten-tts-nano-0.1",
        "model_file": "kitten_tts_nano_v0_1.onnx",
        "voices_file": "voices.npz",
    },
    "nano_v2": {
        "name": "KittenTTS Nano v2 (15M Params / 24MB - Enhanced)",
        "repo_id": "KittenML/kitten-tts-nano-0.2",
        "model_file": "kitten_tts_nano_v0_2.onnx",
        "voices_file": "voices.npz",
    },
    "mini_v1": {
        "name": "KittenTTS Mini (80M Params / 166MB - High Quality)",
        "repo_id": "KittenML/kitten-tts-mini-0.1",
        "model_file": "kitten_tts_mini_v0_1.onnx",
        "voices_file": "voices.npz",
    },
}

# ---------------------------------------------------------------------------
# Kokoro TTS Configuration
# ---------------------------------------------------------------------------
KOKORO_VOICE_PRESETS = [
    {"id": "af_heart", "name": "American Female — Heart (Popular)", "category": "American Female"},
    {"id": "af_bella", "name": "American Female — Bella", "category": "American Female"},
    {"id": "af_sarah", "name": "American Female — Sarah", "category": "American Female"},
    {"id": "af_sky", "name": "American Female — Sky", "category": "American Female"},
    {"id": "af_nicole", "name": "American Female — Nicole", "category": "American Female"},
    {"id": "am_adam", "name": "American Male — Adam", "category": "American Male"},
    {"id": "am_echo", "name": "American Male — Echo", "category": "American Male"},
    {"id": "am_eric", "name": "American Male — Eric", "category": "American Male"},
    {"id": "am_michael", "name": "American Male — Michael", "category": "American Male"},
    {"id": "am_onyx", "name": "American Male — Onyx", "category": "American Male"},
    {"id": "bf_alice", "name": "British Female — Alice", "category": "British Female"},
    {"id": "bf_emma", "name": "British Female — Emma", "category": "British Female"},
    {"id": "bm_daniel", "name": "British Male — Daniel", "category": "British Male"},
    {"id": "bm_george", "name": "British Male — George", "category": "British Male"},
]

# ---------------------------------------------------------------------------
# Pocket TTS Configuration
# ---------------------------------------------------------------------------
POCKET_VOICE_PRESETS = [
    {"id": "alba", "name": "Alba (Female)"},
    {"id": "marius", "name": "Marius (Male)"},
    {"id": "jean", "name": "Jean (Male)"},
    {"id": "javert", "name": "Javert (Male)"},
    {"id": "cosette", "name": "Cosette (Female)"},
    {"id": "anna", "name": "Anna (Female)"},
    {"id": "vera", "name": "Vera (Female)"},
    {"id": "fantine", "name": "Fantine (Female)"},
    {"id": "charles", "name": "Charles (Male)"},
    {"id": "paul", "name": "Paul (Male)"},
    {"id": "eponine", "name": "Eponine (Female)"},
    {"id": "george", "name": "George (Male)"},
    {"id": "mary", "name": "Mary (Female)"},
    {"id": "jane", "name": "Jane (Female)"},
    {"id": "michael", "name": "Michael (Male)"},
    {"id": "eve", "name": "Eve (Female)"},
    {"id": "giovanni", "name": "Giovanni (Male)"},
    {"id": "lola", "name": "Lola (Female)"},
]

# Global cache for loaded model instances
_model_cache = {}


def get_kitten_model(submodel_key="nano_v1"):
    """Loads KittenTTS model instance and voice profiles."""
    cache_key = f"kitten_{submodel_key}"
    if cache_key in _model_cache:
        return _model_cache[cache_key]

    from huggingface_hub import hf_hub_download
    from kittentts import KittenTTS

    config = KITTEN_MODELS.get(submodel_key, KITTEN_MODELS["nano_v1"])
    model_path = hf_hub_download(repo_id=config["repo_id"], filename=config["model_file"])
    voices_path = hf_hub_download(repo_id=config["repo_id"], filename=config["voices_file"])

    model = KittenTTS(model_path)
    model._voices = np.load(voices_path)

    _model_cache[cache_key] = (model, list(model._voices.files))
    return _model_cache[cache_key]


def get_kokoro_model():
    """Loads Kokoro ONNX model instance."""
    if "kokoro" in _model_cache:
        return _model_cache["kokoro"]

    from kokoro_onnx import Kokoro

    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_file = os.path.join(base_dir, "kokoro-v1.0.onnx")
    voices_file = os.path.join(base_dir, "voices-v1.0.bin")

    if not os.path.isfile(model_file) or not os.path.isfile(voices_file):
        raise FileNotFoundError(
            f"Kokoro model files missing in {base_dir}. Expected kokoro-v1.0.onnx and voices-v1.0.bin."
        )

    kokoro = Kokoro(model_file, voices_file)
    _model_cache["kokoro"] = kokoro
    return kokoro


def get_pocket_model():
    """Loads PocketTTS 100M model instance."""
    if "pocket" in _model_cache:
        return _model_cache["pocket"]

    from pocket_tts import TTSModel

    tts_model = TTSModel.load_model()
    _model_cache["pocket"] = tts_model
    return tts_model


def synthesize_kitten(text, submodel="nano_v1", voice=None, speed=1.0):
    """Synthesizes text using KittenTTS."""
    model, available_voices = get_kitten_model(submodel)
    if not voice or voice not in available_voices:
        voice = available_voices[0]

    audio = model.generate(text, voice=voice)
    sample_rate = 24000
    return audio, sample_rate, voice


def synthesize_kokoro(text, voice="af_heart", speed=1.0, lang="en-us"):
    """Synthesizes text using Kokoro ONNX."""
    kokoro = get_kokoro_model()
    available_voices = kokoro.get_voices()
    if voice not in available_voices:
        voice = "af_heart"

    audio, sample_rate = kokoro.create(text, voice=voice, speed=speed, lang=lang)
    return audio, sample_rate, voice


def synthesize_pocket(text, voice_or_ref="alba"):
    """Synthesizes text using PocketTTS (presets or zero-shot cloning)."""
    tts_model = get_pocket_model()
    try:
        voice_state = tts_model.get_state_for_audio_prompt(voice_or_ref)
    except ValueError as ve:
        if "VOICE_CLONING_UNSUPPORTED" in str(ve) or "weights for the model with voice cloning" in str(ve):
            raise RuntimeError(
                "Pocket TTS Voice Cloning requires Hugging Face authentication to download gated weights.\n"
                "To enable cloning:\n"
                "1. Accept terms at https://huggingface.co/kyutai/pocket-tts\n"
                "2. Run `huggingface-cli login` in your terminal\n\n"
                "Preset voices (Alba, Marius, Jean, Cosette, etc.) are available offline without login."
            ) from ve
        raise ve

    audio_tensor = tts_model.generate_audio(voice_state, text)
    audio_data = audio_tensor.cpu().numpy() if hasattr(audio_tensor, "cpu") else audio_tensor
    sample_rate = getattr(tts_model, "sample_rate", 24000)
    return audio_data, sample_rate, voice_or_ref


def save_audio(audio_data, output_path, sample_rate):
    """Saves numpy audio array to a WAV file."""
    sf.write(output_path, audio_data, sample_rate)
    return output_path
