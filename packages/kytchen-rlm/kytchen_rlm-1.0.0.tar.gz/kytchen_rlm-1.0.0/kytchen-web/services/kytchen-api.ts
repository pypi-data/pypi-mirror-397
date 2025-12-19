export type KytchenId = string

export interface KytchenResponse {
  id: string
  slug: string
  name: string
  description?: string | null
  visibility?: string
  forked_from?: string | null
  created_at?: string
  updated_at?: string
  dataset_count?: number
  total_size_bytes?: number
}

export interface KytchenListResponse {
  kytchens: KytchenResponse[]
  total: number
  has_more: boolean
}

export interface TicketMetrics {
  baseline_tokens: number
  tokens_served: number
  iterations: number
  cost_usd: number
}

export interface TicketResponse {
  id: string
  kytchen_id: string
  query: string
  status: "pending" | "running" | "completed" | "failed"
  answer?: string | null
  evidence?: unknown[] | null
  error?: string | null
  metrics?: TicketMetrics | null
  created_at: string
  completed_at?: string | null
}

export interface TicketListResponse {
  tickets: TicketResponse[]
  total: number
  has_more: boolean
}

export interface TicketCreateBody {
  query: string
  dataset_ids?: string[]
  provider?: string
  model?: string
  provider_api_key?: string
  budget?: Record<string, unknown>
}

export type TicketStreamEvent = {
  type: "started" | "step" | "completed" | "error"
  data: Record<string, unknown>
  timestamp: number
}

export function getKytchenApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_KYTCHEN_API_URL || "http://localhost:8000"
}

export function getKytchenApiKey(): string {
  if (typeof window !== "undefined") {
    const fromStorage = window.localStorage.getItem("KYTCHEN_API_KEY")
    if (fromStorage && fromStorage.startsWith("kyt_sk_")) return fromStorage
  }

  const fromEnv = process.env.NEXT_PUBLIC_KYTCHEN_API_KEY
  if (fromEnv && fromEnv.startsWith("kyt_sk_")) return fromEnv

  throw new Error(
    "Missing KYTCHEN API key. Set localStorage['KYTCHEN_API_KEY']=kyt_sk_... or NEXT_PUBLIC_KYTCHEN_API_KEY."
  )
}

async function apiFetchJson<T>(
  path: string,
  init: RequestInit & { apiKey?: string; baseUrl?: string } = {}
): Promise<T> {
  const baseUrl = init.baseUrl || getKytchenApiBaseUrl()
  const apiKey = init.apiKey || getKytchenApiKey()

  const headers = new Headers(init.headers)
  headers.set("Authorization", `Bearer ${apiKey}`)
  headers.set("Accept", "application/json")

  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers,
  })

  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = await response.json()
      if (typeof body?.detail === "string") detail = body.detail
      if (typeof body?.error === "string") detail = body.error
    } catch {
      // ignore
    }
    throw new Error(`${response.status} ${detail}`)
  }

  return (await response.json()) as T
}

export async function ensureKytchenForWorkspaceSlug(
  slug: string,
  opts: { apiKey?: string; baseUrl?: string } = {}
): Promise<KytchenResponse> {
  const list = await apiFetchJson<KytchenListResponse>("/v1/kytchens", {
    method: "GET",
    apiKey: opts.apiKey,
    baseUrl: opts.baseUrl,
  })

  const existing = list.kytchens.find((k) => k.slug === slug)
  if (existing) return existing

  try {
    return await apiFetchJson<KytchenResponse>("/v1/kytchens", {
      method: "POST",
      apiKey: opts.apiKey,
      baseUrl: opts.baseUrl,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: slug }),
    })
  } catch {
    const safeName = slug.replace(/[^a-z0-9-]+/gi, "-").replace(/-+/g, "-")
    return apiFetchJson<KytchenResponse>("/v1/kytchens", {
      method: "POST",
      apiKey: opts.apiKey,
      baseUrl: opts.baseUrl,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: safeName || "workspace" }),
    })
  }
}

export async function listTickets(
  kytchenId: KytchenId,
  opts: { apiKey?: string; baseUrl?: string; limit?: number; offset?: number } = {}
): Promise<TicketListResponse> {
  const limit = opts.limit ?? 50
  const offset = opts.offset ?? 0
  return apiFetchJson<TicketListResponse>(
    `/v1/kytchens/${encodeURIComponent(kytchenId)}/tickets?limit=${limit}&offset=${offset}`,
    {
      method: "GET",
      apiKey: opts.apiKey,
      baseUrl: opts.baseUrl,
    }
  )
}

export async function getTicket(
  kytchenId: KytchenId,
  ticketId: string,
  opts: { apiKey?: string; baseUrl?: string } = {}
): Promise<TicketResponse> {
  return apiFetchJson<TicketResponse>(
    `/v1/kytchens/${encodeURIComponent(kytchenId)}/tickets/${encodeURIComponent(ticketId)}`,
    {
      method: "GET",
      apiKey: opts.apiKey,
      baseUrl: opts.baseUrl,
    }
  )
}

export async function addDatasetToPantry(
  kytchenId: KytchenId,
  datasetId: string,
  opts: { apiKey?: string; baseUrl?: string } = {}
): Promise<void> {
  try {
    await apiFetchJson(`/v1/kytchens/${encodeURIComponent(kytchenId)}/pantry`, {
      method: "POST",
      apiKey: opts.apiKey,
      baseUrl: opts.baseUrl,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: datasetId }),
    })
  } catch (e) {
    // 409 = already in pantry. Treat as success.
    if (e instanceof Error && e.message.startsWith("409 ")) return
    throw e
  }
}

export async function streamTicket(
  kytchenId: KytchenId,
  body: TicketCreateBody,
  onEvent: (evt: TicketStreamEvent) => void,
  opts: { apiKey?: string; baseUrl?: string; signal?: AbortSignal } = {}
): Promise<void> {
  const baseUrl = opts.baseUrl || getKytchenApiBaseUrl()
  const apiKey = opts.apiKey || getKytchenApiKey()

  const response = await fetch(`${baseUrl}/v1/kytchens/${encodeURIComponent(kytchenId)}/tickets/stream`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(body),
    signal: opts.signal,
  })

  if (!response.ok) {
    let detail = response.statusText
    try {
      const json = await response.json()
      if (typeof json?.detail === "string") detail = json.detail
    } catch {
      // ignore
    }
    throw new Error(`${response.status} ${detail}`)
  }

  if (!response.body) {
    throw new Error("No response body")
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  let buffer = ""

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // SSE frames are separated by a blank line
      let idx
      while ((idx = buffer.indexOf("\n\n")) !== -1) {
        const frame = buffer.slice(0, idx)
        buffer = buffer.slice(idx + 2)

        const lines = frame.split("\n")
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          const payload = line.slice(6).trim()
          if (!payload) continue
          try {
            const evt = JSON.parse(payload) as TicketStreamEvent
            onEvent(evt)
          } catch {
            // ignore parse errors
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}
