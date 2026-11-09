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


def test_research_accepts_effort_and_agent_name():
    app = _App()
    register(app)

    fn = app.tools["nimble_research"]
    import inspect

    sig = inspect.signature(fn)
    assert "effort" in sig.parameters
    assert "agent_name" in sig.parameters
    assert sig.parameters["effort"].default == "low"
    assert sig.parameters["agent_name"].default == ""
