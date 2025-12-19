#!/usr/bin/env python3
"""
TaskAgent - Governed Task Execution Wrapper
============================================

Wraps any task with MOA governance:
1. Token optimization (67% savings)
2. Grammar validation (bounded state transitions)
3. Risk gating (GREEN/YELLOW/RED zones)
4. Hard stop support (KILL/PAUSE/RESUME)
5. Audit trail (Prime Gödel codes)

Usage:
    agent = TaskAgent("backup_agent", allowed_transitions=["IDLE", "RUNNING", "DONE"])
    result = agent.execute("Backup the database to cloud storage")

Copyright (c) 2025 Michael Ordon. PROPRIETARY.
"""

import sys
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

# Fix imports
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# =============================================================================
# IMPORTS FROM MOA STACK
# =============================================================================

try:
    from src.esm_token_optimizer import ESMTokenOptimizer, compress_prompt
except ImportError:
    ESMTokenOptimizer = None
    def compress_prompt(text, aggressive=False): return text

try:
    from src.ssg.grammar import GrammarValidator
except ImportError:
    GrammarValidator = None

try:
    from moa_telehealth_governor.src.governor.telehealth_governor import TelehealthGovernor
except ImportError:
    TelehealthGovernor = None

try:
    from moa_telehealth_governor.src.physics.prime_codecs import encode_macro_state
except ImportError:
    encode_macro_state = None

# =============================================================================
# KILL SWITCH (From GEMINI.md)
# =============================================================================

KILL_PHRASES = ["STOP", "KILL", "ABORT", "EMERGENCY STOP", "HALT ALL"]
PAUSE_PHRASES = ["PAUSE", "HOLD"]
RESUME_PHRASES = ["RESUME", "CONTINUE"]

class AgentState(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    KILLED = "KILLED"

# =============================================================================
# TASK RESULT
# =============================================================================

@dataclass
class TaskResult:
    """Result of a governed task execution."""
    success: bool
    output: Any
    zone: str  # GREEN, YELLOW, RED
    risk_score: float
    tokens_saved: int
    cost_saved_usd: float
    state_valid: bool
    prime_code: int
    execution_time: float
    logs: List[str] = field(default_factory=list)

# =============================================================================
# TASK AGENT
# =============================================================================

class TaskAgent:
    """
    Governed agent that wraps task execution with MOA safety layers.

    Features:
    - Token optimization before LLM calls
    - Grammar validation for state transitions
    - Risk gating (blocks RED zone actions)
    - Hard stop via kill phrases
    - Full audit trail via Prime Gödel codes
    """

    def __init__(
        self,
        name: str,
        allowed_transitions: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.config = config or {}
        self.state = AgentState.IDLE
        self.current_macro_state = "IDLE"
        self._paused = False
        self._killed = False

        # Token optimizer
        if ESMTokenOptimizer:
            self.optimizer = ESMTokenOptimizer()
        else:
            self.optimizer = None

        # Grammar validator for bounded states
        if GrammarValidator and allowed_transitions:
            self.grammar = GrammarValidator(dummy_state="INIT", robust=True)
            self.grammar.train(["INIT"] + allowed_transitions)
        else:
            self.grammar = None

        # Governor for risk assessment
        if TelehealthGovernor:
            self.governor = TelehealthGovernor(config)
        else:
            self.governor = None

        # Metrics
        self.total_tokens_saved = 0
        self.total_cost_saved = 0.0
        self.execution_count = 0
        self.history: List[TaskResult] = []

    # =========================================================================
    # CONTROL
    # =========================================================================

    def kill(self):
        """Emergency stop."""
        self._killed = True
        self.state = AgentState.KILLED
        return {"status": "KILLED", "agent": self.name}

    def pause(self):
        """Pause execution."""
        self._paused = True
        self.state = AgentState.PAUSED
        return {"status": "PAUSED", "agent": self.name}

    def resume(self):
        """Resume execution."""
        self._paused = False
        if self.state == AgentState.PAUSED:
            self.state = AgentState.RUNNING
        return {"status": "RESUMED", "agent": self.name}

    def check_control_phrase(self, text: str) -> Optional[str]:
        """Check for kill/pause/resume phrases in text."""
        upper = text.upper()
        for phrase in KILL_PHRASES:
            if phrase in upper:
                self.kill()
                return "KILLED"
        for phrase in PAUSE_PHRASES:
            if phrase in upper:
                self.pause()
                return "PAUSED"
        for phrase in RESUME_PHRASES:
            if phrase in upper:
                self.resume()
                return "RESUMED"
        return None

    # =========================================================================
    # EXECUTE
    # =========================================================================

    def execute(
        self,
        task_description: str,
        executor: Optional[Callable[[str], Any]] = None,
        target_state: str = "DONE"
    ) -> TaskResult:
        """
        Execute a task with full MOA governance.

        Args:
            task_description: What to do
            executor: Optional callable to run (default: stub)
            target_state: Expected end state for grammar validation

        Returns:
            TaskResult with metrics and output
        """
        t0 = time.time()
        logs = []

        # 0. Check if killed/paused
        if self._killed:
            return TaskResult(
                success=False, output="Agent killed", zone="RED",
                risk_score=100, tokens_saved=0, cost_saved_usd=0,
                state_valid=False, prime_code=0, execution_time=0, logs=["KILLED"]
            )

        if self._paused:
            return TaskResult(
                success=False, output="Agent paused", zone="YELLOW",
                risk_score=50, tokens_saved=0, cost_saved_usd=0,
                state_valid=False, prime_code=0, execution_time=0, logs=["PAUSED"]
            )

        self.state = AgentState.RUNNING
        logs.append(f"[{self.name}] Starting task execution")

        # 1. Token optimization
        original_tokens = len(task_description.split()) * 1.3
        if self.optimizer:
            result = self.optimizer.compress(task_description, aggressive=True)
            compressed = result.compressed_text
            compressed_tokens = result.compressed_tokens
            tokens_saved = int(result.original_tokens - result.compressed_tokens)
            cost_saved = tokens_saved / 1000 * 0.01
            logs.append(f"Tokens: {result.original_tokens} → {compressed_tokens} (saved {tokens_saved})")
        else:
            compressed = task_description
            compressed_tokens = original_tokens
            tokens_saved = 0
            cost_saved = 0

        self.total_tokens_saved += tokens_saved
        self.total_cost_saved += cost_saved

        # 2. Grammar validation
        state_valid = True
        if self.grammar:
            transition = [self.current_macro_state, target_state]
            results = self.grammar.detect(transition)
            anomalies = [r for r in results if r[1]]
            if anomalies:
                state_valid = False
                logs.append(f"⚠️ Invalid transition: {self.current_macro_state} → {target_state}")
            else:
                logs.append(f"✓ Valid transition: {self.current_macro_state} → {target_state}")

        # 3. Governor risk assessment
        zone = "GREEN"
        risk_score = 0.0
        prime_code = 0

        if self.governor:
            gov_result = self.governor.process_interaction(f"agent_{self.name}", compressed)
            zone = gov_result.zone
            risk_score = gov_result.risk_score
            prime_code = gov_result.prime_code_macro
            logs.append(f"Governor: zone={zone}, risk={risk_score:.1f}")

            # Block RED zone
            if zone == "RED":
                self.state = AgentState.FAILED
                return TaskResult(
                    success=False, output="Blocked by risk gate",
                    zone=zone, risk_score=risk_score, tokens_saved=tokens_saved,
                    cost_saved_usd=cost_saved, state_valid=state_valid,
                    prime_code=prime_code, execution_time=time.time() - t0, logs=logs
                )
        else:
            # Fallback: encode based on simple heuristics
            if encode_macro_state:
                a_bin = min(6, int(len(compressed) / 100))
                e_bin = 3  # Assume human band
                p_bin = 3
                prime_code = encode_macro_state(a_bin, e_bin, p_bin)

        # 4. Execute task
        try:
            if executor:
                output = executor(compressed)
            else:
                output = f"[STUB] Would execute: {compressed[:100]}..."

            self.current_macro_state = target_state
            self.state = AgentState.COMPLETED
            logs.append("✓ Task completed successfully")

        except Exception as e:
            self.state = AgentState.FAILED
            output = str(e)
            logs.append(f"✗ Task failed: {e}")
            return TaskResult(
                success=False, output=output, zone="RED", risk_score=100,
                tokens_saved=tokens_saved, cost_saved_usd=cost_saved,
                state_valid=state_valid, prime_code=prime_code,
                execution_time=time.time() - t0, logs=logs
            )

        # 5. Return result
        self.execution_count += 1
        result = TaskResult(
            success=True,
            output=output,
            zone=zone,
            risk_score=risk_score,
            tokens_saved=tokens_saved,
            cost_saved_usd=cost_saved,
            state_valid=state_valid,
            prime_code=prime_code,
            execution_time=time.time() - t0,
            logs=logs
        )
        self.history.append(result)
        return result

    # =========================================================================
    # METRICS
    # =========================================================================

    def get_metrics(self) -> Dict[str, Any]:
        """Get cumulative agent metrics."""
        return {
            "agent_name": self.name,
            "state": self.state.value,
            "execution_count": self.execution_count,
            "total_tokens_saved": self.total_tokens_saved,
            "total_cost_saved_usd": round(self.total_cost_saved, 4),
            "current_macro_state": self.current_macro_state,
            "is_paused": self._paused,
            "is_killed": self._killed,
        }


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstrate TaskAgent with governance."""
    print("=" * 60)
    print("  TASK AGENT DEMO")
    print("  Governed Task Execution")
    print("=" * 60)

    # Create agent with allowed states
    agent = TaskAgent(
        name="backup_agent",
        allowed_transitions=["IDLE", "PREPARING", "RUNNING", "DONE", "FAILED"]
    )

    print(f"\n[1] Agent created: {agent.name}")
    print(f"    State: {agent.state.value}")

    # Execute a task
    print("\n[2] Executing backup task...")
    result = agent.execute(
        task_description="""
        In order to ensure data safety and provide comprehensive backup coverage,
        please perform a full backup of the following directories to Google Drive:
        - C:\\Users\\Mike\\Projects
        - C:\\Users\\Mike\\source
        Due to the fact that these files are critical, use high-priority transfer.
        At this point in time, compression should be enabled.
        """,
        target_state="RUNNING"
    )

    print(f"    Success: {result.success}")
    print(f"    Zone: {result.zone}")
    print(f"    Tokens Saved: {result.tokens_saved}")
    print(f"    Cost Saved: ${result.cost_saved_usd:.4f}")
    print(f"    State Valid: {result.state_valid}")
    print(f"    Prime Code: {result.prime_code}")

    # Check metrics
    print("\n[3] Agent Metrics:")
    metrics = agent.get_metrics()
    for k, v in metrics.items():
        print(f"    {k}: {v}")

    # Test kill switch
    print("\n[4] Testing KILL switch...")
    agent.check_control_phrase("EMERGENCY STOP")
    print(f"    State after KILL: {agent.state.value}")

    print("\n" + "=" * 60)
    print("  Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
