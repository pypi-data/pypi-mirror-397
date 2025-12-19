#!/usr/bin/env python3
"""
COMPREHENSIVE DEBUG & VERIFICATION REPORT
==========================================
Tests ALL P0/P1/P2 implementations with actual execution.
"""

import sys
import os
import json
import traceback
from pathlib import Path
from datetime import datetime

# Set up path
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
os.environ["PYTHONPATH"] = str(REPO_ROOT)

REPORT = {
    "timestamp": datetime.utcnow().isoformat(),
    "repo_root": str(REPO_ROOT),
    "tests": [],
    "summary": {"passed": 0, "failed": 0, "errors": 0}
}

def test(name, category):
    """Decorator for test functions."""
    def decorator(func):
        def wrapper():
            result = {"name": name, "category": category, "status": "UNKNOWN", "details": ""}
            try:
                output = func()
                result["status"] = "PASS"
                result["details"] = str(output) if output else "OK"
                REPORT["summary"]["passed"] += 1
            except AssertionError as e:
                result["status"] = "FAIL"
                result["details"] = str(e)
                REPORT["summary"]["failed"] += 1
            except Exception as e:
                result["status"] = "ERROR"
                result["details"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
                REPORT["summary"]["errors"] += 1
            REPORT["tests"].append(result)
            status_emoji = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥"}.get(result["status"], "❓")
            print(f"{status_emoji} [{category}] {name}: {result['status']}")
            if result["status"] != "PASS":
                print(f"   Details: {result['details'][:200]}...")
            return result
        return wrapper
    return decorator


# ============================================================================
# P0: NaN/Inf Fail-Closed Guards
# ============================================================================

@test("NaN triggers BLOCK", "P0-NaN/Inf")
def test_nan_guard():
    from src.governance.moa_gate import MoaTokenGate
    gate = MoaTokenGate()
    result = gate.evaluate({"spectral_state": {"entropy": float("nan")}})
    assert result["action"] == "BLOCK", f"Expected BLOCK, got {result['action']}"
    assert "CRITICAL_NAN_INF_DETECTED" in result["flags"], f"Missing flag: {result['flags']}"
    return result

@test("Inf triggers BLOCK", "P0-NaN/Inf")
def test_inf_guard():
    from src.governance.moa_gate import MoaTokenGate
    gate = MoaTokenGate()
    result = gate.evaluate({"spectral_state": {"entropy": float("inf")}})
    assert result["action"] == "BLOCK", f"Expected BLOCK, got {result['action']}"
    return result

@test("Normal entropy PASS", "P0-NaN/Inf")
def test_normal_entropy():
    from src.governance.moa_gate import MoaTokenGate
    gate = MoaTokenGate()
    result = gate.evaluate({"spectral_state": {"entropy": 4.0}})
    assert result["action"] == "PASS", f"Expected PASS, got {result['action']}"
    return result


# ============================================================================
# P0: Secret Scanning Files Exist
# ============================================================================

@test(".pre-commit-config.yaml exists", "P0-Secrets")
def test_precommit_exists():
    path = REPO_ROOT / ".pre-commit-config.yaml"
    assert path.exists(), f"File not found: {path}"
    content = path.read_text()
    assert "secrets-scan" in content, "Missing secrets-scan hook"
    assert "detect-secrets" in content, "Missing detect-secrets hook"
    return f"Size: {len(content)} bytes"

@test(".github/workflows/security.yml exists", "P0-Secrets")
def test_security_workflow_exists():
    path = REPO_ROOT / ".github" / "workflows" / "security.yml"
    assert path.exists(), f"File not found: {path}"
    content = path.read_text()
    assert "secrets-scan" in content or "detect-secrets" in content, "Missing secret scanning"
    return f"Size: {len(content)} bytes"

@test(".secrets.baseline exists", "P0-Secrets")
def test_secrets_baseline_exists():
    path = REPO_ROOT / ".secrets.baseline"
    assert path.exists(), f"File not found: {path}"
    content = json.loads(path.read_text())
    assert "plugins_used" in content, "Invalid baseline format"
    return f"Plugins: {len(content['plugins_used'])}"


# ============================================================================
# P1: ESM Baseline Store
# ============================================================================

@test("ESM store module exists", "P1-ESM-Store")
def test_esm_store_exists():
    path = REPO_ROOT / "src" / "store" / "esm_baseline.py"
    assert path.exists(), f"File not found: {path}"
    return f"Size: {path.stat().st_size} bytes"

@test("ESM store imports correctly", "P1-ESM-Store")
def test_esm_store_import():
    from src.store.esm_baseline import ESMBaselineStore
    return "Import successful"

@test("ESM store CRUD works", "P1-ESM-Store")
def test_esm_store_crud():
    import tempfile
    from src.store.esm_baseline import ESMBaselineStore
    
    db_path = os.path.join(tempfile.gettempdir(), f"test_esm_{datetime.now().timestamp()}.db")
    store = ESMBaselineStore(db_path)
    
    # Store a fingerprint
    record = store.store("test_session", [0.1] * 192, {"test": True})
    assert "curr_hash" in record, "Missing curr_hash"
    assert record["prev_hash"] == "GENESIS", f"First record should have GENESIS prev_hash"
    
    # Verify chain
    verify = store.verify_chain()
    assert verify["valid"], f"Chain should be valid: {verify}"
    assert verify["records"] == 1, f"Should have 1 record: {verify}"
    
    # Cleanup (ignore errors on Windows due to file locks)
    try:
        os.remove(db_path)
    except PermissionError:
        pass  # File will be cleaned up by OS temp cleanup
    return record


# ============================================================================
# P1: 192-Dimension SSG Fingerprint
# ============================================================================

@test("SSG runtime module exists", "P1-SSG-192")
def test_ssg_runtime_exists():
    path = REPO_ROOT / "src" / "core" / "ssg_runtime.py"
    assert path.exists(), f"File not found: {path}"
    return f"Size: {path.stat().st_size} bytes"

@test("SSG fingerprint is 192 dimensions", "P1-SSG-192")
def test_ssg_192_dims():
    from src.core.ssg import compute_ssg_fingerprint
    fp = compute_ssg_fingerprint("The quick brown fox jumps over the lazy dog.", n_bins=64)
    assert len(fp) == 192, f"Expected 192 dims, got {len(fp)}"
    return f"Shape: {fp.shape}, dtype: {fp.dtype}"

@test("SSG runtime comparison works", "P1-SSG-192")
def test_ssg_runtime_compare():
    from src.core.ssg_runtime import SSGFingerprintRuntime
    runtime = SSGFingerprintRuntime()
    
    similar1 = "The patient presents with symptoms of anxiety."
    similar2 = "A patient is showing signs of anxiety symptoms."
    different = "Hello world this is completely different."
    
    sim1 = runtime.compare(similar1, similar2)
    sim2 = runtime.compare(similar1, different)
    
    assert sim1["cosine_similarity"] > sim2["cosine_similarity"], \
        f"Similar texts should have higher sim: {sim1['cosine_similarity']} vs {sim2['cosine_similarity']}"
    
    return {"similar": sim1["cosine_similarity"], "different": sim2["cosine_similarity"]}


# ============================================================================
# P1: One-Command Reproducibility
# ============================================================================

@test("run_all.py exists", "P1-Repro")
def test_run_all_exists():
    path = REPO_ROOT / "run_all.py"
    assert path.exists(), f"File not found: {path}"
    return f"Size: {path.stat().st_size} bytes"


# ============================================================================
# P2: TruthfulQA Benchmark
# ============================================================================

@test("TruthfulQA report exists", "P2-TruthfulQA")
def test_truthfulqa_report_exists():
    path = REPO_ROOT / "benchmarks" / "truthfulqa_report.json"
    assert path.exists(), f"File not found: {path}"
    return f"Size: {path.stat().st_size} bytes"

@test("TruthfulQA accuracy >= 94%", "P2-TruthfulQA")
def test_truthfulqa_accuracy():
    path = REPO_ROOT / "benchmarks" / "truthfulqa_report.json"
    data = json.loads(path.read_text())
    accuracy = data.get("accuracy", 0)
    assert accuracy >= 94.0, f"Expected >= 94%, got {accuracy}%"
    return f"Accuracy: {accuracy}%, Passed: {data.get('passed')}/{data.get('total_questions')}"


# ============================================================================
# P2: PyPI Configuration
# ============================================================================

@test("pyproject.toml exists", "P2-PyPI")
def test_pyproject_exists():
    path = REPO_ROOT / "pyproject.toml"
    assert path.exists(), f"File not found: {path}"
    content = path.read_text()
    assert "[project]" in content, "Missing [project] section"
    assert "teletrust" in content, "Missing package name"
    return f"Size: {path.stat().st_size} bytes"

@test("pypi-release.yml has trusted publisher config", "P2-PyPI")
def test_pypi_workflow():
    path = REPO_ROOT / ".github" / "workflows" / "pypi-release.yml"
    assert path.exists(), f"File not found: {path}"
    content = path.read_text()
    assert "id-token: write" in content, "Missing OIDC permission"
    assert "pypa/gh-action-pypi-publish" in content, "Missing publish action"
    return "Trusted Publisher config present"


# ============================================================================
# Core Module Import Tests
# ============================================================================

@test("src.governance.moa_gate imports", "Core-Imports")
def test_import_moa_gate():
    from src.governance.moa_gate import MoaTokenGate
    return str(MoaTokenGate)

@test("src.core.ssg imports", "Core-Imports")
def test_import_ssg():
    from src.core.ssg import compute_ssg_fingerprint
    return str(compute_ssg_fingerprint)

@test("src.core.evaluate imports", "Core-Imports")
def test_import_evaluate():
    from src.core.evaluate import compute_quality
    return str(compute_quality)

@test("src.store.esm_baseline imports", "Core-Imports")
def test_import_esm_baseline():
    from src.store.esm_baseline import ESMBaselineStore
    return str(ESMBaselineStore)


# ============================================================================
# Run All Tests
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("COMPREHENSIVE DEBUG & VERIFICATION REPORT")
    print(f"Timestamp: {REPORT['timestamp']}")
    print(f"Repo: {REPORT['repo_root']}")
    print("=" * 70)
    print()
    
    # Run all tests
    test_nan_guard()
    test_inf_guard()
    test_normal_entropy()
    test_precommit_exists()
    test_security_workflow_exists()
    test_secrets_baseline_exists()
    test_esm_store_exists()
    test_esm_store_import()
    test_esm_store_crud()
    test_ssg_runtime_exists()
    test_ssg_192_dims()
    test_ssg_runtime_compare()
    test_run_all_exists()
    test_truthfulqa_report_exists()
    test_truthfulqa_accuracy()
    test_pyproject_exists()
    test_pypi_workflow()
    test_import_moa_gate()
    test_import_ssg()
    test_import_evaluate()
    test_import_esm_baseline()
    
    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ PASSED: {REPORT['summary']['passed']}")
    print(f"❌ FAILED: {REPORT['summary']['failed']}")
    print(f"💥 ERRORS: {REPORT['summary']['errors']}")
    print()
    
    # Save report
    report_path = REPO_ROOT / "debug_report.json"
    with open(report_path, "w") as f:
        # Convert non-serializable items
        serializable_report = {
            "timestamp": REPORT["timestamp"],
            "repo_root": REPORT["repo_root"],
            "summary": REPORT["summary"],
            "tests": [
                {"name": t["name"], "category": t["category"], "status": t["status"], 
                 "details": str(t["details"])[:500]}
                for t in REPORT["tests"]
            ]
        }
        json.dump(serializable_report, f, indent=2)
    print(f"Report saved to: {report_path}")
    
    # Exit code
    if REPORT["summary"]["failed"] > 0 or REPORT["summary"]["errors"] > 0:
        print("\n❌ VERIFICATION FAILED")
        sys.exit(1)
    else:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
