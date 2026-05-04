---
name: improve-codebase-architecture
description: Explore a codebase to find opportunities for architectural improvement, focusing on making the codebase more testable by deepening shallow modules. Use when user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more AI-navigable.
user_invocable: true
---

# Improve Codebase Architecture

Explore a codebase like an AI would, surface architectural friction, discover opportunities for improving testability, and propose module-deepening refactors.

A **deep module** (John Ousterhout, "A Philosophy of Software Design") has a small interface hiding a large implementation. Deep modules are more testable, more AI-navigable, and let you test at the boundary instead of inside.

## Process

### 1. Explore the codebase

Use the Agent tool with subagent_type=Explore to navigate the codebase naturally. Note where you experience friction:

- Where does understanding one concept require bouncing between many small files?
- Where are modules so shallow that the interface is nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called?
- Where do tightly-coupled modules create integration risk at the seams between them?
- Which parts of the codebase are untested or hard to test?

The friction you encounter IS the signal.

### 2. Present candidates

Present a numbered list of improvement opportunities. For each:

- **Cluster**: Which modules/concepts are involved
- **Why they're coupled**: Shared types, call patterns, co-ownership of a concept
- **Test impact**: What existing tests would be replaced by boundary tests

Do NOT propose interfaces yet. Ask Kevin: "Which of these would you like to explore?"

### 3. Kevin picks a candidate

### 4. Frame the problem space

Before spawning sub-agents, write a user-facing explanation of the problem space:

- The constraints any new interface would need to satisfy
- The dependencies it would need to rely on
- A rough illustrative code sketch to make the constraints concrete

Show this, then immediately proceed to Step 5.

### 5. Design multiple interfaces

Spawn 3 sub-agents in parallel using the Agent tool. Each produces a radically different interface. Give each a different design constraint:

- Agent 1: "Minimize the interface — aim for 1-3 entry points max"
- Agent 2: "Maximize flexibility — support many use cases and extension"
- Agent 3: "Optimize for the most common caller — make the default case trivial"

Each sub-agent outputs: interface signature, usage example, what complexity it hides, trade-offs.

Present designs, compare in prose, give a recommendation. Be opinionated.

### 6. Kevin picks an interface

### 7. Create a refactor plan

Output a prioritized refactor plan as a numbered list of steps Kevin can execute in order. Each step should be independently executable and verifiable.
