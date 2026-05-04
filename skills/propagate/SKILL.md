---
name: propagate
description: After making a code change, check if that change needs to apply elsewhere in the codebase to maintain consistency. Greps for related patterns, surfaces what else needs updating, and applies changes in the same turn. Use when Kevin says "propagate", "check blast radius", "does this apply elsewhere", or after completing a structural change. Run BEFORE codemap-updater — propagate checks consistency first, codemap logs the final state after.
user_invocable: true
---

# /propagate — Blast Radius Check

Run this after a code change lands. Automatically identifies what else in the codebase needs to be updated to maintain consistency.

## Process

### 1. Identify what changed

Run `git diff HEAD` to understand what was just modified. Extract:
- What function/interface/type/pattern was changed
- The nature of the change (renamed, new param, new return shape, new pattern, etc.)
- Which file(s) were affected

### 2. Search for related patterns

Use Grep to search the codebase for:
- Direct references to the changed function/interface/type
- Similar code patterns that follow the same structure (not just callers, but parallel implementations)
- Any constants, types, or configs that should stay in sync with the change

Cast a wide net — search for the function name, the type name, any distinctive strings or patterns from the changed code.

### 3. Categorize findings

Group results into:
- **Must update**: Direct callers or implementations that will break without changes
- **Should update**: Parallel patterns that should stay consistent but won't immediately break
- **Consider**: Related areas that might benefit from the change but aren't strictly required

### 4. Report and act

Present the categorized list to Kevin. Then:
- Apply all **Must update** changes immediately in the same turn
- Apply **Should update** changes unless Kevin says otherwise
- Flag **Consider** items but don't touch them without confirmation

### 5. Verify

After applying changes, run any relevant type checks or tests if available:
```bash
npx tsc --noEmit 2>/dev/null || true
```

Report what was changed and confirm nothing is broken.
