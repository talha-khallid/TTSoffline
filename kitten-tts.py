import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from kittentts import KittenTTS

# The 3 distinct model architectures compatible with your current setup
MODELS = {
    "1": {
        "name": "KittenTTS Nano v1 (15M Parameters / 24MB - Ultra Fast)",
        "repo_id": "KittenML/kitten-tts-nano-0.1",
        "model_file": "kitten_tts_nano_v0_1.onnx",
        "voices_file": "voices.npz",
    },
    "2": {
        "name": "KittenTTS Nano v2 (15M Parameters / 24MB - Enhanced Clarity)",
        "repo_id": "KittenML/kitten-tts-nano-0.2",
        "model_file": "kitten_tts_nano_v0_2.onnx",
        "voices_file": "voices.npz",
    },
    "3": {
        "name": "KittenTTS Mini (80M Parameters / 166MB - Highest Quality)",
        "repo_id": "KittenML/kitten-tts-mini-0.1",
        "model_file": "kitten_tts_mini_v0_1.onnx",
        "voices_file": "voices.npz",
    },
}

def main():
    print("=== KittenTTS 3-Model Voice CLI ===")

    # 1. Prompt for Text
    text = input("\nWhat do you want the model to say?\n> ").strip()
    if not text:
        print("No text entered. Exiting.")
        return

    # 2. Select Model Size
    print("\nSelect a Model:")
    for key, info in MODELS.items():
        print(f"[{key}] {info['name']}")

    while True:
        model_choice = input("\nPick a model (1, 2, or 3): ").strip()
        if model_choice in MODELS:
            selected_model = MODELS[model_choice]
            break
        print("Invalid choice. Enter 1, 2, or 3.")

    # 3. Load Model and Voices from Cache (Zero re-download if already cached)
    print(f"\nLoading {selected_model['name']}...")
    try:
        model_path = hf_hub_download(
            repo_id=selected_model["repo_id"],
            filename=selected_model["model_file"],
        )
        voices_path = hf_hub_download(
            repo_id=selected_model["repo_id"],
            filename=selected_model["voices_file"],
        )
    except Exception as e:
        print(f"Error loading model weights: {e}")
        return

    # Initialize ONNX inference session with matching voice profiles
    model = KittenTTS(model_path)
    model._voices = np.load(voices_path)

    # 4. Select Voice Preset
    available_voices = list(model._voices.files)
    print("\nAvailable Voices for this model:")
    for i, v in enumerate(available_voices):
        print(f"[{i + 1}] {v}")

    while True:
        try:
            v_choice = input(f"\nPick a voice (1-{len(available_voices)}) [default 1]: ").strip()
            if not v_choice:
                idx = 0
                break
            idx = int(v_choice) - 1
            if 0 <= idx < len(available_voices):
                break
            print(f"Enter a number between 1 and {len(available_voices)}.")
        except ValueError:
            print("Invalid input.")

    selected_voice = available_voices[idx]

    # 5. Generate Clear Audio
    print(f"\nSynthesizing with '{selected_voice}' on {selected_model['name'].split()[1]}...")
    try:
        audio = model.generate(text, voice=selected_voice)
        output_file = "output.wav"
        sf.write(output_file, audio, 24000)

        print(f"\nSuccess! Audio generated and saved to '{output_file}'.")
        print(f"Listen with: aplay {output_file}")
    except Exception as e:
        print(f"\nGeneration error: {e}")

if __name__ == "__main__":
    main()