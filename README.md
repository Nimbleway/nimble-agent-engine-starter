# Nimble Web Agent for Atlas Agent Engine

Give your [Atlas Agent Engine](https://www.mongodb.com/docs/agentengine/) agent live web data from Nimble.

This starter agent searches the web, reads pages and runs multi-step web research with [Nimble](https://nimbleway.com), and cites its sources. It is built from MongoDB's [`hello-world-agent`](https://github.com/mongodb/agent-engine-examples/tree/main/templates/hello-world-agent) template (Apache-2.0) and modified to add Nimble.

## What it uses

Three tools in `src/hello_world_agent/tools.py`, built on the [Nimble Python SDK](https://pypi.org/project/nimble-python/):

- `nimble_search`: search the live web.
- `nimble_extract`: read a page as markdown.
- `nimble_research`: run a Nimble Web Search Agent and wait for the cited answer.

Prefer MCP? `agent.yaml` has a commented block that uses Nimble's hosted [MCP server](https://docs.nimbleway.com/integrations/mcp-server/mcp-server) for search and extract instead.

## Run locally

You need the [`agentengine` CLI](https://www.mongodb.com/docs/agentengine/build/install-authenticate/), Docker, a [Nimble API key](https://online.nimbleway.com/signup) and an OpenAI key.

```bash
cp env.example .env   # set LLM_API_KEY and NIMBLE_API_KEY
agentengine dev up
```

Open the playground at `http://localhost:3000` and try:

- "What are the latest announcements about MongoDB Atlas?"
- "Summarize https://www.mongodb.com/docs/agentengine/"
- "Research the top three open-source vector databases and compare their licenses."

Stop with `agentengine dev down`.

To use another LLM provider, change the client in `src/hello_world_agent/llm.py` and its host in the `egress` list in `agent.yaml`.

## Deploy

Deploying needs the Project Owner role.

```bash
agentengine init
agentengine secret set LLM_API_KEY --workspace-scope
agentengine secret set NIMBLE_API_KEY --workspace-scope
agentengine build
agentengine deploy
```

## Good to know

- Use a dedicated Nimble API key with a credit limit for this agent. See [pricing](https://nimbleway.com/pricing).
- The agent can only reach the hosts listed under `egress` in `agent.yaml`.
- Atlas Agent Engine is in public preview and may change.

## License

Apache-2.0. Use of the Atlas Agent Engine software is governed by MongoDB's [license agreement](https://github.com/mongodb/agent-engine-examples/blob/main/LICENSE).
