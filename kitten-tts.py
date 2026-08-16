#!/usr/bin/env python3
import os
import sys
import webbrowser

import tts_core

KITTEN_MODELS = tts_core.KITTEN_MODELS


def run_terminal_mode():
    print("\n" + "=" * 54)
    print("      🐱 KITTEN TTS — TERMINAL SYNTHESIS MODE")
    print("=" * 54)

    # 1. Prompt for Text
    text = input("\nEnter text to synthesize:\n> ").strip()
    if not text:
        print("❌ No text entered. Exiting.")
        return

    # 2. Select Model Size
    print("\nSelect KittenTTS Model Architecture:")
    keys = list(KITTEN_MODELS.keys())
    for idx, key in enumerate(keys, 1):
        info = KITTEN_MODELS[key]
        print(f"  [{idx}] {info['name']}")

    while True:
        choice = input(f"\nPick a model (1-{len(keys)}) [default 1]: ").strip() or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(keys):
            selected_model_key = keys[int(choice) - 1]
            break
        print(f"Invalid input. Please enter a number between 1 and {len(keys)}.")

    selected_model = KITTEN_MODELS[selected_model_key]

    # 3. Load Model and Voices
    print(f"\n🔄 Loading {selected_model['name']}...")
    try:
        model, available_voices = tts_core.get_kitten_model(selected_model_key)
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    # 4. Select Voice Preset
    print("\nAvailable Voices:")
    for idx, voice_name in enumerate(available_voices, 1):
        print(f"  [{idx}] {voice_name}")

    while True:
        v_choice = (
            input(f"\nPick a voice (1-{len(available_voices)}) [default 1]: ").strip() or "1"
        )
        if v_choice.isdigit() and 1 <= int(v_choice) <= len(available_voices):
            selected_voice = available_voices[int(v_choice) - 1]
            break
        print(f"Invalid input. Enter a number between 1 and {len(available_voices)}.")

    # 5. Synthesize Audio
    print(
        f"\n⚡ Synthesizing with '{selected_voice}' on {selected_model['name'].split()[0]}..."
    )
    try:
        audio, sample_rate, _ = tts_core.synthesize_kitten(
            text=text, submodel=selected_model_key, voice=selected_voice
        )
        output_file = "kitten_output.wav"
        tts_core.save_audio(audio, output_file, sample_rate)

        print("\n" + "─" * 54)
        print("✅ SYNTHESIS SUCCESSFUL!")
        print(f"📁 Output File : {output_file}")
        print(f"🎧 Sample Rate : {sample_rate} Hz")
        print(f"🔊 Play Audio  : aplay {output_file}")
        print("─" * 54 + "\n")
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")


def main():
    print("\n" + "=" * 54)
    print("             🐱 KITTEN TTS STUDIO")
    print("=" * 54)
    print("How would you like to run Kitten TTS?")
    print("  [1] Terminal Mode (CLI Generation)")
    print("  [2] Web UI Mode   (Browser Interface)")

    mode = input("\nSelect mode (1 or 2) [default 1]: ").strip() or "1"

    if mode == "2":
        port = 8000
        url = f"http://localhost:{port}?model=kitten"
        print(f"\n🚀 Launching Web UI for Kitten TTS at {url} ...")
        webbrowser.open(url)
        import uvicorn

        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
    else:
        run_terminal_mode()


if __name__ == "__main__":
    main()