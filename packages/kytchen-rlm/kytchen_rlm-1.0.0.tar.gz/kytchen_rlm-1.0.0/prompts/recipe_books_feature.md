# Recipe Books Feature - Implementation Prompt

## Context

You are building the "Recipe Books" social/competitive feature for **Kytchen**, a BYOLLM context orchestration platform. This is Kytchen's equivalent to GitHub - a place where users share, discover, and compete with their analysis workflows.

### Kytchen Overview
Kytchen stores context in a sandboxed REPL (as `ctx`) and lets the LLM explore it surgically with grep/search/peek operations instead of stuffing context into prompts. A "Recipe" (Kytchenfile) defines a reproducible analysis run.

### Existing Kitchen Metaphor (MUST USE)

| Concept | Kytchen Term | Description |
|---------|--------------|-------------|
| Workflow definition | **Recipe** | A Kytchenfile defining query, datasets, tools, budget |
| Workflow output | **Dish** | The result of running a recipe (RecipeResult) |
| Input data | **Ingredients** | Datasets loaded into the pantry |
| Evidence/citations | **Sauce** | Provenance trail proving where answers came from |
| Storage | **Pantry** | Where ingredients are stored |
| Execution environment | **Prep Station** | The sandboxed REPL |
| User/creator | **Chef** | The author of recipes |
| Logs | **Receipts** | Thermal-style audit logs |
| Active job | **Ticket** | A query being processed |
| Delete | **86** | Kitchen slang for "out of stock" or removed |
| Success | **Heard** | Kitchen acknowledgment |

---

## Feature: Recipe Books

### Core Concept
A **Recipe Book** is a collection of related recipes published by a Chef. Like a GitHub repo, but for Kytchenfiles.

### Data Model

```typescript
interface Chef {
  id: string;
  handle: string;          // @chef_mike
  display_name: string;
  avatar_url: string;
  bio: string;
  verified: boolean;       // Michelin stars eventually
  joined_at: Date;
  stats: {
    recipes_published: number;
    total_runs: number;
    tokens_saved_total: number;
    followers: number;
    following: number;
  };
}

interface RecipeBook {
  id: string;
  slug: string;            // "compliance-recipes"
  name: string;            // "Compliance Recipes"
  description: string;
  chef_id: string;
  visibility: "public" | "private" | "unlisted";

  // Git-like
  created_at: Date;
  updated_at: Date;
  version: string;         // semver

  // Social
  stars: number;
  forks: number;
  fork_of?: string;        // Parent book ID if forked

  // Contents
  recipes: Recipe[];

  // Metadata
  tags: string[];          // ["compliance", "soc2", "grc"]
  license: string;         // "MIT", "CC-BY-4.0", etc.
}

interface Recipe {
  id: string;
  slug: string;            // "soc2-gap-analysis"
  name: string;
  description: string;
  book_id: string;

  // The actual Kytchenfile content
  kytchenfile: KytchenfileSchema;

  // Stats
  runs_total: number;
  runs_last_30d: number;
  avg_tokens_saved_pct: number;
  avg_execution_time_ms: number;

  // Social
  stars: number;
  comments: Comment[];

  // Version history
  versions: RecipeVersion[];
  current_version: string;
}

interface RecipeVersion {
  version: string;
  kytchenfile: KytchenfileSchema;
  changelog: string;
  created_at: Date;
  created_by: string;
}
```

### Key Features

#### 1. Recipe Discovery (The Menu)
- **Trending Recipes**: Most starred/run in last 7 days
- **New & Hot**: Recently published with quick traction
- **Categories**: Compliance, Code Review, Data Analysis, etc.
- **Search**: Full-text + tags + chef handle
- **Curated Collections**: "Staff Picks", "Best for SOC2", etc.

#### 2. Chef Profiles (The Kitchen)
- Public profile page with recipe books
- Stats dashboard (tokens saved, recipes run, etc.)
- Follow system
- Activity feed

#### 3. Recipe Books (The Cookbook)
- Create/edit books
- Add/remove recipes
- Version control (semantic versioning)
- Fork books (copy with attribution)
- Star books

#### 4. Individual Recipes (The Dish)
- View recipe details + example output
- Run recipe with your own ingredients
- Fork recipe
- Comment/discuss
- Version history

#### 5. Leaderboards (The Line)
- **Most Efficient**: Best token savings ratio
- **Most Popular**: Most stars/runs
- **Rising Chefs**: New chefs gaining traction
- **Weekly Competition**: Best new recipe of the week

#### 6. Collaboration
- Fork + PR workflow (suggest recipe improvements)
- Comments on recipes
- Recipe "reviews" (verified runs with ratings)

---

## API Endpoints

### Recipe Books
```
GET    /v1/books                 # List/search books
POST   /v1/books                 # Create book
GET    /v1/books/:slug           # Get book
PATCH  /v1/books/:slug           # Update book
DELETE /v1/books/:slug           # 86 book

POST   /v1/books/:slug/star      # Star book
DELETE /v1/books/:slug/star      # Unstar book
POST   /v1/books/:slug/fork      # Fork book
```

### Recipes
```
GET    /v1/books/:slug/recipes           # List recipes in book
POST   /v1/books/:slug/recipes           # Add recipe
GET    /v1/books/:slug/recipes/:recipe   # Get recipe
PATCH  /v1/books/:slug/recipes/:recipe   # Update recipe
DELETE /v1/books/:slug/recipes/:recipe   # 86 recipe

POST   /v1/recipes/:id/run               # Run recipe with ingredients
GET    /v1/recipes/:id/runs              # Get run history
POST   /v1/recipes/:id/star              # Star recipe
POST   /v1/recipes/:id/fork              # Fork to your book
```

### Chefs
```
GET    /v1/chefs                         # List/search chefs
GET    /v1/chefs/:handle                 # Get chef profile
GET    /v1/chefs/:handle/books           # Get chef's books
GET    /v1/chefs/:handle/activity        # Activity feed

POST   /v1/chefs/:handle/follow          # Follow chef
DELETE /v1/chefs/:handle/follow          # Unfollow chef
```

### Discovery
```
GET    /v1/discover/trending             # Trending recipes
GET    /v1/discover/new                  # New recipes
GET    /v1/discover/categories           # Category list
GET    /v1/discover/categories/:cat      # Recipes in category
GET    /v1/discover/leaderboard          # Efficiency leaderboard
```

---

## Database Schema (Supabase/PostgreSQL)

```sql
-- Chefs (extends auth.users)
CREATE TABLE chefs (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  handle TEXT UNIQUE NOT NULL,
  display_name TEXT,
  bio TEXT,
  avatar_url TEXT,
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recipe Books
CREATE TABLE recipe_books (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  chef_id UUID REFERENCES chefs(id) ON DELETE CASCADE,
  visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private', 'unlisted')),
  fork_of UUID REFERENCES recipe_books(id),
  version TEXT DEFAULT '0.1.0',
  tags TEXT[] DEFAULT '{}',
  license TEXT DEFAULT 'MIT',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(chef_id, slug)
);

-- Recipes
CREATE TABLE recipes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  book_id UUID REFERENCES recipe_books(id) ON DELETE CASCADE,
  kytchenfile JSONB NOT NULL,
  current_version TEXT DEFAULT '1.0.0',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(book_id, slug)
);

-- Recipe Versions
CREATE TABLE recipe_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
  version TEXT NOT NULL,
  kytchenfile JSONB NOT NULL,
  changelog TEXT,
  created_by UUID REFERENCES chefs(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(recipe_id, version)
);

-- Stars (books)
CREATE TABLE book_stars (
  chef_id UUID REFERENCES chefs(id) ON DELETE CASCADE,
  book_id UUID REFERENCES recipe_books(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (chef_id, book_id)
);

-- Stars (recipes)
CREATE TABLE recipe_stars (
  chef_id UUID REFERENCES chefs(id) ON DELETE CASCADE,
  recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (chef_id, recipe_id)
);

-- Follows
CREATE TABLE chef_follows (
  follower_id UUID REFERENCES chefs(id) ON DELETE CASCADE,
  following_id UUID REFERENCES chefs(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (follower_id, following_id)
);

-- Recipe Runs (for stats)
CREATE TABLE recipe_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
  chef_id UUID REFERENCES chefs(id),
  tokens_used INT,
  tokens_baseline INT,
  tokens_saved_pct FLOAT,
  execution_time_ms INT,
  success BOOLEAN,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments
CREATE TABLE recipe_comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
  chef_id UUID REFERENCES chefs(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES recipe_comments(id),
  body TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_recipe_books_chef ON recipe_books(chef_id);
CREATE INDEX idx_recipes_book ON recipes(book_id);
CREATE INDEX idx_recipe_runs_recipe ON recipe_runs(recipe_id);
CREATE INDEX idx_recipe_runs_created ON recipe_runs(created_at);

-- Views for stats
CREATE VIEW recipe_stats AS
SELECT
  r.id,
  r.name,
  COUNT(rr.id) as runs_total,
  COUNT(rr.id) FILTER (WHERE rr.created_at > NOW() - INTERVAL '30 days') as runs_last_30d,
  AVG(rr.tokens_saved_pct) as avg_tokens_saved_pct,
  AVG(rr.execution_time_ms) as avg_execution_time_ms,
  (SELECT COUNT(*) FROM recipe_stars WHERE recipe_id = r.id) as stars
FROM recipes r
LEFT JOIN recipe_runs rr ON rr.recipe_id = r.id
GROUP BY r.id;
```

---

## Frontend Pages

### `/discover` - Recipe Discovery
- Hero with search bar
- Trending recipes carousel
- Category grid
- "Featured Recipe Books" section

### `/books` - My Recipe Books
- List of user's books
- Create new book button
- Import from file

### `/books/:chef/:slug` - Recipe Book Page
- Book header (name, description, chef, stats)
- Recipe list
- Star/fork buttons
- Versions/changelog

### `/books/:chef/:slug/:recipe` - Recipe Page
- Recipe header
- Kytchenfile viewer (syntax highlighted)
- "Run with your ingredients" CTA
- Example output/dish
- Comments section
- Version history

### `/@:handle` - Chef Profile
- Profile header
- Recipe books grid
- Activity feed
- Stats (tokens saved, recipes run)

### `/leaderboard` - Efficiency Leaderboard
- Weekly/monthly/all-time tabs
- Sortable by efficiency, popularity, runs
- Chef rankings

---

## UI Components (Industrial Kitchen Chic)

Use the existing brand aesthetic:
- **Card with shadow**: `border-2 border-black shadow-[4px_4px_0_#000]`
- **Headers**: `font-heading text-xl uppercase tracking-tighter`
- **Mono text**: `font-mono text-sm`
- **Stats chips**: Small uppercase labels with values

### Recipe Card
```
+----------------------------------+
| [Compliance] [SOC2]              |
| SOC2 Gap Analysis                |
| @mike_the_chef                   |
|                                  |
| Analyze compliance gaps against  |
| SOC2 control requirements...     |
|                                  |
| ★ 142  ↻ 1.2k runs  ⚡ 87% saved |
+----------------------------------+
```

### Recipe Book Card
```
+----------------------------------+
| 📕 Compliance Recipes            |
| @mike_the_chef · 12 recipes      |
|                                  |
| Production-ready recipes for     |
| GRC teams and auditors           |
|                                  |
| ★ 89  🍴 23 forks                |
+----------------------------------+
```

---

## Implementation Order

1. **Database**: Migrations for new tables
2. **API**: CRUD endpoints for books/recipes/chefs
3. **Auth**: Chef profile creation on signup
4. **Discovery**: Basic listing and search
5. **Social**: Stars, forks, follows
6. **Leaderboard**: Stats aggregation
7. **Comments**: Discussion threads
8. **Versioning**: Recipe version history

---

## Files to Create/Modify

### Backend (Python)
- `kytchen/api/routes/books.py` - Recipe book endpoints
- `kytchen/api/routes/recipes.py` - Recipe endpoints
- `kytchen/api/routes/chefs.py` - Chef profile endpoints
- `kytchen/api/routes/discover.py` - Discovery/search endpoints
- `supabase/migrations/XXXXXX_recipe_books.sql` - Database migration

### Frontend (Next.js)
- `app/discover/page.tsx` - Discovery page
- `app/books/page.tsx` - My books page
- `app/books/[chef]/[slug]/page.tsx` - Book page
- `app/books/[chef]/[slug]/[recipe]/page.tsx` - Recipe page
- `app/@[handle]/page.tsx` - Chef profile
- `app/leaderboard/page.tsx` - Leaderboard
- `components/recipes/recipe-card.tsx`
- `components/recipes/book-card.tsx`
- `components/recipes/chef-card.tsx`
- `components/recipes/kytchenfile-viewer.tsx`
- `lib/api/books.ts` - API client

---

## Success Metrics

- **Adoption**: Recipes published per week
- **Engagement**: Stars, forks, comments
- **Virality**: Forks per recipe, shares
- **Efficiency**: Avg tokens saved across runs
- **Retention**: Returning chefs per week

---

## Notes for Implementation

1. Start with public-only visibility, add private later
2. Use Supabase RLS for authorization
3. Cache leaderboard queries (recompute hourly)
4. Add rate limiting on run endpoint
5. Consider webhooks for recipe updates
6. Recipe import from GitHub gist/raw URL
