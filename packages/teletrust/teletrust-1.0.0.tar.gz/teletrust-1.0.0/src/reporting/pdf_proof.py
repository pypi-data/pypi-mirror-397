from pathlib import Path
from typing import List, Dict, Any
import datetime


# Mock PDF generator if ReportLab is missing
def generate_audit_proof(
    output_path: Path, audit_data: Dict[str, Any], graph_image: bytes = None
) -> None:
    """
    Generates a legal-grade Audit Proof (Markdown fallback if no ReportLab).
    Includes: Timestamp, Session ID, Hash Chain, Verdict, and Entropy Graph reference.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Try using ReportLab first
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.utils import ImageReader
        import io

        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, "TeleTrust Audit Proof")

        c.setFont("Helvetica", 10)
        c.drawString(
            72, height - 90, f"Generated: {datetime.datetime.utcnow().isoformat()}Z"
        )
        c.drawString(
            72, height - 104, f"Session ID: {audit_data.get('session_id', 'UNKNOWN')}"
        )

        y = height - 140

        # Verdict Section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, "Compliance Verdict")
        y -= 20

        verdict = audit_data.get("verdict", "UNKNOWN")
        c.setFont("Helvetica", 12)
        if verdict == "ALLOW":
            c.setFillColor(colors.green)
        else:
            c.setFillColor(colors.red)
        c.drawString(72, y, verdict)
        c.setFillColor(colors.black)
        y -= 30

        # Hash Chain Evidence
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, "Cryptographic Evidence (SHA-256)")
        y -= 20
        c.setFont("Courier", 9)
        c.drawString(72, y, f"Previous Hash: {audit_data.get('prev_hash', 'GENESIS')}")
        y -= 14
        c.drawString(72, y, f"Current Hash:  {audit_data.get('hash', 'PENDING')}")
        y -= 30

        # Entropy Graph
        if graph_image:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(72, y, "Spectral Entropy Analysis")
            y -= 150

            img = ImageReader(io.BytesIO(graph_image))
            c.drawImage(img, 72, y, width=400, height=130)
            y -= 20

        # Audit Log Details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, "Action Log")
        y -= 20
        c.setFont("Helvetica", 9)

        logs = audit_data.get("logs", [])
        for line in logs:
            if y < 72:
                c.showPage()
                y = height - 72
                c.setFont("Helvetica", 9)

            clean_line = str(line).replace("\n", " ")
            while len(clean_line) > 90:
                c.drawString(72, y, clean_line[:90])
                clean_line = clean_line[90:]
                y -= 12
            c.drawString(72, y, clean_line)
            y -= 12

        c.save()
        return

    except ImportError:
        # Fallback to Markdown Report
        md_path = output_path.with_suffix(".md")
        print(f"    [!] ReportLab missing. Generating Markdown Proof: {md_path}")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# TeleTrust Audit Proof\n\n")
            f.write(f"**Generated:** {datetime.datetime.utcnow().isoformat()}Z  \n")
            f.write(f"**Session ID:** {audit_data.get('session_id', 'UNKNOWN')}  \n\n")

            verdict = audit_data.get("verdict", "UNKNOWN")
            color = "🟢" if verdict == "ALLOW" else "🔴"
            f.write(f"## Compliance Verdict: {color} {verdict}\n\n")

            f.write("## Cryptographic Evidence (SHA-256)\n")
            f.write(
                f"- **Previous Hash:** `{audit_data.get('prev_hash', 'GENESIS')}`\n"
            )
            f.write(f"- **Current Hash:** `{audit_data.get('hash', 'PENDING')}`\n\n")

            if graph_image:
                f.write("## Spectral Entropy Analysis\n")
                f.write("*(Graph image saved separately as entropy_trace.png)*\n\n")

            f.write("## Action Log\n")
            for line in audit_data.get("logs", []):
                f.write(f"- {line}\n")
