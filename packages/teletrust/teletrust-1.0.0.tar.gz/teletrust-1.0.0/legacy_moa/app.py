"""
Streamlit UI for MCP-enhanced regulatory evaluation.
Wires PHI-safe evaluator with real-time regulatory verification.
"""

import streamlit as st

from regulatory_mcp_client import RegulatoryMCPClient, run_mcp_tool
from mcp_enhanced_evaluator import PHISafeEvaluator


# ============================================================================
# Initialization
# ============================================================================

@st.cache_resource
def init_evaluator():
    """Initialize a PHI-safe evaluator with dummy MCP client."""
    dummy_client = None
    return PHISafeEvaluator(dummy_client, α=0.7)


evaluator = init_evaluator()


# ============================================================================
# Evaluation wrapper
# ============================================================================

def evaluate_text(text: str, mode: str, jurisdiction: str = "CA"):
    """Trigger evaluation with mathematical core + MCP verification."""

    async def run_evaluation():
        async with RegulatoryMCPClient() as mcp:
            evaluator.mcp_client = mcp
            result = evaluator.evaluate(text, mode, jurisdiction)
            return result

    with st.spinner("Evaluating with real-time regulatory verification..."):
        result = run_mcp_tool(run_evaluation())
    return result


# ============================================================================
# UI
# ============================================================================

st.title("Mike's Way Editor – MCP Regulatory Gateway")

mode = st.selectbox("Mode", ["clinical", "academic"])
jurisdiction = st.text_input("Jurisdiction (state code)", value="CA")
text_input = st.text_area("Enter text to evaluate:", height=200)

if st.button("Evaluate"):
    if not text_input.strip():
        st.warning("Please enter some text first.")
    else:
        result = evaluate_text(text_input, mode, jurisdiction)

        # Clinical mode returns minimal output
        if mode == "clinical":
            st.subheader("Clinical Compliance Summary")
            st.metric("Risk level", result["risk_level"])
            st.metric("Quality (Q)", f"{result['Q']:.3f}")
            st.metric("Distance (D)", f"{result['distance']:.3f}")

            st.write(
                f"Consent complete: {'✅' if result['consent_complete'] else '❌'}"
            )
            st.write(
                f"Regulations verified: {'✅' if result['regulations_verified'] else '❌'}"
            )
            st.sidebar.success("🔒 PHI safety active – no patient data sent to APIs")

        else:
            # Academic mode returns full structure
            st.subheader("Quality Scores")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Quality (Q)", f"{result['Q']:.3f}")
                st.metric("Distance (D)", f"{result['D']:.3f}")

                if result["D"] < 0.2:
                    st.success("✅ Acceptable quality")
                elif result["D"] < 0.5:
                    st.warning("⚠️ Needs revision")
                else:
                    st.error("❌ Significant issues")

            with col2:
                st.metric("Rule score (static)", f"{result['S_rule_static']:.3f}")
                st.metric("Rule score (MCP)", f"{result['S_rule_mcp']:.3f}")
                st.metric("Vector similarity", f"{result['S_vec']:.3f}")

            with st.expander("🔍 Real-time regulatory verification"):
                st.markdown("### What was checked")
                st.markdown(
                    f"- **Billing codes:** {result.get('verified_codes', 'None found')}"
                )
                st.markdown(
                    f"- **Legislation:** {result.get('verified_bills', 'None found')}"
                )
                st.markdown(
                    f"- **Federal regs (CFR):** {result.get('verified_cfr', 'None found')}"
                )

            st.sidebar.info("Academic mode: PHI rules still apply if you paste notes.")
