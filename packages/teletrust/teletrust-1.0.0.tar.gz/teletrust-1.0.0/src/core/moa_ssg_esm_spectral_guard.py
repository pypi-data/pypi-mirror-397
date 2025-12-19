#!/usr/bin/env python3
# moa_ssg_esm_spectral_guard.py
# Purpose: SSG × ESM spectral guard v2 (offline-friendly, no telemetry)

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
import sqlite3
import sys
import time
import wave
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    from scipy import signal as sp_signal
except Exception as e:
    raise SystemExit("Missing dependency: scipy. Install scipy to run this module.") from e


# -----------------------------
# Utilities
# -----------------------------

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def now_unix() -> int:
    return int(time.time())

def safe_mkdir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def read_wav_mono(path: str) -> Tuple[np.ndarray, int]:
    """Reads PCM WAV using stdlib wave. Returns float32 mono in [-1,1], fs."""
    with wave.open(path, "rb") as wf:
        n_ch = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        fs = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if sampwidth not in (1, 2, 3, 4):
        raise ValueError(f"Unsupported WAV sample width: {sampwidth}")

    # Convert bytes -> int
    if sampwidth == 1:
        x = np.frombuffer(raw, dtype=np.uint8).astype(np.int16) - 128
        denom = 128.0
    elif sampwidth == 2:
        x = np.frombuffer(raw, dtype=np.int16)
        denom = 32768.0
    elif sampwidth == 3:
        # 24-bit little-endian PCM
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) |
             (a[:, 1].astype(np.int32) << 8) |
             (a[:, 2].astype(np.int32) << 16))
        # Sign extend
        x = (x ^ 0x800000) - 0x800000
        denom = float(2**23)
    else:  # 4
        x = np.frombuffer(raw, dtype=np.int32)
        denom = float(2**31)

    if n_ch > 1:
        x = x.reshape(-1, n_ch).mean(axis=1)

    y = (x.astype(np.float32) / denom).clip(-1.0, 1.0)
    return y, fs


# -----------------------------
# Layer A: Aperiodic exponent + spectral features
# -----------------------------

@dataclasses.dataclass
class SpectralConfig:
    fs: float = 1.0
    nperseg: int = 256
    noverlap: int = 128
    fmin: float = 0.01
    fmax: float = 0.40
    detrend: str = "linear"

def welch_psd(x: np.ndarray, cfg: SpectralConfig) -> Tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError("welch_psd expects 1D array")
    if not np.isfinite(x).all():
        raise ValueError("Non-finite values in input")
    if len(x) < 16:
        raise ValueError("Input too short")

    nper = min(cfg.nperseg, len(x))
    nov = min(cfg.noverlap, max(0, nper - 1))

    f, p = sp_signal.welch(
        x,
        fs=cfg.fs,
        window="hann",
        nperseg=nper,
        noverlap=nov,
        detrend=cfg.detrend,
        scaling="density",
        return_onesided=True,
        average="mean",
    )
    return f, p

def fit_aperiodic_exponent(f: np.ndarray, p: np.ndarray, fmin: float, fmax: float) -> Tuple[float, float, int]:
    """
    Fits log10(P) = b - chi*log10(f) for f in [fmin,fmax], excluding f=0.
    Returns (chi, b, n_points).
    """
    f = np.asarray(f, dtype=np.float64)
    p = np.asarray(p, dtype=np.float64)

    m = (f > 0.0) & np.isfinite(f) & np.isfinite(p) & (p > 0.0) & (f >= fmin) & (f <= fmax)
    ff = f[m]
    pp = p[m]
    if ff.size < 6:
        raise ValueError("Not enough frequency points in fit band")

    x = np.log10(ff)
    y = np.log10(pp)

    # Weighted least squares: downweight highest frequencies slightly (optional but stable)
    w = 1.0 / (ff ** 0.25)
    w = w / np.mean(w)

    # Solve for y = a*x + c using weights
    X = np.vstack([x, np.ones_like(x)]).T
    W = np.diag(w)
    beta = np.linalg.lstsq(W @ X, W @ y, rcond=None)[0]  # [a, c]
    a, c = float(beta[0]), float(beta[1])

    chi = -a
    b = c
    return chi, b, int(ff.size)

def spectral_entropy(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=np.float64)
    p = np.where(np.isfinite(p) & (p > 0), p, 0.0)
    s = float(p.sum())
    if s <= 0:
        return float("nan")
    q = p / s
    q = q[q > 0]
    h = -float(np.sum(q * np.log(q)))
    return h / math.log(len(p) + 1e-12)

def spectral_flatness(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=np.float64)
    p = np.where(np.isfinite(p) & (p > 0), p, np.nan)
    if np.all(np.isnan(p)):
        return float("nan")
    gm = float(np.exp(np.nanmean(np.log(p))))
    am = float(np.nanmean(p))
    if am <= 0:
        return float("nan")
    return gm / am

def bandpower(f: np.ndarray, p: np.ndarray, fmin: float, fmax: float) -> float:
    m = (f >= fmin) & (f <= fmax) & np.isfinite(p)
    if not np.any(m):
        return 0.0
    return float(np.trapz(p[m], f[m]))

def embedding_to_channels(E: np.ndarray, max_ch: int = 4) -> np.ndarray:
    """
    E: [T,D]. Returns channels [T,C] using PCA on centered data.
    No sklearn dependency.
    """
    E = np.asarray(E, dtype=np.float64)
    if E.ndim != 2:
        raise ValueError("Embeddings must be 2D [T,D]")
    T, D = E.shape
    if T < 16 or D < 2:
        raise ValueError("Embeddings too small")
    X = E - E.mean(axis=0, keepdims=True)
    # SVD for PCA directions
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    C = int(min(max_ch, Vt.shape[0]))
    # Project
    Y = X @ Vt[:C].T
    return Y.astype(np.float64)

def spectral_features_from_series(x: np.ndarray, cfg: SpectralConfig) -> Dict[str, Any]:
    f, p = welch_psd(x, cfg)
    chi, b, nfit = fit_aperiodic_exponent(f, p, cfg.fmin, cfg.fmax)

    bp_low = bandpower(f, p, cfg.fmin, min(cfg.fmax, cfg.fmin * 4))
    bp_mid = bandpower(f, p, min(cfg.fmax, cfg.fmin * 4), min(cfg.fmax, cfg.fmin * 16))
    bp_all = bandpower(f, p, cfg.fmin, cfg.fmax)
    ratio_low_mid = (bp_low / (bp_mid + 1e-12)) if bp_all > 0 else float("nan")

    return {
        "chi": float(chi),
        "b": float(b),
        "nfit": int(nfit),
        "entropy": float(spectral_entropy(p)),
        "flatness": float(spectral_flatness(p)),
        "bp_all": float(bp_all),
        "bp_low": float(bp_low),
        "bp_mid": float(bp_mid),
        "ratio_low_mid": float(ratio_low_mid),
    }


# -----------------------------
# Layer B: SSG (syllable structure graph) + optional audio congruence
# -----------------------------

_VOWELS = set("aeiouyAEIOUY")

def syllabify_heuristic(text: str) -> List[str]:
    """
    Fast syllable proxy: groups of vowel-runs with surrounding consonants.
    Not linguistically perfect; good enough for structure drift checks.
    """
    t = "".join(ch if ch.isalpha() or ch.isspace() else " " for ch in text)
    words = [w for w in t.split() if w]
    out: List[str] = []
    for w in words:
        cur = []
        last_v = False
        for ch in w:
            is_v = ch in _VOWELS
            if cur and is_v and not last_v:
                out.append("".join(cur).lower())
                cur = [ch]
            else:
                cur.append(ch)
            last_v = is_v
        if cur:
            out.append("".join(cur).lower())
    return out

def ssg_bigram_graph(syllables: List[str]) -> Dict[str, Any]:
    if len(syllables) < 2:
        return {"n": len(syllables), "edges": {}, "entropy": 0.0, "fingerprint": sha256_hex(b"")}
    edges: Dict[str, int] = {}
    for a, b in zip(syllables[:-1], syllables[1:]):
        k = f"{a}->{b}"
        edges[k] = edges.get(k, 0) + 1

    counts = np.array(list(edges.values()), dtype=np.float64)
    p = counts / max(1.0, counts.sum())
    ent = -float(np.sum(p * np.log(p + 1e-12)))

    # Order-independent fingerprint
    items = sorted(edges.items(), key=lambda kv: kv[0])
    payload = json.dumps(items, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    fp = sha256_hex(payload)

    return {"n": len(syllables), "edges": edges, "entropy": float(ent), "fingerprint": fp}

def audio_syllable_rate_proxy(y: np.ndarray, fs: int) -> float:
    """
    Simple onset proxy using rectified, smoothed energy.
    Returns peaks/sec as a syllable-rate proxy.
    """
    y = np.asarray(y, dtype=np.float64)
    if y.size < fs // 2:
        return float("nan")

    # High-pass-ish via differencing
    d = np.diff(y, prepend=y[0])
    e = np.abs(d)

    # Smooth
    win = max(3, int(0.02 * fs))
    k = np.ones(win, dtype=np.float64) / win
    s = np.convolve(e, k, mode="same")

    # Peak pick
    thr = np.median(s) + 2.5 * (np.median(np.abs(s - np.median(s))) + 1e-12)
    peaks = np.where((s[1:-1] > s[:-2]) & (s[1:-1] > s[2:]) & (s[1:-1] > thr))[0] + 1
    dur = y.size / float(fs)
    return float(peaks.size / max(dur, 1e-9))


# -----------------------------
# ESM store: rolling baseline + hash-chain audit
# -----------------------------

@dataclasses.dataclass
class ESMConfig:
    db_path: str
    ttl_seconds: int = 7 * 24 * 3600
    max_rows: int = 20000

class ESMStore:
    def __init__(self, cfg: ESMConfig):
        self.cfg = cfg
        safe_mkdir(os.path.dirname(cfg.db_path) or ".")
        self.conn = sqlite3.connect(cfg.db_path)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS esm_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            context TEXT NOT NULL,
            features_json TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            this_hash TEXT NOT NULL
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_esm_ts ON esm_events(ts);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_esm_ctx ON esm_events(context);")
        self.conn.commit()

    def _get_last_hash(self) -> str:
        cur = self.conn.cursor()
        cur.execute("SELECT this_hash FROM esm_events ORDER BY id DESC LIMIT 1;")
        r = cur.fetchone()
        return r[0] if r else "0" * 64

    def prune(self) -> None:
        cutoff = now_unix() - int(self.cfg.ttl_seconds)
        cur = self.conn.cursor()
        cur.execute("DELETE FROM esm_events WHERE ts < ?;", (cutoff,))
        # Cap rows
        cur.execute("SELECT COUNT(*) FROM esm_events;")
        n = int(cur.fetchone()[0])
        if n > self.cfg.max_rows:
            drop = n - self.cfg.max_rows
            cur.execute("""
                DELETE FROM esm_events
                WHERE id IN (SELECT id FROM esm_events ORDER BY id ASC LIMIT ?);
            """, (drop,))
        self.conn.commit()

    def add(self, context: str, features: Dict[str, Any]) -> str:
        ts = now_unix()
        prev = self._get_last_hash()
        features_json = json.dumps(features, separators=(",", ":"), ensure_ascii=False)
        payload = f"{ts}|{context}|{features_json}|{prev}".encode("utf-8")
        h = sha256_hex(payload)

        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO esm_events (ts, context, features_json, prev_hash, this_hash) VALUES (?,?,?,?,?);",
            (ts, context, features_json, prev, h),
        )
        self.conn.commit()
        return h

    def baseline_stats(self, context: str, keys: List[str], lookback: int = 500) -> Dict[str, Any]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT features_json FROM esm_events
            WHERE context = ?
            ORDER BY id DESC LIMIT ?;
        """, (context, lookback))
        rows = [json.loads(r[0]) for r in cur.fetchall()]
        if not rows:
            return {"n": 0}

        X = []
        for r in rows:
            vec = []
            ok = True
            for k in keys:
                v = r.get(k, None)
                if v is None or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
                    ok = False
                    break
                vec.append(float(v))
            if ok:
                X.append(vec)

        if len(X) < 10:
            return {"n": len(X)}

        A = np.array(X, dtype=np.float64)
        mu = A.mean(axis=0)
        sd = A.std(axis=0) + 1e-9
        return {"n": int(A.shape[0]), "mean": mu.tolist(), "std": sd.tolist()}

def zscore(features: Dict[str, Any], stats: Dict[str, Any], keys: List[str]) -> Dict[str, float]:
    if stats.get("n", 0) < 10:
        return {}
    mu = np.array(stats["mean"], dtype=np.float64)
    sd = np.array(stats["std"], dtype=np.float64)
    vec = np.array([float(features[k]) for k in keys], dtype=np.float64)
    z = (vec - mu) / sd
    return {k: float(z[i]) for i, k in enumerate(keys)}


# -----------------------------
# Pipeline
# -----------------------------

def analyze_v2(
    context: str,
    text: Optional[str],
    embeddings_path: Optional[str],
    wav_path: Optional[str],
    store: Optional[ESMStore],
    cfg: SpectralConfig,
) -> Dict[str, Any]:

    out: Dict[str, Any] = {"context": context, "ts": now_unix()}

    # SSG features (text)
    if text is not None:
        syl = syllabify_heuristic(text)
        g = ssg_bigram_graph(syl)
        out["ssg_n"] = g["n"]
        out["ssg_entropy"] = g["entropy"]
        out["ssg_fp"] = g["fingerprint"]
    else:
        out["ssg_n"] = 0
        out["ssg_entropy"] = float("nan")
        out["ssg_fp"] = "0" * 64

    # Audio congruence (optional)
    if wav_path is not None:
        y, fs = read_wav_mono(wav_path)
        r = audio_syllable_rate_proxy(y, fs)
        out["audio_rate_proxy"] = r
        if text is not None and out["ssg_n"] > 0 and math.isfinite(r):
            dur = y.size / float(fs)
            expected = out["ssg_n"] / max(dur, 1e-9)
            out["rate_error"] = float(abs(r - expected))
        else:
            out["rate_error"] = float("nan")
    else:
        out["audio_rate_proxy"] = float("nan")
        out["rate_error"] = float("nan")

    # Embedding dynamics spectral features (optional)
    if embeddings_path is not None:
        E = np.load(embeddings_path)  # expects [T,D]
        Y = embedding_to_channels(E, max_ch=4)
        feats = []
        for c in range(Y.shape[1]):
            fdict = spectral_features_from_series(Y[:, c], cfg)
            feats.append(fdict)
        # Aggregate
        chis = [f["chi"] for f in feats if math.isfinite(f["chi"])]
        out["chi_mean"] = float(np.mean(chis)) if chis else float("nan")
        out["chi_std"] = float(np.std(chis)) if chis else float("nan")
        out["entropy_mean"] = float(np.mean([f["entropy"] for f in feats if math.isfinite(f["entropy"])])) if feats else float("nan")
        out["flatness_mean"] = float(np.mean([f["flatness"] for f in feats if math.isfinite(f["flatness"])])) if feats else float("nan")
        out["ratio_low_mid_mean"] = float(np.mean([f["ratio_low_mid"] for f in feats if math.isfinite(f["ratio_low_mid"])])) if feats else float("nan")
    else:
        out["chi_mean"] = float("nan")
        out["chi_std"] = float("nan")
        out["entropy_mean"] = float("nan")
        out["flatness_mean"] = float("nan")
        out["ratio_low_mid_mean"] = float("nan")

    # ESM baseline + flags
    keys = ["chi_mean", "chi_std", "entropy_mean", "flatness_mean", "ratio_low_mid_mean", "ssg_entropy", "rate_error"]
    numeric_keys = [k for k in keys if isinstance(out.get(k, None), (int, float)) and math.isfinite(float(out[k]))]

    if store is not None and numeric_keys:
        store.prune()
        stats = store.baseline_stats(context, numeric_keys, lookback=500)
        out["baseline_n"] = int(stats.get("n", 0))

        z = zscore(out, stats, numeric_keys) if stats.get("n", 0) >= 10 else {}
        out["z"] = z

        # Conservative flags: any |z| > 3.5 is “hard drift”
        hard = [k for k, v in z.items() if abs(v) >= 3.5]
        out["hard_drift_keys"] = hard
        out["hard_drift"] = bool(hard)

        # Write event to ESM
        event_hash = store.add(context, {k: out.get(k) for k in ["chi_mean","chi_std","entropy_mean","flatness_mean","ratio_low_mid_mean","ssg_entropy","rate_error","ssg_fp","audio_rate_proxy"]})
        out["event_hash"] = event_hash
    else:
        out["baseline_n"] = 0
        out["z"] = {}
        out["hard_drift_keys"] = []
        out["hard_drift"] = False
        out["event_hash"] = ""

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="SSG × ESM spectral guard v2")
    ap.add_argument("--context", required=True, help="Baseline key, e.g., modelA:clinical_note:pos_check")
    ap.add_argument("--text", default=None, help="Raw text for SSG syllable structure")
    ap.add_argument("--embeddings_npy", default=None, help="Path to .npy embeddings [T,D]")
    ap.add_argument("--wav", default=None, help="Path to PCM .wav for congruence proxy")
    ap.add_argument("--db", default=None, help="SQLite path for ESM store (offline)")
    ap.add_argument("--fs", type=float, default=1.0, help="Sample rate for embedding time axis (tokens/sec or steps/sec)")
    ap.add_argument("--fmin", type=float, default=0.01)
    ap.add_argument("--fmax", type=float, default=0.40)
    ap.add_argument("--nperseg", type=int, default=256)
    ap.add_argument("--noverlap", type=int, default=128)

    args = ap.parse_args()

    cfg = SpectralConfig(
        fs=float(args.fs),
        nperseg=int(args.nperseg),
        noverlap=int(args.noverlap),
        fmin=float(args.fmin),
        fmax=float(args.fmax),
        detrend="linear",
    )

    store = None
    if args.db:
        store = ESMStore(ESMConfig(db_path=args.db))

    out = analyze_v2(
        context=args.context,
        text=args.text,
        embeddings_path=args.embeddings_npy,
        wav_path=args.wav,
        store=store,
        cfg=cfg,
    )

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
