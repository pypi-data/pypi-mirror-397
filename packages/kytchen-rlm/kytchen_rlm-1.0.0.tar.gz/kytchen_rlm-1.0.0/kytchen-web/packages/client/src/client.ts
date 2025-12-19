import { Datasets } from './datasets';
import { KytchenError, AuthenticationError, NotFoundError } from './errors';
import { TicketCreateParams, TicketListResponse, TicketResponse, TicketStreamEvent } from './types';

export interface ClientOptions {
    apiKey: string;
    baseUrl?: string;
}

export class KytchenClient {
    public datasets: Datasets;
    public tickets: {
        list: (kytchenId: string, opts?: { limit?: number; offset?: number }) => Promise<TicketListResponse>;
        get: (kytchenId: string, ticketId: string) => Promise<TicketResponse>;
        create: (kytchenId: string, body: TicketCreateParams) => Promise<TicketResponse>;
        stream: (kytchenId: string, body: TicketCreateParams) => AsyncGenerator<TicketStreamEvent, void, unknown>;
    };
    private apiKey: string;
    private baseUrl: string;

    constructor(options: ClientOptions) {
        this.apiKey = options.apiKey;
        this.baseUrl = options.baseUrl || 'https://api.kytchen.dev';
        this.datasets = new Datasets(this);

        this.tickets = {
            list: async (kytchenId: string, opts: { limit?: number; offset?: number } = {}) => {
                const limit = opts.limit ?? 50;
                const offset = opts.offset ?? 0;
                return this.request<TicketListResponse>(
                    `/v1/kytchens/${encodeURIComponent(kytchenId)}/tickets?limit=${limit}&offset=${offset}`,
                    { method: 'GET' }
                );
            },
            get: async (kytchenId: string, ticketId: string) => {
                return this.request<TicketResponse>(
                    `/v1/kytchens/${encodeURIComponent(kytchenId)}/tickets/${encodeURIComponent(ticketId)}`,
                    { method: 'GET' }
                );
            },
            create: async (kytchenId: string, body: TicketCreateParams) => {
                return this.request<TicketResponse>(
                    `/v1/kytchens/${encodeURIComponent(kytchenId)}/tickets`,
                    {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(body),
                    }
                );
            },
            stream: (kytchenId: string, body: TicketCreateParams) => this.streamTicket(kytchenId, body),
        };
    }

    private async *streamTicket(
        kytchenId: string,
        body: TicketCreateParams
    ): AsyncGenerator<TicketStreamEvent, void, unknown> {
        const response = await fetch(
            `${this.baseUrl}/v1/kytchens/${encodeURIComponent(kytchenId)}/tickets/stream`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                },
                body: JSON.stringify(body),
            }
        );

        if (!response.ok) {
            throw await this.handleError(response);
        }

        if (!response.body) throw new Error('No response body');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = '';

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                let idx;
                while ((idx = buffer.indexOf('\n\n')) !== -1) {
                    const frame = buffer.slice(0, idx);
                    buffer = buffer.slice(idx + 2);

                    const lines = frame.split('\n');
                    for (const line of lines) {
                        if (!line.startsWith('data: ')) continue;
                        const payload = line.slice(6).trim();
                        if (!payload) continue;

                        try {
                            const data = JSON.parse(payload);
                            yield data as TicketStreamEvent;
                        } catch {
                            // ignore parse errors
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }

    async request<T>(path: string, options: RequestInit = {}): Promise<T> {
        const url = `${this.baseUrl}${path}`;
        const headers = new Headers(options.headers);
        headers.set('Authorization', `Bearer ${this.apiKey}`);

        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (!response.ok) {
            throw await this.handleError(response);
        }

        if (response.status === 204) {
            return {} as T;
        }

        return response.json();
    }

    private async handleError(response: Response): Promise<Error> {
        let message = response.statusText;
        try {
            const errorBody = await response.json();
            if (typeof errorBody?.detail === 'string') message = errorBody.detail;
            else if (typeof errorBody?.message === 'string') message = errorBody.message;
        } catch {} 

        if (response.status === 401) {
            return new AuthenticationError(message);
        }
        if (response.status === 404) {
            return new NotFoundError(message);
        }

        return new KytchenError(message, response.status);
    }
}
