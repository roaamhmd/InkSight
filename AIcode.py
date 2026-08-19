from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    # Payload image is available as payload.image (Base64)
    # Pass image to Vision LLM / OCR Engine here
    
    return {
        "text": "Hello World",
        "score": 88,
        "feedback": "Great stroke alignment. Letter spacing is clean, though the 'r' could be clearer."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)