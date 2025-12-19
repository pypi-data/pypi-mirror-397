# KYTCHEN | The Brand Bible
**"The Runtime Layer for the Agentic Web."**

---

## 0. The Billion-Dollar Positioning

### The Landing Page Hero

> **GitHub is where code sleeps. Kytchen is where code cooks.**
>
> We are the **Runtime Layer** for the Agentic Web.

### The Three Bullets

> - **Don't build a sandbox.** `pip install kytchen`
> - **Don't stuff context.** Let Kytchen sieve it.
> - **Don't trust the output.** Check the Sauce.

### The Promise

> **Stop paying $50/query to send raw PDFs to Claude.**
> Send your Agent to Kytchen, and let it cook for pennies.

---

### The Heroku Analogy

| Era | The Problem | The Solution | The Outcome |
| :--- | :--- | :--- | :--- |
| **Web 2.0** | Servers are hard. | **Heroku** | Developers shipped 10x faster. |
| **Agentic AI** | Context/State is hard. | **Kytchen** | Agents ship 10x faster. |

**Before Heroku:** Developers wasted 50% of their time managing Servers.
**Before Kytchen:** Developers waste 50% of their time managing Context (parsing PDFs, setting up sandboxes, handling memory).

**Heroku:** "Don't think about Servers. Just write Code."
**Kytchen:** "Don't think about Context. Just write Prompts."

### Platform vs Tool
We are NOT a tool. We are **The Runtime**.

- **Recipe Books are not "planned"** - they are THE CORE
- **Fork = Full Environment** (indexed data + tools + config)
- **The Pantry is the moat** - pre-indexed data is valuable
- When you fork, you save 20 minutes of setup. THAT is the network effect.

### The Magic Command
Heroku had `git push heroku master`. Kytchen has:
```bash
kytchen run recipe.json --ingredients ./docs/
```
You send us your recipe and ingredients. **Magic happens.** We provision the sandbox, parse the documents, manage the memory, and return the dish with sauce (evidence).

### Where Things Live
- **GitHub** is where code *sleeps*.
- **Kytchen** is where code *cooks*.
- We are where the Agents **live.**

### Why This Matters for Investors
When you say "We are the Heroku for Agents," they immediately understand:
1. You are an **Infrastructure Play** (High value, defensible moat)
2. You are solving the **"Deployment"** problem for AI
3. You are aiming to be the **Default Standard**
4. The Pantry (pre-indexed data) = network effect = winner-take-all

---

## 1. The Core Innovation: "Infinite Context via Prep"
**Kytchen solves the Context Window Problem.**
Most "Long Context" (1M+ token) models are a trap. They get lazy ("Lost in the Middle"), hallucinate, and burn cash.
Kytchen doesn't stuff the context window. It **manages** it.

*   **The Mechanism:** The model sees **metadata, not full text.** It uses a REPL to `grep`, `search`, and `read` documents iteratively.
*   **The Metaphor:** "Mise en Place" for AI.
    *   **The Pantry (Infinite Data):** Your terabytes of docs/code.
    *   **The Prep Cook (Local Agent):** Aggressively filters `grep "auth"` -> 12 hits. Trims the fat.
    *   **The Chef (LLM):** "Plates" the final 500-token signal.

## 2. The Core Aesthetic
**"Industrial Kitchen Chic."**
*   **Vibe:** Deterministic. Auditable. "Grep first. Generate second."
*   **Visuals:** The "Reduction Pipeline." Big interactions that shrink data visibly.
*   **UI Hook:**
    *   **Ticket Rail:** The active order.
    *   **Ticket Annotation:** Live handwritten-style notes in margins as the agent works (`grep: 12 hits`, `read: 2 candidates`).

## 3. The Killer Hooks (Landing Page)
*   **"Grep first. Generate second."** (The CTO Hook)
*   **"Your LLM reads metadata. Not your monorepo."** (The Engineer Hook)
*   **"Infinite pantry. 500-token plate."** (The Brand Hook)
*   **"Stop stuffing prompts. Prep context. Ship answers."**

### B. The "Glass Kitchen" (Trust & Observability) 👓
*   **Problem:** Standard AI is a black box. You don't know *why* it gave an answer.
*   **Solution:** **Extreme Observability.** We show the `grep`, the `scan`, the `read`.
*   **Pitch:** "See the prep work. Trust the dish."

### C. "Chain of Custody" (Liability) ⚖️
*   **Problem:** Hallucinations are liability landmines for Enterprise/Gov.
*   **Solution:** **Audit Receipts.** Every `read()` is logged.
*   **Pitch:** "Malpractice Insurance for your AI."

## 4. The "Spicy" UI/UX
*   **Ticket Rail:** Jobs hang like tickets. Pulse when cooking. Spike when done.
*   **Thermal Receipts:** Logs are jagged, physical, and verifiable.
*   **Heat Knobs:** Analog control for temperature.
*   **Action 86:** "86 Me" instead of Logout. "86 Station" instead of Delete.

## 5. Terminology (The Slang)

### Core Concepts
| Standard SaaS | Kytchen Term | Usage |
| :--- | :--- | :--- |
| **System** | **The House** | "The House is busy" = high load |
| **Query** | **Ticket / Order** | "Fire a ticket" = start a query |
| **Dataset** | **Ingredients** | Input data loaded into pantry |
| **Storage** | **Pantry** | Where ingredients are stored |
| **Execution env** | **Prep Station** | Sandboxed REPL for analysis |
| **Logs** | **Receipts** | Thermal-style audit logs |
| **Settings** | **Mise en Place** | Configuration/setup |
| **Delete** | **86** | "86 that file" = delete it |
| **Success** | **Heard** | Acknowledgment, completion |
| **Error** | **In the Weeds** | Something went wrong |

### Workflow Concepts (Recipe System)
| Concept | Kytchen Term | Description |
| :--- | :--- | :--- |
| **Workflow definition** | **Recipe** | A Kytchenfile (JSON/YAML) defining query, ingredients, budget |
| **Workflow output** | **Dish** | The result of running a recipe (RecipeResult) |
| **Evidence/citations** | **Sauce** | Provenance trail - "where's the sauce?" = show your sources |
| **Workflow collection** | **Recipe Book** | Collection of related recipes (like a GitHub repo) |
| **User/creator** | **Chef** | Author of recipes, handle is @chef_name |
| **Token budget** | **Portion Control** | Budget constraints on a recipe |

### Actions
| Action | Kytchen Verb | Example |
| :--- | :--- | :--- |
| Start a query | **Fire** | "Fire the ticket" |
| Load data | **Prep** | "Prep the ingredients" |
| Execute code | **Cook** | "Cooking the analysis" |
| Return results | **Plate** | "Plating the dish" |
| Duplicate/copy | **Fork** | "Fork this recipe" |
| Favorite | **Star** | "Star this book" |
| Cancel | **86** | "86 that order" |

### Status Indicators
| Status | Kytchen Term | Visual |
| :--- | :--- | :--- |
| Queued | **On Deck** | Grey, waiting |
| In Progress | **Cooking** | Pulsing, orange/yellow |
| Complete | **Plated** | Green, checkmark |
| Error | **Burned** | Red, crossed out |
| Cancelled | **86'd** | Struck through |

### Roles
| Role | Kytchen Term |
| :--- | :--- |
| Admin | **Executive Chef** |
| Power User | **Sous Chef** |
| Regular User | **Line Cook** |
| Read-only | **Front of House** |

---

## 6. Copywriting Guidelines

### Voice
- **Direct**: No fluff. "Grep first. Generate second."
- **Confident**: We know this works. "See the prep. Trust the dish."
- **Technical but accessible**: Kitchen metaphors bridge the gap
- **Slightly irreverent**: "Malpractice insurance for your AI"

### Headlines (Examples)
- "Infinite pantry. 500-token plate."
- "Stop stuffing prompts. Prep context. Ship answers."
- "Your LLM reads metadata. Not your monorepo."
- "Show your sauce. Ship with confidence."

### Button Labels
| Generic | Kytchen |
| :--- | :--- |
| Submit | Fire |
| Run | Cook |
| Delete | 86 |
| Cancel | 86 |
| Save | Heard |
| Create | Prep |
| Export | Plate |
| Copy | Fork |

### Error Messages
- "Something went wrong" → "In the weeds - [specific error]"
- "Not found" → "86'd - couldn't find that"
- "Unauthorized" → "Back of house only"
- "Rate limited" → "Kitchen's slammed - try again in [X]"
- "Timeout" → "Order burned - took too long"

### Success Messages
- "Saved" → "Heard!"
- "Deleted" → "86'd"
- "Completed" → "Plated and ready"
- "Copied" → "Forked to your book"
