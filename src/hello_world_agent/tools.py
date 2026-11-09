"""Nimble web tools: search, extract and Nimble Agent research."""

from __future__ import annotations

import json
import os
import time

from agent_engine_sdk_langgraph import App
from nimble_python import APIError, Nimble

WAIT_SECONDS = 20  # leaves headroom inside the 30-second tool timeout
MAX_PAGE_CHARS = 20_000


def _client() -> Nimble:
    return Nimble(
        api_key=os.environ["NIMBLE_API_KEY"],
        client_source="mongodb-atlas-agent-engine",
        timeout=25,  # one call must finish inside the 30-second tool timeout
        max_retries=0,
    )


def register(app: App) -> None:
    @app.tool()
    def nimble_search(query: str) -> str:
        """Search the live web. Returns titles, URLs and snippets."""
        try:
            response = _client().search(query=query, max_results=5)
        except APIError as e:
            return json.dumps({"error": str(e)})
        results = [
            {"title": r.title, "url": r.url, "snippet": r.description} for r in response.results
        ]
        return json.dumps(results)

    @app.tool()
    def nimble_extract(url: str) -> str:
        """Read a web page and return its content as markdown."""
        try:
            response = _client().extract.run(url=url, formats=["markdown"])
        except APIError as e:
            return json.dumps({"error": str(e)})
        return (response.data.markdown or "")[:MAX_PAGE_CHARS]

    @app.tool()
    def nimble_research(
        question: str = "",
        run_id: str = "",
        agent_id: str = "",
        effort: str = "low",
        agent_name: str = "",
    ) -> str:
        """Research a question on the live web with a Nimble Agent.

        Returns a cited answer. If the reply has status "running", call again
        with its run_id and agent_id to keep waiting.

        Args:
            question: The research question.
            run_id: Run ID from a previous "running" reply, to resume polling.
            agent_id: Agent ID from a previous "running" reply.
            effort: How deep the research goes. One of low, medium, high,
                x-high, max. Defaults to low (about 1 minute).
            agent_name: Optional name to reuse a persistent agent across calls.
                All callers sharing the same API key and name share the agent's
                memory. Scope the name per user in multi-tenant deployments.
        """
        if run_id and not agent_id:
            return json.dumps({"error": "pass both run_id and agent_id from the running reply"})
        deadline = time.monotonic() + WAIT_SECONDS
        client = _client()
        try:
            if not run_id:
                if not question:
                    return json.dumps({"error": "question is required"})
                kwargs: dict = {"input": question, "effort": effort}
                if agent_name:
                    kwargs["agent_name"] = agent_name
                run = client.agents.run(**kwargs)
                run_id, agent_id = run.id, run.web_search_agent_id
            while time.monotonic() < deadline:
                run = client.agents.runs.get(run_id, agent_id=agent_id)
                if run.status == "completed":
                    result = client.agents.runs.result(run_id, agent_id=agent_id)
                    return result.model_dump_json(warnings=False)
                if run.status in ("failed", "cancelled"):
                    return json.dumps({"error": f"run {run.status}", "details": str(run.error)})
                time.sleep(5)
        except APIError as e:
            return json.dumps({"error": str(e)})
        return json.dumps({"status": "running", "run_id": run_id, "agent_id": agent_id})
