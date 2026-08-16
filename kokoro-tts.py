#!/usr/bin/env python3
import os
import sys
import webbrowser

import tts_core

KOKORO_VOICES = tts_core.KOKORO_VOICE_PRESETS


def run_terminal_mode():
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
        output_file = "kokoro_output.wav"
        tts_core.save_audio(audio, output_file, sample_rate)

        print("\n" + "─" * 54)
        print("✅ SYNTHESIS SUCCESSFUL!")
        print(f"📁 Output File : {output_file}")
        print(f"🎙️ Voice Persona: {selected_voice['name']}")
        print(f"🎧 Sample Rate : {sample_rate} Hz")
        print(f"🔊 Play Audio  : aplay {output_file}")
        print("─" * 54 + "\n")
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")


def main():
    print("\n" + "=" * 54)
    print("             🌸 KOKORO TTS STUDIO")
    print("=" * 54)
    print("How would you like to run Kokoro TTS?")
    print("  [1] Terminal Mode (CLI Generation)")
    print("  [2] Web UI Mode   (Browser Interface)")

    mode = input("\nSelect mode (1 or 2) [default 1]: ").strip() or "1"

    if mode == "2":
        port = 8001
        url = f"http://localhost:{port}?model=kokoro"
        print(f"\n🚀 Launching Web UI for Kokoro TTS at {url} ...")
        webbrowser.open(url)
        import uvicorn

        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
    else:
        run_terminal_mode()


if __name__ == "__main__":
    main()