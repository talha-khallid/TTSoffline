import os
import soundfile as sf
from pocket_tts import TTSModel

VOICE_PRESETS = {
    "1": {"id": "alba", "name": "Alba (Female)"},
    "2": {"id": "marius", "name": "Marius (Male)"},
    "3": {"id": "jaime", "name": "Jaime (Male)"},
    "4": {"id": "jean", "name": "Jean (Male)"},
}


def main():
    print("=== PocketTTS 100M Dual-Mode CLI (Preset & Zero-Shot Cloning) ===")

    # 1. Prompt for Text
    text = input("What do you want the model to say?\n> ").strip()
    if not text:
        print("No text entered. Exiting.")
        return

    # 2. Select Voice Preset or Clone
    print("\nVoice Generation Mode:")
    for key, v in VOICE_PRESETS.items():
        print(f"[{key}] Preset: {v['name']}")
    clone_key = str(len(VOICE_PRESETS) + 1)
    print(f"[{clone_key}] Zero-shot Voice Clone (.wav reference file)")

    choice = input(f"\nPick an option (1-{clone_key}) [default 1]: ").strip() or "1"

    voice_prompt = "alba"
    voice_label = "Alba (Female)"

    if choice == clone_key:
        while True:
            ref_path = input("\nEnter path to reference .wav clip (or Enter for 'alba'): ").strip()
            if not ref_path:
                print("No file provided. Falling back to preset 'alba'.")
                break
            if os.path.isfile(ref_path):
                voice_prompt = ref_path
                voice_label = f"Cloned from '{ref_path}'"
                break
            print(f"File '{ref_path}' not found. Please enter a valid path.")
    else:
        selected = VOICE_PRESETS.get(choice, VOICE_PRESETS["1"])
        voice_prompt = selected["id"]
        voice_label = selected["name"]

    # 3. Load Model Checkpoint
    print("\nLoading PocketTTS 100M model onto CPU...")
    tts_model = TTSModel.load_model()

    # 4. Generate Speech
    print(f"Synthesizing with {voice_label}...")
    voice_state = tts_model.get_state_for_audio_prompt(voice_prompt)
    audio_tensor = tts_model.generate_audio(voice_state, text)

    # 5. Save Output
    output_file = "pocket_output.wav"
    audio_data = audio_tensor.cpu().numpy() if hasattr(audio_tensor, "cpu") else audio_tensor
    sf.write(output_file, audio_data, tts_model.sample_rate)

    print(f"\nSuccess! Audio generated and saved to '{output_file}'.")
    print(f"Listen with: aplay {output_file}")


if __name__ == "__main__":
    main()
