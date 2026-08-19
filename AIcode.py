import base64
import io
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import google.generativeai as genai

# Set your Gemini API Key directly here or via system environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImagePayload(BaseModel):
    image: str  # Base64 string from canvas

@app.post("/api/evaluate")
async def evaluate_handwriting(payload: ImagePayload):
    try:
        # Strip base64 header if present (e.g., "data:image/png;base64,")
        base64_data = payload.image
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]

        # Decode base64 bytes into PIL Image
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_bytes))

        # Flatten transparent background onto solid white
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
            image = background
        else:
            image = image.convert('RGB')

        # Request vision evaluation from Gemini
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = """
        Analyze the handwriting in this image. Return ONLY a valid JSON object matching this structure without extra text or markdown wrappers:
        {
            "text": "<exact transcribed handwriting>",
            "score": <legibility score 0-100 as integer>,
            "feedback": "<1-2 concise sentences analyzing legibility and letter formation>"
        }
        """

        response = model.generate_content([prompt, image])
        
        # Parse and sanitize response JSON
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").removeprefix("json").strip()

        return json.loads(raw_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("AIcode:app", host="127.0.0.1", port=8000, reload=True)