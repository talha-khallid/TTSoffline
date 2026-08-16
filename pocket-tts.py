#!/usr/bin/env python3
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import tts_core

POCKET_VOICES = tts_core.POCKET_VOICE_PRESETS


def main():
    print("\n" + "=" * 54)
    print("   🎙️ POCKET TTS 100M — TERMINAL SYNTHESIS & CLONING MODE")
    print("=" * 54)

    # 1. Prompt for Text
    text = input("\nEnter text to synthesize:\n> ").strip()
    if not text:
        print("❌ No text entered. Exiting.")
        return

    # 2. Select Voice Preset or Zero-Shot Clone
    print("\nVoice Generation Mode:")
    for idx, v in enumerate(POCKET_VOICES, 1):
        print(f"  [{idx}] Preset Voice: {v['name']}")
    clone_idx = len(POCKET_VOICES) + 1
    print(f"  [{clone_idx}] Zero-Shot Voice Clone (reference .wav file)")

    choice = input(f"\nPick an option (1-{clone_idx}) [default 1]: ").strip() or "1"

    voice_target = "alba"
    voice_label = "Alba (Female)"

    if choice == str(clone_idx):
        while True:
            ref_path = input("\nEnter path to reference .wav clip: ").strip()
            if not ref_path:
                print("No file provided. Falling back to preset 'alba'.")
                break
            if os.path.isfile(ref_path):
                voice_target = ref_path
                voice_label = f"Cloned from '{os.path.basename(ref_path)}'"
                break
            print(f"❌ File '{ref_path}' not found. Please enter a valid file path.")
    else:
        if choice.isdigit() and 1 <= int(choice) <= len(POCKET_VOICES):
            selected = POCKET_VOICES[int(choice) - 1]
        else:
            selected = POCKET_VOICES[0]
        voice_target = selected["id"]
        voice_label = selected["name"]

    # 3. Synthesize Speech
    print(f"\n⚡ Synthesizing speech with {voice_label}...")
    try:
        audio, sample_rate, used_voice = tts_core.synthesize_pocket(
            text=text, voice_or_ref=voice_target
        )
        output_file = os.path.join(OUTPUTS_DIR, "pocket_output.wav")
        tts_core.save_audio(audio, output_file, sample_rate)

        print("\n" + "─" * 54)
        print("✅ SYNTHESIS SUCCESSFUL!")
        print(f"📁 Output File : {output_file}")
        print(f"🎙️ Voice Mode   : {voice_label}")
        print(f"🎧 Sample Rate : {sample_rate} Hz")
        print(f"🔊 Play Audio  : aplay \"{output_file}\"")
        print("─" * 54 + "\n")
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")


if __name__ == "__main__":
    main()
