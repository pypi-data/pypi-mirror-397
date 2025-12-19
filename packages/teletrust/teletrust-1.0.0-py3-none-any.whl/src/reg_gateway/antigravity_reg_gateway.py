from __future__ import annotations
import os
import json
from datetime import datetime
from typing import Dict, Any, List

CORPUS_PATH = os.getenv("REG_GATEWAY_CORPUS", "reg_gateway_corpus.jsonl")

def _ssg_stub(text: str) -> Dict[str, Any]:
    return {"fingerprint_version": "stub-0", "approx_len": len(text)}

def _moa_score_stub(fingerprint: Dict[str, Any]) -> float:
    length = max(1, fingerprint.get("approx_len", 1))
    return 1.0 / float(length)

def run_once() -> None:
    docs: List[Dict[str, Any]] = []

    # Placeholder example: one fake CMS doc
    raw = {
        "id": "cms-demo-001",
        "summary": "Updated CMS guidance on telehealth billing for mental health services.",
    }
    text = raw["summary"].strip()
    if text:
        fp = _ssg_stub(text)
        score = _moa_score_stub(fp)
        docs.append({
            "doc_id": raw["id"],
            "source": "cms-demo",
            "ingested_at": datetime.utcnow().isoformat(),
            "text": text,
            "ssg": fp,
            "moa": {"spectral_score": score},
        })

    if docs:
        with open(CORPUS_PATH, "a", encoding="utf-8") as f:
            for d in docs:
                f.write(json.dumps(d) + "\n")

    print(f"[{datetime.utcnow().isoformat()}] Ingested {len(docs)} docs into {CORPUS_PATH}")

if __name__ == "__main__":
    run_once()
