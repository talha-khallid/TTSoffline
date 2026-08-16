import os
import sys
import uuid
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import tts_core

app = FastAPI(title="TTS Studio Server")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "static_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class GenerateRequest(BaseModel):
    model: str  # "kitten", "kokoro", "pocket"
    text: str
    submodel: Optional[str] = "nano_v1"
    voice: Optional[str] = "expr-voice-5-m"
    speed: Optional[float] = 1.0


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    """Serves the standalone Web UI dashboard."""
    ui_path = os.path.join(BASE_DIR, "web_ui.html")
    if not os.path.exists(ui_path):
        raise HTTPException(status_code=404, detail="web_ui.html file not found.")
    with open(ui_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/generate")
def api_generate(req: GenerateRequest):
    """API endpoint for preset voice TTS synthesis."""
    try:
        filename = f"output_{uuid.uuid4().hex[:8]}.wav"
        out_path = os.path.join(OUTPUT_DIR, filename)

        if req.model == "kitten":
            audio, sr, used_voice = tts_core.synthesize_kitten(
                text=req.text, submodel=req.submodel, voice=req.voice
            )
        elif req.model == "kokoro":
            audio, sr, used_voice = tts_core.synthesize_kokoro(
                text=req.text, voice=req.voice, speed=req.speed
            )
        elif req.model == "pocket":
            audio, sr, used_voice = tts_core.synthesize_pocket(
                text=req.text, voice_or_ref=req.voice
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model '{req.model}'")

        tts_core.save_audio(audio, out_path, sr)
        audio_url = f"/output/{filename}"

        return {
            "status": "success",
            "model": req.model,
            "voice": used_voice,
            "audio_url": audio_url,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})


@app.post("/api/clone")
async def api_clone(text: str = Form(...), ref_audio: UploadFile = File(...)):
    """API endpoint for Pocket TTS Zero-Shot Voice Cloning."""
    try:
        ref_filename = f"ref_{uuid.uuid4().hex[:8]}.wav"
        ref_path = os.path.join(OUTPUT_DIR, ref_filename)
        out_filename = f"cloned_{uuid.uuid4().hex[:8]}.wav"
        out_path = os.path.join(OUTPUT_DIR, out_filename)

        with open(ref_path, "wb") as buffer:
            buffer.write(await ref_audio.read())

        audio, sr, used_voice = tts_core.synthesize_pocket(text=text, voice_or_ref=ref_path)
        tts_core.save_audio(audio, out_path, sr)
        audio_url = f"/output/{out_filename}"

        return {
            "status": "success",
            "model": "pocket_clone",
            "voice": f"Cloned ({ref_audio.filename})",
            "audio_url": audio_url,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})


@app.get("/output/{filename}")
def serve_audio(filename: str):
    """Serves generated output audio files."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Audio file not found.")


def main():
    import uvicorn

    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    print(f"\n🚀 Starting Unified TTS Studio Web UI on http://localhost:{port}\n")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
