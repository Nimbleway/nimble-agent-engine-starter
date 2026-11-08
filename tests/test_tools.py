import json

from hello_world_agent.tools import register


class _App:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def add(fn):
            self.tools[fn.__name__] = fn
            return fn

        return add


def test_research_resume_without_agent_id_returns_error():
    app = _App()
    register(app)

    reply = json.loads(app.tools["nimble_research"](run_id="task_run_1"))

    assert "error" in reply
