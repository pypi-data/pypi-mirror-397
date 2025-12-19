import { useEffect, useState } from 'react';

import type { TicketStreamEvent } from '@/services/kytchen-api';
import { streamTicket } from '@/services/kytchen-api';

export interface RunEvent {
    id: string;
    type: 'grep' | 'read' | 'llm' | 'db' | 'system' | 'step';
    message: string;
    timestamp: string;
    duration?: string;
    metadata?: unknown;
}

export interface UseRunStreamArgs {
    kytchenId: string;
    query: string;
    datasetIds?: string[];
    enabled?: boolean;
}

/** Type-safe accessor for evt.data fields */
function dataField(evt: TicketStreamEvent, key: string): unknown {
    return evt.data[key];
}

function mapTicketStreamEventToRunEvent(evt: TicketStreamEvent): RunEvent | null {
    const ts = new Date(evt.timestamp * 1000).toISOString();
    const id = `${String(dataField(evt, 'id') ?? 'evt')}-${evt.type}-${evt.timestamp}`;

    if (evt.type === 'started') {
        return {
            id,
            type: 'system',
            message: `TICKET_STARTED: ${String(dataField(evt, 'id') ?? '')}`.trim(),
            timestamp: ts,
            metadata: evt,
        };
    }

    if (evt.type === 'completed') {
        return {
            id,
            type: 'system',
            message: 'TICKET_COMPLETED',
            timestamp: ts,
            metadata: evt,
        };
    }

    if (evt.type === 'error') {
        const err = String(dataField(evt, 'error') ?? 'Unknown error');
        return {
            id,
            type: 'system',
            message: `TICKET_ERROR: ${err}`,
            timestamp: ts,
            metadata: evt,
        };
    }

    if (evt.type === 'step') {
        const stepNumber = dataField(evt, 'step_number');
        const actionType = String(dataField(evt, 'action_type') ?? '');
        const action = String(dataField(evt, 'action') ?? '');
        const resultPreview = String(dataField(evt, 'result_preview') ?? '');

        const combined = `${action} ${resultPreview}`.trim();

        let type: RunEvent['type'] = 'step';
        if (actionType === 'code') type = 'db';
        if (/\bsearch\b|\bgrep\b/i.test(combined)) type = 'grep';
        if (/\bpeek\b|\blines\b|\bread\b/i.test(combined)) type = 'read';
        if (/\bllm\b|anthropic|openai|model/i.test(combined)) type = 'llm';

        const prefix = stepNumber != null ? `STEP_${String(stepNumber)}:` : 'STEP:';
        const msg = combined ? `${prefix} ${combined}` : `${prefix} ${actionType}`.trim();

        return {
            id,
            type,
            message: msg,
            timestamp: ts,
            metadata: evt,
        };
    }

    return null;
}

export function useRunStream(args: UseRunStreamArgs) {
    const [events, setEvents] = useState<RunEvent[]>([]);
    const [status, setStatus] = useState<'connecting' | 'connected' | 'error' | 'closed'>('connecting');
    const [runId, setRunId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (args.enabled === false) return;
        if (!args.kytchenId) return;
        if (!args.query) return;

        setEvents([]);
        setRunId(null);
        setError(null);
        setStatus('connecting');

        const abort = new AbortController();

        streamTicket(
            args.kytchenId,
            {
                query: args.query,
                dataset_ids: args.datasetIds,
            },
            (evt) => {
                if (evt.type === 'started') {
                    const ticketId = String(dataField(evt, 'id') ?? '');
                    if (ticketId) setRunId(ticketId);
                    setStatus('connected');
                }

                if (evt.type === 'completed') {
                    setStatus('closed');
                }

                if (evt.type === 'error') {
                    setStatus('error');
                    const err = String(dataField(evt, 'error') ?? 'Unknown error');
                    setError(err);
                }

                const mapped = mapTicketStreamEventToRunEvent(evt);
                if (mapped) {
                    setEvents((prev) => [...prev, mapped]);
                }
            },
            { signal: abort.signal }
        ).catch((e) => {
            if (abort.signal.aborted) return;
            const msg = e instanceof Error ? e.message : 'Stream failed';
            setError(msg);
            setStatus('error');
        });

        return () => abort.abort();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [args.enabled, args.kytchenId, args.query, args.datasetIds?.join(',')]);

    return { events, status, runId, error };
}
