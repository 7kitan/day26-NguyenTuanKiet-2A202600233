# Legal Multi-Agent Lab — Marker's Guide

This project is a legal advisory system built with LangGraph and Google's A2A protocol. It progresses through five stages from a simple LLM call to a fully distributed multi-agent network.

See `ARCHITECTURE.md` for the full system design and `CODELAB_REPORT.md` for all lab answers and observations.

## What Was Done

All five stages were completed and tested using DeepSeek Chat via OpenRouter.

- Stage 1 runs a direct LLM call with no tools or memory.
- Stage 2 adds a legal knowledge base and tool calling with manual orchestration.
- Stage 3 wraps the LLM and tools in an autonomous ReAct agent.
- Stage 4 splits work across specialist agents that run in parallel within one process.
- Stage 5 deploys each agent as an independent HTTP service communicating through the A2A protocol.

Exercises completed include adding knowledge base entries, creating tools, modifying agent prompts, testing fault tolerance, and observing trace propagation.

All outputs are saved in the `outputs/` folder. The `tax_agent/graph.py` prompt was shortened for Exercise 5.3, and the Stage 4 routing was fixed to work with the installed LangGraph version.

## Quick Start

```bash
uv sync
cp .env.example .env   # add your OpenRouter API key
uv run python stages/stage_1_direct_llm/main.py
./start_all.sh          # launches all 5 A2A services
uv run python test_client.py
```

## Key Files

- `CODELAB_REPORT.md` — all answers, observations, and exercise results
- `ARCHITECTURE.md` — full system architecture and design notes
- `outputs/` — pre-generated outputs for all five stages
- `tax_agent/graph.py` — modified for Exercise 5.3
- `stages/stage_4_milti_agent/main.py` — fixed routing logic
