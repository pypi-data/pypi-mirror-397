"""
APA Writer Backend API
======================
Exposes the Voice Preservation and Citation engines to the Chrome Extension.

Run: uvicorn src.apa_writer_backend.main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import our Engines
from src.apa_writer_backend.citation_engine import CitationEngine
from src.apa_writer_backend.voice_preservation import VoicePreservationEngine

app = FastAPI(title="APA Writer Backend", version="1.0.0")

# Initialize Engines
citation_engine = CitationEngine()
voice_engine = VoicePreservationEngine()

class CitationRequest(BaseModel):
    doi: Optional[str] = None
    title: Optional[str] = None

class VoiceRequest(BaseModel):
    text: str
    reference_text: Optional[str] = None

@app.get("/")
def health_check():
    return {"status": "active", "module": "APA Writer Backend"}

@app.post("/citation")
def get_citation(req: CitationRequest):
    """
    Get an APA-7 citation for a DOI or Title.
    """
    if req.doi:
        meta = citation_engine.lookup_doi(req.doi)
    elif req.title:
        results = citation_engine.search_by_title(req.title, limit=1)
        if not results:
            raise HTTPException(status_code=404, detail="Paper not found")
        meta = results[0]
    else:
        raise HTTPException(status_code=400, detail="Must provide DOI or Title")

    citation = citation_engine.format_apa7(meta)
    return {"citation": citation, "metadata": meta}

@app.post("/voice/analyze")
def analyze_voice(req: VoiceRequest):
    """
    Analyze text for 'Voice Drift' using SSG + TextStat.
    """
    result = voice_engine.analyze_voice(req.text, req.reference_text)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
