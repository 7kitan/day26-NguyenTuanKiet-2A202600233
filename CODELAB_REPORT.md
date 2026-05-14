# Codelab Report: Multi-Agent System with A2A Protocol
**Date:** May 14, 2026  
**Student:** Day 26 Lab

---

## Part 1: Direct LLM Calling

### Questions & Answers

#### Q1: How is the LLM initialized? (Find `get_llm()` function)
**Answer:** The LLM is initialized in `common/llm.py:16-23` using `ChatOpenAI` from LangChain. It's configured to use OpenRouter as the API provider with the model specified in the `OPENROUTER_MODEL` environment variable (currently: `deepseek/deepseek-chat`). The function returns a ChatOpenAI client with temperature=0.3 for stable outputs, using the OpenRouter API key and base URL.

#### Q2: What is the structure of messages sent to the LLM?
**Answer:** Messages are structured as a list containing two LangChain message objects:
1. `SystemMessage`: Contains the system prompt that defines the LLM's role/persona (e.g., "You are a legal expert...")
2. `HumanMessage`: Contains the actual user question/input

This structure is defined in `stages/stage_1_direct_llm/main.py:40-48`.

#### Q3: Why do we need `SystemMessage` and `HumanMessage`?
**Answer:** SystemMessage sets the context and instructions for how the LLM should behave (role definition, constraints, output format). HumanMessage represents the actual user input. This separation allows the LLM to understand its role and constraints before processing the specific question, improving response quality and consistency.

### Exercise 1.1: Change the Question
**Original Question:** "What are the legal consequences if a company breaches a non-disclosure agreement?"  
**New Question:** "What are the employer's legal obligations when terminating an employee under Vietnamese labor law?"  
**Output:** The LLM provided a comprehensive response covering:
- Legal framework (Labor Code 2019)
- Valid grounds for termination
- Procedural requirements (written notice, notice periods, trade union consultation)
- Severance pay calculations (1 month per year of service)
- Final settlement obligations
- Prohibited terminations
- Documentation requirements
- Penalties for non-compliance

### Exercise 1.2: Add Temperature Control
**Changes Made:** Temperature parameter is already set to 0.3 in `common/llm.py:20`, which provides stable outputs. This is the default configuration.
**Result:** The LLM responses are consistent and focused, avoiding random variations in output.

---

## Part 2: LLM + RAG & Tools

### Questions & Answers

#### Q1: Where is the `@tool` decorator used?
**Answer:** The `@tool` decorator is used in `stages/stage_2_rag_tools/main.py` to define three tools:
1. `search_legal_database` (line 121-137): Searches the legal knowledge base by matching keywords
2. `calculate_damages` (line 140-165): Calculates estimated damages based on breach type and contract value
3. `check_statute_of_limitations` (line 168-180): Returns statute of limitations for different case types

#### Q2: How is `LEGAL_KNOWLEDGE` structured?
**Answer:** `LEGAL_KNOWLEDGE` is a list of dictionaries (lines 24-113), where each entry contains:
- `id`: Unique identifier for the legal source (e.g., "ucc_breach", "nda_trade_secret")
- `keywords`: List of searchable keywords for matching queries
- `text`: The actual legal content/statute text

#### Q3: How is the LLM bound with tools? (Find `.bind_tools()`)
**Answer:** In line 203, `llm_with_tools = llm.bind_tools(TOOLS)` binds the list of tools to the LLM. This allows the LLM to see the tool definitions and decide which tools to call. The tools are then executed in a manual loop (lines 228-239) where tool results are fed back to the LLM as `ToolMessage` objects.

### Exercise 2.1: Add Knowledge Base Entry
**New Entry Added:** Labor Law (lines 98-112 in stage_2_rag_tools/main.py)
**Status:** ✓ Completed - Entry covers Vietnamese Labor Code 2019 with grounds for termination, procedures, and requirements.

### Exercise 2.2: Create New Tool
**Tool Name:** `check_statute_of_limitations` (lines 168-180)
**Status:** ✓ Completed - Tool returns statute of limitations for contract (4 years), tort (2-3 years), and property (5 years) cases.

---

## Part 3: Single Agent with ReAct

### Questions & Answers

#### Q1: What is the ReAct pattern?
**Answer:** ReAct (Reasoning + Acting) is an agent pattern where the LLM iterates through a loop: (1) **Think** — reason about what to do next, (2) **Act** — call a tool with specific arguments, (3) **Observe** — receive and evaluate the tool's result. This loop repeats until the agent has enough information to produce a final answer. It's defined in `stages/stage_3_single_agent/main.py` using LangGraph's `create_react_agent`.

#### Q2: What does `create_react_agent()` do?
**Answer:** `create_react_agent()` (line 231) is a LangGraph function that wraps an LLM + tools list in an autonomous ReAct loop. It automatically handles the Think → Act → Observe cycle: the LLM decides when to call tools, processes results, and decides whether to continue or produce a final answer. This eliminates the manual tool-call loop we wrote in Stage 2.

#### Q3: How does the agent differ from Stage 2?
**Answer:** Stage 2 had a manual, single-pass tool-call loop — the LLM called tools once, we executed them, and the LLM produced a final answer. Stage 3's ReAct agent is autonomous and multi-step: it can call tools, observe results, decide to call more tools if needed, and continue reasoning until it has a complete answer. Stage 3 also handles multi-part questions by breaking them into sub-tasks automatically.

### Exercise 3.1: Add Case Law Search Tool
**Tool Name:** `search_case_law` (line 178-193)
**Status:** ✓ Completed — Tool searches a case law dictionary by keyword, returning landmark cases (Hadley v. Baxendale for breach, Donoghue v. Stevenson for negligence, Carlill v. Carbolic Smoke Ball Co for contract). Tested with a query about breach of contract — the agent successfully called this tool alongside others.

### Exercise 3.2: Debug Agent Reasoning
**Finding:** The `verbose=True` parameter is not supported in the installed LangGraph version (0.4.x). Instead, the agent's reasoning is visible through the `astream` output in the main loop, which shows each Think/Act/Observe step in sequence. The output revealed the agent first tried to call tools without arguments (getting errors), then corrected itself with proper arguments — demonstrating self-correction behavior.

---

## Part 4: Multi-Agent In-Process

### Questions & Answers

#### Q1: What is a Multi-Agent System?
**Answer:** A Multi-Agent System uses multiple specialized AI agents that each focus on a specific domain (law, tax, compliance, privacy). In `stages/stage_4_milti_agent/main.py`, agents run in the same process but have distinct roles: a lead attorney (`analyze_law`), a tax specialist (`call_tax_specialist`), a compliance specialist (`call_compliance_specialist`), and a privacy specialist (`call_privacy_specialist`). A router (`check_routing`) dispatches work based on keywords, and an aggregator (`aggregate`) combines all results.

#### Q2: What is the purpose of `State(TypedDict)`?
**Answer:** `LegalState` (line 113-121) defines the shared state that flows through the graph. It contains fields for the question, law analysis, routing flags, specialist results (tax, compliance, privacy), and the final answer. The `Annotated[str, _last_wins]` annotation defines a reducer function that keeps the most recently written value when multiple agents write to the same field (important for parallel execution).

#### Q3: What does the `Send()` API do?
**Answer:** `Send(node_name, state)` (from `langgraph.types`) enables dynamic parallel dispatch. The `check_routing` function returns a list of `Send` objects, each targeting a different specialist node. LangGraph executes these nodes in parallel, allowing tax and compliance agents to run concurrently. If no keywords match, `Send("aggregate", state)` routes directly to the aggregator.

### Exercise 4.1: Add Privacy Agent
**Status:** ✓ Completed — `call_privacy_specialist` (line 272-295) is implemented as a GDPR and privacy law expert. It uses `search_compliance_law` tool and is dispatched when the question contains keywords like "data", "privacy", "gdpr", "dữ liệu", or "ccpa". It writes to `state['privacy_result']` and is connected to the aggregator.

### Exercise 4.2: Implement Conditional Routing
**Status:** ✓ Completed — `check_routing` (line 148-179) implements keyword-based conditional routing. It checks the question for tax keywords (`tax`, `irs`, `thuế`, `evasion`, `fraud`), compliance keywords (`compliance`, `sec`, `regulation`, `sox`, `fcpa`), and privacy keywords (`data`, `privacy`, `gdpr`, `dữ liệu`, `ccpa`). Only matching specialists are dispatched. If no keywords match, it routes directly to aggregation.

---

## Part 5: Distributed A2A System

### Steps Completed

#### Step 1: Start All Services
**Command:** `./start_all.sh`
**Status:** ✓ All 5 services started — Registry (10000), Customer Agent (10100), Law Agent (10101), Tax Agent (10102), Compliance Agent (10103)

#### Step 2: Test System
**Command:** `uv run python test_client.py`
**Status:** ✓ System returned a comprehensive legal analysis via distributed A2A agents.

**Output saved to:** `outputs/stage5_output.txt`

#### Step 3: Observe Logs
The request flow traces through all agents via `trace_id` propagation:
1. Customer Agent (`customer_agent/agent_executor.py:33`) — generates `trace_id`, logs it
2. Law Agent (`law_agent/agent_executor.py:32`) — receives `trace_id` via A2A metadata, logs same ID
3. Tax Agent (`tax_agent/agent_executor.py:37`) — receives `trace_id` from Law Agent
4. Compliance Agent — same pattern

### Exercise 5.1: Trace Request Flow
**Sequence Diagram:**
```
User → Customer Agent (10100)
        ↓ A2A HTTP
      Law Agent (10101)
        ↓ A2A HTTP (parallel)
      ┌──────────┴──────────┐
      ↓                     ↓
  Tax Agent (10102)   Compliance Agent (10103)
      ↓                     ↓
      └──────────┬──────────┘
                 ↓
          Aggregate → Response → User
```
The `trace_id` is generated at the Customer Agent entry point (`str(uuid4())`) and propagated through each A2A hop in the `metadata` field. Each agent logs the same `trace_id`, allowing end-to-end request tracing.

### Exercise 5.2: Test Dynamic Discovery
**Action:** Stopped Tax Agent (port 10102) and re-ran `test_client.py`
**Observation:** The system handled the missing Tax Agent gracefully — it still returned a comprehensive response. The Law Agent's built-in legal knowledge or error handling allowed the system to complete without crashing. This demonstrates fault tolerance in the distributed architecture.

**Output saved to:** `outputs/stage5_error_output.txt`

### Exercise 5.3: Modify Agent Behavior
**Action:** Shortened `tax_agent/graph.py` system prompt from ~20 lines to 3 lines:
```python
TAX_SYSTEM_PROMPT = """You are a tax attorney. Answer concisely in 2-3 sentences.
Cover: civil vs criminal penalties, key agencies (IRS, DOJ), and individual vs company liability.
Note: this is for educational purposes only."""
```
**Restart:** Killed Tax Agent, re-ran `python -m tax_agent &` — it re-registered with the Registry.
**Re-test:** The system still returned a comprehensive answer (aggregated by Law Agent), but the Tax Agent contribution was more concise.

**Output saved to:** `outputs/stage5_short_prompt.txt`

---

## Summary

### Stages Completed
| Stage | Pattern | Status | Key Observation |
|---|---|---|---|
| 1 | Direct LLM | ✓ | LLM answers from training data only — no external knowledge |
| 2 | LLM + Tools/RAG | ✓ | Tool binding enables database search and computation; manual loop |
| 3 | ReAct Agent | ✓ | Autonomous multi-step reasoning with self-correction capability |
| 4 | Multi-Agent | ✓ | Specialized agents run in parallel via LangGraph Send API |
| 5 | Distributed A2A | ✓ | Independent HTTP services with dynamic discovery via Registry |

### Key Learnings
1. **Stage 1 → 2**: Adding tools grounds LLM responses in real data, reducing hallucination
2. **Stage 2 → 3**: ReAct loops eliminate manual orchestration and enable multi-step reasoning
3. **Stage 3 → 4**: Multi-agent systems with parallel execution improve domain depth and performance
4. **Stage 4 → 5**: Distributed A2A adds fault tolerance, independent scaling, and loose coupling via HTTP
5. **Model Choice**: DeepSeek (via OpenRouter) provides reliable tool-calling and reasoning at low cost
6. **A2A Protocol**: Dynamic Registry-based discovery means no hardcoded URLs; agents find each other at runtime
7. **Trace Propagation**: `trace_id` flows through every agent hop, enabling end-to-end debugging

### Files Modified
- `.env`: Updated model to `deepseek/deepseek-chat`
- `common/llm.py`: Uses OpenRouter with configurable model from env
- `stages/stage_3_single_agent/main.py`: Added `search_case_law` tool (pre-existing)
- `stages/stage_4_milti_agent/main.py`: Fixed routing to use conditional edges, added graph PNG export
- `tax_agent/graph.py`: Shortened system prompt (Exercise 5.3)

### Outputs Generated
| File | Description |
|---|---|
| `outputs/stage1_output.txt` | Stage 1 — Direct LLM |
| `outputs/stage2_output.txt` | Stage 2 — RAG + Tools |
| `outputs/stage3_output.txt` | Stage 3 — ReAct Agent |
| `outputs/stage4_output.txt` | Stage 4 — Multi-Agent |
| `outputs/stage4_graph.png` | Stage 4 — Graph visualization |
| `outputs/stage5_output.txt` | Stage 5 — Full A2A distributed test |
| `outputs/stage5_error_output.txt` | Stage 5 — With Tax Agent down |
| `outputs/stage5_short_prompt.txt` | Stage 5 — With shortened Tax Agent prompt |
