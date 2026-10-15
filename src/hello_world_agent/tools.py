"""Nimble Web Search Agent tool. Search and extract come from Nimble's MCP server."""

from __future__ import annotations

import json
import os
import time

import httpx
from agent_engine_sdk_langgraph import App

NIMBLE = "https://sdk.nimbleway.com/v2/agents"
WAIT_SECONDS = 20  # leaves headroom inside the 30-second tool timeout


def register(app: App) -> None:
    @app.tool()
    def research(question: str = "", run_id: str = "", agent_id: str = "") -> str:
        """Research a question on the live web with a Nimble Web Search Agent.

        Returns a cited answer. If the reply has status "running", call again
        with its run_id and agent_id to keep waiting.
        """
        deadline = time.monotonic() + WAIT_SECONDS
        headers = {
            "Authorization": f"Bearer {os.environ['NIMBLE_API_KEY']}",
            "X-Client-Source": "mongodb-atlas-agent-engine",
        }
        try:
            with httpx.Client(headers=headers, timeout=10) as http:
                if not run_id:
                    if not question:
                        return json.dumps({"error": "question is required"})
                    run = http.post(f"{NIMBLE}/runs", json={"input": question, "effort": "low"})
                    run.raise_for_status()
                    run_id, agent_id = run.json()["id"], run.json()["web_search_agent_id"]
                while time.monotonic() < deadline:
                    status = http.get(f"{NIMBLE}/{agent_id}/runs/{run_id}")
                    status.raise_for_status()
                    state = status.json()["status"]
                    if state == "completed":
                        result = http.get(f"{NIMBLE}/{agent_id}/runs/{run_id}/result")
                        result.raise_for_status()
                        return result.text
                    if state in ("failed", "cancelled"):
                        error = status.json().get("error")
                        return json.dumps({"error": f"run {state}", "details": error})
                    time.sleep(5)
        except httpx.HTTPError as e:
            return json.dumps({"error": str(e)})
        return json.dumps({"status": "running", "run_id": run_id, "agent_id": agent_id})
