import argparse
import sys
import subprocess
import os
import time
from pathlib import Path

# Configuration
REPO_ROOT = Path("moa_telehealth_governor").resolve()
SCRIPTS_DIR = REPO_ROOT / "scripts"
SRC_DIR = REPO_ROOT / "src"


def print_header(title):
    print("\n" + "=" * 60)
    print(f"TELETRUST CLI: {title}")
    print("=" * 60)


def check_requirements():
    """Ensure we are running in the right environment."""
    if not REPO_ROOT.exists():
        print(f"[ERROR] Repo root not found at {REPO_ROOT}")
        print("Please run this script from M:\\workspace")
        sys.exit(1)


def cmd_inventory(args):
    """List all available products and their status."""
    print_header("PRODUCT INVENTORY")
    products = [
        {
            "name": "Telehealth Citation Gateway",
            "type": "API Service",
            "status": "Ready",
            "path": "src/governor/telehealth_governor.py",
            "desc": "HIPAA-compliant regulatory lookup & consensus engine.",
        },
        {
            "name": "ESM Token Optimizer",
            "type": "CLI Tool",
            "status": "Ready",
            "path": "src/tools/esm_token_optimizer.py",
            "desc": "Spectral compression tool to reduce API costs by 30-50%.",
        },
        {
            "name": "TeleTrust Guard",
            "type": "Docker Container",
            "status": "Ready",
            "path": "Dockerfile",
            "desc": "Hardened container with PHI filtering and auditing.",
        },
        {
            "name": "Validator App",
            "type": "Desktop Utility",
            "status": "Ready",
            "path": "validator_app.py",
            "desc": "End-to-end proof generator (Scan -> Fix -> Prove).",
        },
    ]

    print(f"{'PRODUCT':<30} | {'TYPE':<15} | {'STATUS':<10}")
    print("-" * 65)
    for p in products:
        print(f"{p['name']:<30} | {p['type']:<15} | {p['status']:<10}")
        print(f"  > {p['desc']}")
        print(f"  > Location: {p['path']}\n")


def cmd_deploy_gateway(args):
    """Build and Run the Telehealth Gateway locally via Docker."""
    print_header("DEPLOYING GATEWAY (LOCAL)")

    # 1. Check Docker
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Docker is not installed or not in PATH.")
        return

    # 2. Build
    print("[1/3] Building Docker Image (teletrust-gateway)...")
    try:
        subprocess.run(
            ["docker", "build", "-t", "teletrust-gateway", "."],
            cwd=str(REPO_ROOT),
            check=True,
        )
    except subprocess.CalledProcessError:
        print("[ERROR] Docker build failed.")
        return

    # 3. Run
    print("[2/3] Starting Container on port 8000...")
    print("      (Press Ctrl+C to stop)")
    try:
        subprocess.run(
            [
                "docker",
                "run",
                "-it",
                "--rm",
                "-p",
                "8000:8000",
                "--env-file",
                ".env",
                "teletrust-gateway",
            ],
            cwd=str(REPO_ROOT),
        )
    except KeyboardInterrupt:
        print("\n[3/3] Stopping container...")


def cmd_run_optimizer(args):
    """Run the Token Optimizer on a file."""
    print_header("RUNNING TOKEN OPTIMIZER")
    input_file = Path(args.file).resolve()
    if not input_file.exists():
        print(f"[ERROR] Input file not found: {input_file}")
        return

    # Using the validator_app logic or calling the script directly
    # To keep it simple/robust, let's call the script directly if possible,
    # or import it if paths allow. Since we are in root workspace, path manipulation is needed.

    optimizer_script = SRC_DIR / "tools" / "esm_token_optimizer.py"

    # Construct python path to include src
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)

    # We can invoke it via python -m if we treat src as package,
    # but the script might not have a __main__ block for CLI args yet.
    # Actually, I verified earlier it DOES NOT have a CLI main block, it's a class.
    # So we should use a wrapper or the validator logic.

    print(f"[*] Compressing {input_file.name}...")

    # Inline wrapper execution
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from src.tools.esm_token_optimizer import ESMTokenOptimizer

        opt = ESMTokenOptimizer()
        text = input_file.read_text(encoding="utf-8")
        result = opt.compress(text, aggressive=True)

        print(f"Original:   {result.original_tokens} tokens")
        print(f"Compressed: {result.compressed_tokens} tokens")
        print(f"Savings:    {result.savings_percent:.2f}%")

        out_path = input_file.with_suffix(".optimized.txt")
        out_path.write_text(result.compressed_text, encoding="utf-8")
        print(f"Output saved to: {out_path}")

    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
    except Exception as e:
        print(f"[ERROR] Execution failed: {e}")


def cmd_validate(args):
    """Run the Validator App (Proof Generator)."""
    print_header("RUNNING VALIDATOR")
    target_file = args.file if args.file else "failed_audit.txt"

    validator_script = Path("validator_app.py").resolve()
    if not validator_script.exists():
        print("[ERROR] validator_app.py not found in current directory.")
        return

    cmd = [sys.executable, str(validator_script), target_file]
    subprocess.run(cmd)


def cmd_setup(args):
    """Run Setup Scripts (Billing, Secrets)."""
    print_header("SYSTEM SETUP")

    # 1. Secrets Scan
    print("[1/2] Scanning for Secrets...")
    scan_script = SCRIPTS_DIR / "secrets_scan.py"
    subprocess.run([sys.executable, str(scan_script)])

    # 2. Stripe Setup
    print("\n[2/2] Setting up Stripe Products...")
    stripe_script = SCRIPTS_DIR / "setup_stripe_products.py"
    if os.environ.get("STRIPE_SECRET_KEY"):
        subprocess.run([sys.executable, str(stripe_script)])
    else:
        print("[WARN] STRIPE_SECRET_KEY not found. Skipping Stripe setup.")


def main():
    parser = argparse.ArgumentParser(description="TeleTrust Ecosystem CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Inventory
    subparsers.add_parser("inventory", help="List all products and assets")

    # Deploy
    subparsers.add_parser("deploy", help="Deploy the Telehealth Gateway (Docker)")

    # Optimizer
    opt_parser = subparsers.add_parser("optimize", help="Run Token Optimizer")
    opt_parser.add_argument("file", help="Path to text file to compress")

    # Validator
    val_parser = subparsers.add_parser("validate", help="Run Validator/Proof Generator")
    val_parser.add_argument(
        "file", nargs="?", help="File to validate (default: failed_audit.txt)"
    )

    # Setup
    subparsers.add_parser("setup", help="Run security scan and billing setup")

    args = parser.parse_args()

    check_requirements()

    if args.command == "inventory":
        cmd_inventory(args)
    elif args.command == "deploy":
        cmd_deploy_gateway(args)
    elif args.command == "optimize":
        cmd_run_optimizer(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "setup":
        cmd_setup(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
