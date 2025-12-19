# Kytchen v1.0 Launch Sprint

**Repo**: `/Volumes/VIXinSSD/kytchen`
**Linear**: https://linear.app/shannonlabs/

---

## What's Done (This Session)

### Backend
- [x] **SHA-107**: Menu API - `GET /v1/kitchens/{id}/menu` (OpenAI-compatible)
- [x] **SHA-108**: Kitchen model + CRUD endpoints
- [x] **SHA-104**: SSE streaming - `POST /v1/query/stream`
- [x] Full `QueryResult` from `/v1/query` (answer, evidence, metrics)
- [x] **SHA-101**: Docker self-host (`docker-compose.yml`)
- [x] **SHA-103**: Token savings metrics in responses
- [x] **Tickets API**: `POST /v1/kitchens/{id}/tickets` + streaming variant

### Frontend
- [x] Heat distortion shader (WebGL/R3F)
- [x] Steam particles (Canvas 2D)
- [x] Drag & Drop Pantry with Context Bowl
- [x] Token savings dashboard
- [x] Run detail page with step timeline

### SDKs
- [x] TypeScript SDK at `kytchen-web/packages/client/`
- [x] Python SDK at `kytchen-sdk/`

---

## What's Left for v1.0 Launch

### CRITICAL PATH (Must Have)

| Task | Est | Notes |
|------|-----|-------|
| **Deploy to Production** | 2h | Vercel (frontend) + Railway (backend) |
| **Wire Kitchen UI to backend** | 3h | Frontend currently uses workspace, needs Kitchen paradigm |
| ~~**Tickets endpoint**~~ | ~~2h~~ | ✅ DONE: `POST /v1/kitchens/{id}/tickets` + streaming |
| **Connect real SSE to frontend** | 1h | Replace mock in `use-run-stream.ts` |
| **Test end-to-end flow** | 2h | Upload → Create Kitchen → Query → View Results |

### NICE TO HAVE (Polish)

| Task | Est | Notes |
|------|-----|-------|
| Thermal Receipt component | 1h | Zigzag edge, noise texture, VT323 font |
| Sound effects | 30m | clack/print/ding MP3s + useSound hook |
| Landing page copy update | 1h | "Give Your Cursor Agent a Backend" |
| SDK publishing | 2h | PyPI + npm |

---

## Deployment Architecture

```
app.kytchen.dev  → Vercel (Next.js in kytchen-web/)
api.kytchen.dev  → Railway (FastAPI in kytchen/api/)
```

### Vercel Setup
```bash
cd kytchen-web
vercel login
vercel --prod
# Set env: NEXT_PUBLIC_API_URL=https://api.kytchen.dev
```

### Railway Setup
```bash
# Create new project, link to repo
# Set root directory: /
# Set start command: uvicorn kytchen.api.app:app --host 0.0.0.0 --port $PORT
# Set env vars from .env.selfhost
```

---

## Key Files

| File | Purpose |
|------|---------|
| `kytchen/api/routes/kitchens.py` | Kitchen CRUD + Menu API + Tickets |
| `kytchen/api/schemas/ticket.py` | Ticket request/response schemas |
| `kytchen/api/app.py` | FastAPI with streaming endpoints |
| `kytchen-web/lib/hooks/use-run-stream.ts` | SSE hook (needs real endpoint) |
| `kytchen-web/components/pantry/` | Drag & Drop UI |
| `kytchen-web/components/effects/` | Heat shader + Steam |
| `tests/test_menu_api.py` | API integration tests |

---

## Environment Variables Needed

### Backend (.env)
```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
ANTHROPIC_API_KEY=sk-ant-...  # For default provider
KYTCHEN_API_URL=https://api.kytchen.dev
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://api.kytchen.dev
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

---

## Quick Start (Dev Mode)

```bash
# Backend
cd /Volumes/VIXinSSD/kytchen
pip install -e '.[api,mcp]'
KYTCHEN_DEV_MODE=1 uvicorn kytchen.api.app:app --reload --port 8000

# Frontend
cd kytchen-web
npm install
npm run dev
```

---

## Test the Flow

```bash
# 1. Create a Kitchen
curl -X POST http://localhost:8000/v1/kitchens \
  -H "Authorization: Bearer kyt_sk_test" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Kitchen"}'
# Returns: {"id": "kyt_xxx", ...}

# 2. Get the Menu (OpenAI-compatible tools)
curl http://localhost:8000/v1/kitchens/kyt_xxx/menu \
  -H "Authorization: Bearer kyt_sk_test"

# 3. Upload a dataset
curl -X POST http://localhost:8000/v1/datasets \
  -H "Authorization: Bearer kyt_sk_test" \
  -F "name=test" \
  -F "file=@test.txt"
# Returns: {"id": "dataset_id", ...}

# 4. Add dataset to Kitchen's Pantry
curl -X POST http://localhost:8000/v1/kitchens/kyt_xxx/pantry \
  -H "Authorization: Bearer kyt_sk_test" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": "dataset_id"}'

# 5. Fire a Ticket (query) into the Kitchen
curl -X POST http://localhost:8000/v1/kitchens/kyt_xxx/tickets \
  -H "Authorization: Bearer kyt_sk_test" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is in this document?", "provider_api_key": "sk-ant-..."}'

# 6. Fire a Ticket with SSE streaming
curl -X POST http://localhost:8000/v1/kitchens/kyt_xxx/tickets/stream \
  -H "Authorization: Bearer kyt_sk_test" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"query": "What is in this document?", "provider_api_key": "sk-ant-..."}'

# 7. List Tickets (receipts)
curl http://localhost:8000/v1/kitchens/kyt_xxx/tickets \
  -H "Authorization: Bearer kyt_sk_test"
```

---

*Handoff from Claude Opus 4.5 - 2025-12-16*
