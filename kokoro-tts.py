#!/usr/bin/env python3
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import tts_core

KOKORO_VOICES = tts_core.KOKORO_VOICE_PRESETS


def main():
    print("\n" + "=" * 54)
    print("      🌸 KOKORO TTS — TERMINAL SYNTHESIS MODE")
    print("=" * 54)

    # 1. Prompt for Text
    text = input("\nEnter text to synthesize:\n> ").strip()
    if not text:
        print("❌ No text entered. Exiting.")
        return

    # 2. Select Voice Persona
    print("\nSelect Kokoro Voice Preset:")
    for idx, v in enumerate(KOKORO_VOICES, 1):
        print(f"  [{idx}] {v['name']}")

    while True:
        v_choice = (
            input(f"\nPick a voice (1-{len(KOKORO_VOICES)}) [default 1]: ").strip() or "1"
        )
        if v_choice.isdigit() and 1 <= int(v_choice) <= len(KOKORO_VOICES):
            selected_voice = KOKORO_VOICES[int(v_choice) - 1]
            break
        print(f"Invalid input. Enter a number between 1 and {len(KOKORO_VOICES)}.")

    # 3. Prompt for Speed Multiplier
    speed_input = input("\nEnter speech speed multiplier (0.5 to 2.0) [default 1.0]: ").strip()
    try:
        speed = float(speed_input) if speed_input else 1.0
        speed = max(0.5, min(2.0, speed))
    except ValueError:
        speed = 1.0

    # 4. Synthesize Speech
    print(f"\n⚡ Synthesizing with '{selected_voice['name']}' (speed {speed}x)...")
    try:
        audio, sample_rate, voice_used = tts_core.synthesize_kokoro(
            text=text, voice=selected_voice["id"], speed=speed
        )
        output_file = os.path.join(OUTPUTS_DIR, "kokoro_output.wav")
        tts_core.save_audio(audio, output_file, sample_rate)

        print("\n" + "─" * 54)
        print("✅ SYNTHESIS SUCCESSFUL!")
        print(f"📁 Output File : {output_file}")
        print(f"🎙️ Voice Persona: {selected_voice['name']}")
        print(f"🎧 Sample Rate : {sample_rate} Hz")
        print(f"🔊 Play Audio  : aplay \"{output_file}\"")
        print("─" * 54 + "\n")
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")


if __name__ == "__main__":
    main()