---
name: triage-issue
description: Triage a bug or issue by exploring the codebase to find root cause, then create a structured TDD-based fix plan. Use when user reports a bug, wants to investigate a problem, mentions "triage", or wants a structured plan before fixing.
user_invocable: true
---

# Triage Issue

Investigate a reported problem, find its root cause, and produce a TDD fix plan. Minimize questions — start investigating immediately.

## Process

### 1. Capture the problem

Get a brief description from the user. If not provided, ask ONE question: "What's the problem you're seeing?" Do NOT ask follow-ups. Start investigating immediately.

### 2. Explore and diagnose

Use the Agent tool with subagent_type=Explore to deeply investigate the codebase. Find:

- **Where** the bug manifests (entry points, API responses, UI)
- **What** code path is involved (trace the flow)
- **Why** it fails (root cause, not just symptom)
- **What** related code exists (similar patterns, tests, adjacent modules)

Look at: related source files, existing tests, recent git log on affected files, error handling in the code path, similar working patterns elsewhere.

### 3. Identify the fix approach

Determine:
- The minimal change needed to fix the root cause
- Which modules/interfaces are affected
- What behaviors need to be verified via tests
- Whether this is a regression, missing feature, or design flaw

### 4. Design TDD fix plan

Create an ordered list of RED-GREEN cycles. Each cycle is one vertical slice:

- **RED**: Describe a specific test that captures the broken/missing behavior
- **GREEN**: Describe the minimal code change to make that test pass

Rules:
- Tests verify behavior through public interfaces, not implementation details
- One test at a time, vertical slices (NOT all tests first, then all code)
- Each test should survive internal refactors
- Include a final refactor step if needed

### 5. Present the plan

Output the root cause, fix plan, and acceptance criteria. Ask if Kevin wants to proceed with execution or file it as a GitHub issue.
