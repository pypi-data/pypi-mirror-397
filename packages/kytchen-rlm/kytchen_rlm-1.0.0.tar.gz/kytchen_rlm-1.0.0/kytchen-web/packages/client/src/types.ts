export interface Dataset {
  id: string;
  name: string;
  size_bytes: number;
  content_hash: string;
  status: 'uploaded' | 'processing' | 'ready' | 'failed';
  created_at: string;
}

export interface CreateDatasetParams {
    name: string;
    file: File | Blob; // Or specific buffer type for Node
}

export interface TicketMetrics {
    baseline_tokens: number;
    tokens_served: number;
    iterations: number;
    cost_usd: number;
}

export interface TicketResponse {
    id: string;
    kytchen_id: string;
    query: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    answer?: string | null;
    evidence?: unknown[] | null;
    error?: string | null;
    metrics?: TicketMetrics | null;
    created_at: string;
    completed_at?: string | null;
}

export interface TicketListResponse {
    tickets: TicketResponse[];
    total: number;
    has_more: boolean;
}

export interface TicketCreateParams {
    query: string;
    dataset_ids?: string[];
    provider?: string;
    model?: string;
    provider_api_key?: string;
    budget?: Record<string, unknown>;
}

export type TicketStreamEvent = {
    type: 'started' | 'step' | 'completed' | 'error';
    data: Record<string, unknown>;
    timestamp: number;
};
