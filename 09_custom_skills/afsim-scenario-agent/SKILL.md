---
name: afsim-scenario-agent
description: Offline AFSIM intelligent scenario generation workflow using local Ollama models, local RAG knowledge, JSON validation, AFSIM script generation, mission.exe verification, and optional MCP tool calls. Use when Codex needs to create, validate, debug, or explain AFSIM scenario-generation tasks in the D:\AFsim\Agent project, especially requests involving EOIR reconnaissance demos, local model drafting, Agent loops, MCP wrappers, or AFSIM JSON-to-txt workflows.
---

# AFSIM Scenario Agent

Use this skill to work on the local AFSIM intelligent scenario-generation project under `D:\AFsim\Agent`.

## Workflow

1. Inspect the target step directory before editing.
2. Keep every learning step in its own numbered folder.
3. Prefer the existing JSON intermediate format over direct model-written AFSIM txt.
4. Use local RAG context from the step's `knowledge/` folder before drafting scenarios.
5. Generate or repair scenario JSON with the local Ollama model.
6. Validate JSON before generating AFSIM scripts.
7. Run `mission.exe` as the final verification gate when the step requires runnable AFSIM output.
8. Commit and push each completed step if the repository remote is configured.
9. For engineering acceptance, disable rule fallback and preserve the full trace and benchmark report.

## Choose The Entry Point

- For ordinary scenario generation, use `07_agent_loop/agent_loop.py`.
- For standard tool-protocol calls, use `08_mcp_tools/mcp_server.py` or `08_mcp_tools/mcp_client_test.py`.
- For checking local prerequisites, run `scripts/check_afsim_agent_env.py`.

## Required Local Assumptions

- Project root: `D:\AFsim\Agent`
- AFSIM mission executable: `D:\AFsim\AFSim\afsim-2.9.0-win64\bin\mission.exe`
- Ollama model storage: `D:\AFsim\Agent\ollama\models`
- Production baseline model: `qwen2.5:7b`
- Smoke-test-only model: `qwen2.5:0.5b`

## References

- Read `references/workflow.md` when implementing or explaining a learning step.
- Read `references/mcp.md` when working on MCP integration or tool-call debugging.
