import io
from typing import List, Dict, Any


def plot_entropy_trace(
    audit_log: List[Dict[str, Any]], output_path: str = None
) -> bytes:
    """
    Generates a line chart of Spectral Entropy over time (steps).
    Returns the image bytes (PNG) or SVG string bytes.
    """
    steps = []
    entropies = []

    for entry in audit_log:
        step = entry.get("step", 0)
        val = entry.get("entropy", 0.0)
        steps.append(step)
        entropies.append(val)

    # Try Matplotlib first
    try:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 4))
        plt.plot(steps, entropies, marker="o", linestyle="-", color="#2c3e50")
        plt.title("Spectral Entropy Trace (Hallucination Risk)")
        plt.xlabel("Interaction Step")
        plt.ylabel("Entropy (bits)")
        plt.axhline(y=5.5, color="r", linestyle="--", label="High Risk Threshold")
        plt.axhline(y=2.0, color="g", linestyle="--", label="Bot/Repetition Threshold")
        plt.legend()
        plt.grid(True, alpha=0.3)
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png", bbox_inches="tight")
        plt.close()
        img_bytes = img_buffer.getvalue()

    except ImportError:
        # Fallback: Generate SVG manually
        print("[INFO] Matplotlib missing. Generating SVG graph.")
        width = 800
        height = 400
        margin = 50

        if not steps:
            return b""

        min_x, max_x = min(steps), max(steps)
        min_y, max_y = 0, 7  # Fixed scale for entropy (usually 0-6 bits)

        def map_x(x):
            return margin + (x - min_x) / max((max_x - min_x), 1) * (width - 2 * margin)

        def map_y(y):
            return (
                height
                - margin
                - (y - min_y) / max((max_y - min_y), 1) * (height - 2 * margin)
            )

        points = []
        for x, y in zip(steps, entropies):
            points.append(f"{map_x(x)},{map_y(y)}")

        polyline = " ".join(points)

        # Simple SVG template
        svg = f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f8f9fa"/>
            <text x="{width / 2}" y="30" font-family="Arial" font-size="20" text-anchor="middle">Spectral Entropy Trace (Hallucination Risk)</text>

            <!-- Grid lines -->
            <line x1="{margin}" y1="{map_y(5.5)}" x2="{width - margin}" y2="{map_y(5.5)}" stroke="red" stroke-dasharray="5,5" stroke-width="2"/>
            <text x="{width - margin + 5}" y="{map_y(5.5)}" fill="red" font-family="Arial" font-size="12">High Risk (5.5)</text>

            <line x1="{margin}" y1="{map_y(2.0)}" x2="{width - margin}" y2="{map_y(2.0)}" stroke="green" stroke-dasharray="5,5" stroke-width="2"/>
            <text x="{width - margin + 5}" y="{map_y(2.0)}" fill="green" font-family="Arial" font-size="12">Bot (2.0)</text>

            <!-- Axes -->
            <line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="black" stroke-width="2"/>
            <line x1="{margin}" y1="{height - margin}" x2="{margin}" y2="{margin}" stroke="black" stroke-width="2"/>

            <!-- Data -->
            <polyline points="{polyline}" fill="none" stroke="#2c3e50" stroke-width="3"/>

            <!-- Points -->
            {"".join([f'<circle cx="{map_x(x)}" cy="{map_y(y)}" r="4" fill="#2c3e50"/>' for x, y in zip(steps, entropies)])}
        </svg>
        """
        img_bytes = svg.encode("utf-8")

        # Ensure output extension is correct if path provided
        if output_path and output_path.endswith(".png"):
            output_path = output_path.replace(".png", ".svg")

    if output_path:
        with open(output_path, "wb") as f:
            f.write(img_bytes)

    return img_bytes
