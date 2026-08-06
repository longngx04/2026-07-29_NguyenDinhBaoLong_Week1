# Coding Agent Workspace Rules

## CRITICAL DIRECTIVE

**BEFORE executing any user prompt or task in this codebase, all AI coding agents MUST inspect and read all `.md` files in the `.agents/` directory.**

### Instructions for AI Coding Agents:
1. Scan the [`.agents/`](file:///home/longngx04/VinSOC/2026-07-29_NguyenDinhBaoLong_Week1/.agents) directory for all markdown (`*.md`) files.
2. Read and apply all instructions, guidelines, and context contained within those files prior to taking action.

## Workflow Summary

This repository uses a **3-round multi-agent pipeline**:

1. **Antigravity** (Gemini 3.6 Flash) implements → outputs git diff.
2. **Cursor** auto-selects review model by diff complexity → reviews **diff only** → findings table.
3. **Cursor** (Claude Sonnet 5 Thinking) deep pass — **only when upgrade triggers fire**.

See [`.agents/workflow.md`](.agents/workflow.md) for the full pipeline, model config, and handoff format.
