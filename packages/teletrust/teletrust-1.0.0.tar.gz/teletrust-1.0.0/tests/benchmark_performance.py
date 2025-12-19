import time
import sys
import os
import json
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

# Ensure we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.moa_telehealth import govern, GovernanceResult

class BenchmarkResult:
    def __init__(self):
        self.latencies: List[float] = []
        self.success_count = 0
        self.fail_count = 0
        self.start_time = 0.0
        self.end_time = 0.0

def run_single_request(session_id: str, input_text: str) -> bool:
    try:
        res = govern(session_id, input_text)
        return res.zone in ["GREEN", "YELLOW", "RED"]
    except Exception as e:
        print(f"Error: {e}")
        return False

def benchmark_governance(
    num_requests: int = 100,
    concurrency: int = 1,
    label: str = "Baseline"
) -> Dict[str, float]:
    print(f"--- Benchmark: {label} (n={num_requests}, threads={concurrency}) ---")

    executor = ThreadPoolExecutor(max_workers=concurrency)
    futures = []

    result = BenchmarkResult()
    result.start_time = time.time()

    # Pre-generate inputs to avoid generation cost in loop
    inputs = [
        (f"sess_{i}_{time.time()}", f"Patient reports symptom {i}. Check vitals.")
        for i in range(num_requests)
    ]

    def wrapped_req(idx):
        t0 = time.time()
        success = run_single_request(inputs[idx][0], inputs[idx][1])
        lat = time.time() - t0
        return success, lat

    for i in range(num_requests):
        futures.append(executor.submit(wrapped_req, i))

    for f in futures:
        success, lat = f.result()
        if success:
            result.success_count += 1
            result.latencies.append(lat)
        else:
            result.fail_count += 1

    result.end_time = time.time()
    total_time = result.end_time - result.start_time

    stats = {
        "total_requests": num_requests,
        "concurrency": concurrency,
        "duration_sec": total_time,
        "throughput_rps": num_requests / total_time,
        "success_rate": result.success_count / num_requests,
        "latency_p50": statistics.median(result.latencies) if result.latencies else 0,
        "latency_p95": statistics.quantiles(result.latencies, n=20)[18] if len(result.latencies) >= 20 else 0,
        "latency_p99": statistics.quantiles(result.latencies, n=100)[98] if len(result.latencies) >= 100 else 0,
        "latency_max": max(result.latencies) if result.latencies else 0,
        "ledger_integrity": verify_ledger_integrity()
    }

    print(f"Results for {label}:")
    print(f"  Throughput: {stats['throughput_rps']:.2f} req/sec")
    print(f"  Latency p50: {stats['latency_p50']*1000:.2f} ms")
    print(f"  Latency p99: {stats['latency_p99']*1000:.2f} ms")
    print(f"  Success Rate: {stats['success_rate']*100:.1f}%")
    print(f"  Ledger Integrity: {'PASS' if stats['ledger_integrity'] else 'FAIL'}")
    print("-" * 40)

    return stats

def verify_ledger_integrity() -> bool:
    from src.billing.moa_usage_ledger import MoaUsageLedger
    ledger = MoaUsageLedger()
    return ledger.verify_integrity()

if __name__ == "__main__":
    # Ensure usage_ledger.jsonl is cleanish for test
    if os.path.exists("usage_ledger.jsonl"):
        os.rename("usage_ledger.jsonl", f"usage_ledger.jsonl.bak.{time.time()}")

    # Warmup
    print("Warming up...")
    govern("warmup", "warmup")

    # 1. Sequential Baseline
    stats_seq = benchmark_governance(num_requests=50, concurrency=1, label="Sequential")

    # 2. Concurrent Load
    stats_conc = benchmark_governance(num_requests=100, concurrency=10, label="Concurrent (10 threads)")

    # 3. Burst Load (simulating spike)
    stats_burst = benchmark_governance(num_requests=200, concurrency=25, label="Burst (25 threads)")

    # Save results
    with open("benchmark_results.json", "w") as f:
        json.dump({
            "sequential": stats_seq,
            "concurrent": stats_conc,
            "burst": stats_burst,
            "timestamp": time.time()
        }, f, indent=2)
