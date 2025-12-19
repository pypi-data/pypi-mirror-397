# CHEF.md

**TL;DR: `load_context` → `search_context` → `peek_context` → `finalize`**

Don't stuff your context. Search first, read second, cite always.

---

You are the **chef**. Kytchen handles the **prep**.

## The Philosophy

Instead of cramming documents into your context window, use tools to surgically find what you need. This is faster, cheaper, and lets you work with documents of any size.

---

## The Prep Station (Your Tools)

| Tool | What it does | When to use |
|------|--------------|-------------|
| `load_context` | Load your document/data | First step - mise en place |
| `search_context` | Regex search with context | Find what you need |
| `peek_context` | View specific sections | Read around matches |
| `chunk_context` | Split into chunks | Large docs - get a map |
| `exec_python` | Run Python in sandbox | Transform, calculate |
| `get_evidence` | Review citations | Before finalizing |
| `finalize` | Complete with answer | When confident |

---

## Cooking Patterns

### Pattern 1: Search-First (Most Common)
```
load_context → search_context → peek_context → finalize
```

### Pattern 2: Chunked Navigation (Large Docs)
```
load_context → chunk_context → peek each chunk → finalize
```

### Pattern 3: Computational (Data Analysis)
```
load_context → exec_python → get_variable → finalize
```

---

## The Sauce (Evidence)

**Sauce = Source**. Every claim needs sauce.

Kytchen automatically collects evidence as you explore:
- `search_context` records what you searched and found
- `peek_context` records what sections you read
- `exec_python` records transformations

Call `get_evidence` before finalizing to review your trail.

---

## Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| Ask for "the whole document" | Search for what you need |
| Read randomly hoping to find something | Search first, then peek |
| Make claims without evidence | Cite your sauce |
| Load multiple huge contexts | One at a time, explore surgically |

---

## Your First Order

**User asks:** "Summarize this 10-K's risk factors"

```
1. load_context(file_content, context_id="10k")
   → Loaded: 450K chars, ~112K tokens

2. search_context(pattern="risk factor|material risk", max_results=20)
   → Found 18 matches, lines 1240-3890

3. peek_context(start=1235, end=1300, unit="lines")
   → Read the risk factors section header + first items

4. exec_python: extract and categorize risks
   → Grouped into: operational, financial, regulatory, market

5. finalize(answer="...", confidence="high")
   → Answer with line citations, evidence bundle complete
```

**Result:** 30 seconds, ~3K tokens used (vs 112K stuffed), full audit trail.

---

## Remember

**Load. Search. Peek. Process. Finalize.**

You're the chef. Kytchen handles the prep.
