import os
import time
import urllib.request
import soundfile as sf
from kokoro_onnx import Kokoro

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"

CONFIGS = {
    "1": {
        "label": "American English (en-us)",
        "lang_code": "en-us",
        "voices": [
            "af_heart",
            "af_bella",
            "af_nicole",
            "af_sarah",
            "af_sky",
            "am_adam",
            "am_michael",
            "am_echo",
            "am_eric",
            "am_onyx",
        ],
    },
    "2": {
        "label": "British English (en-gb)",
        "lang_code": "en-gb",
        "voices": [
            "bf_emma",
            "bf_isabella",
            "bf_alice",
            "bf_lily",
            "bm_george",
            "bm_lewis",
            "bm_daniel",
            "bm_fable",
        ],
    },
}


def download_with_progress(url: str, output_path: str):
    """Stream download with a real-time progress bar, MB tracker, and speed readout."""
    print(f"Downloading {output_path}...")
    
    # Request headers to follow redirects properly
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req) as response:
        total_size = int(response.headers.get("Content-Length", 0))
        chunk_size = 1024 * 64  # 64 KB per chunk
        downloaded = 0
        start_time = time.time()

        with open(output_path, "wb") as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                elapsed = time.time() - start_time
                speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                downloaded_mb = downloaded / (1024 * 1024)

                if total_size > 0:
                    total_mb = total_size / (1024 * 1024)
                    percent = (downloaded / total_size) * 100
                    
                    bar_length = 30
                    filled = int(bar_length * downloaded // total_size)
                    bar = "=" * filled + (">" if filled < bar_length else "") + "." * (bar_length - filled - 1 if filled < bar_length else 0)
                    
                    print(
                        f"\r[{bar}] {percent:5.1f}% | {downloaded_mb:6.1f} / {total_mb:6.1f} MB | {speed:4.1f} MB/s",
                        end="",
                        flush=True,
                    )
                else:
                    print(f"\rDownloaded: {downloaded_mb:6.1f} MB | {speed:4.1f} MB/s", end="", flush=True)

    print("\nDownload complete.\n")


def ensure_model_files():
    """Verify assets exist and are fully downloaded (Model > 50MB, Voices > 5MB)."""
    # Check model file integrity
    if not os.path.exists(MODEL_FILE) or os.path.getsize(MODEL_FILE) < 50 * 1024 * 1024:
        if os.path.exists(MODEL_FILE):
            os.remove(MODEL_FILE)
        download_with_progress(MODEL_URL, MODEL_FILE)

    # Check voice vectors integrity
    if not os.path.exists(VOICES_FILE) or os.path.getsize(VOICES_FILE) < 5 * 1024 * 1024:
        if os.path.exists(VOICES_FILE):
            os.remove(VOICES_FILE)
        download_with_progress(VOICES_URL, VOICES_FILE)


def main():
    print("=== Kokoro-82M Multi-Voice CLI (ONNX / No PyTorch) ===")
    ensure_model_files()

    # 1. Prompt for Text
    text = input("What do you want the model to say?\n> ").strip()
    if not text:
        print("No text entered. Exiting.")
        return

    # 2. Select Language / Accent
    print("\nSelect Dialect / Language:")
    for key, cfg in CONFIGS.items():
        print(f"[{key}] {cfg['label']}")

    while True:
        lang_choice = input(f"\nPick an option (1-{len(CONFIGS)}) [default 1]: ").strip() or "1"
        if lang_choice in CONFIGS:
            selected_cfg = CONFIGS[lang_choice]
            break
        print("Invalid choice.")

    # 3. Select Voice
    voices = selected_cfg["voices"]
    print(f"\nAvailable Voices ({selected_cfg['label']}):")
    for i, v in enumerate(voices):
        print(f"[{i + 1}] {v}")

    while True:
        v_choice = input(f"\nPick a voice (1-{len(voices)}) [default 1]: ").strip() or "1"
        try:
            idx = int(v_choice) - 1
            if 0 <= idx < len(voices):
                selected_voice = voices[idx]
                break
        except ValueError:
            pass
        print(f"Please enter a valid number between 1 and {len(voices)}.")

    # 4. Speech Speed
    speed_input = input("\nSet speed multiplier (0.5 to 2.0) [default 1.0]: ").strip() or "1.0"
    try:
        speed = float(speed_input)
    except ValueError:
        speed = 1.0

    # 5. Initialize ONNX Engine
    print("\nLoading Kokoro-82M ONNX Runtime engine...")
    kokoro = Kokoro(MODEL_FILE, VOICES_FILE)

    # 6. Generate Audio
    print(f"Synthesizing with '{selected_voice}' at {speed}x speed...")
    try:
        samples, sample_rate = kokoro.create(
            text=text,
            voice=selected_voice,
            speed=speed,
            lang=selected_cfg["lang_code"],
        )

        output_file = "kokoro_output.wav"
        sf.write(output_file, samples, sample_rate)

        print(f"\nSuccess! Saved audio to '{output_file}' ({sample_rate} Hz).")
        print(f"Play with: aplay {output_file}")

    except Exception as e:
        print(f"\nGeneration error: {e}")


if __name__ == "__main__":
    main()