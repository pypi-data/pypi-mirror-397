"""
Async MCP client wrapper for regulatory verification.
Handles tool invocations to regulatory_mcp_server.
"""

import asyncio
from typing import Any, Dict, Optional


class RegulatoryMCPClient:
    """
    Async context manager around MCP server.
    Replace internal calls with real MCP tool invocations.
    """

    def __init__(self):
        self._client = None

    async def __aenter__(self):
        # TODO: create real MCP connection here
        # self._client = await mcp.connect(...)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # TODO: cleanly close MCP connection
        # await self._client.aclose()
        self._client = None

    async def _call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict:
        """Core invocation. Replace with actual MCP call."""
        # Example with a hypothetical MCP client:
        # response = await self._client.call_tool(tool_name, args)
        # return response or {}
        raise NotImplementedError("Wire this to regulatory_mcp_server MCP tools")

    async def lookup_billing_code(
        self,
        code_type: str,
        code: str,
    ) -> Dict:
        """Verify billing code exists in official database."""
        return await self._call_tool(
            "lookup_billing_code",
            {"code_type": code_type, "code": code},
        )

    async def check_state_bill_status(
        self,
        jurisdiction: str,
        bill_id: str,
    ) -> Dict:
        """Check if state bill is signed into law."""
        return await self._call_tool(
            "check_state_bill_status",
            {"jurisdiction": jurisdiction, "bill_id": bill_id},
        )

    async def search_federal_regulations(
        self,
        title: str,
        part: str,
        section: Optional[str] = None,
    ) -> Dict:
        """Search eCFR for regulation text."""
        payload: Dict[str, Any] = {"title": title, "part": part}
        if section is not None:
            payload["section"] = section
        return await self._call_tool(
            "search_federal_regulations",
            payload,
        )


def run_mcp_tool(coro):
    """Run an async MCP workflow from sync Streamlit code."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        return asyncio.run(coro)

    return loop.run_until_complete(coro)
