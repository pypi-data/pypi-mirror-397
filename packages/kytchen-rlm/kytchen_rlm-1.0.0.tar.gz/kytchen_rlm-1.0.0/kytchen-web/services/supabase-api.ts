import { createClient } from '@/lib/supabase/client'
import { KytchenService, TicketItem } from './types'

type TicketRow = {
    id: string
    query: string
    status: TicketItem["status"]
    model: string
    logs?: string[] | null
}

export const SupabaseKytchenService: KytchenService = {
    async getTickets() {
        const supabase = createClient()
        const { data, error } = await supabase
            .from('tickets')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(10)

        if (error) throw error

        // Map DB types to UI types
        return (data as unknown as TicketRow[]).map((t) => ({
            id: String(t.id),
            title: String(t.query),
            status: t.status,
            meta: String(t.model),
            annotations: Array.isArray(t.logs) ? t.logs.map((x) => String(x)) : undefined,
        }))
    },

    async getMetric(key: string) {
        const supabase = createClient()

        switch (key) {
            case 'pantry':
                // Mock for now, but formatted correctly
                return { value: "12.5", unit: "MB", label: "of 50 MB" }

            case 'fired':
                const { count: firedCount } = await supabase
                    .from('tickets')
                    .select('*', { count: 'exact', head: true })
                return { value: (firedCount || 0).toString(), label: "Total Tickets" }

            case 'stations':
                // Count tickets that are currently 'cooking'
                const { count: activeCount } = await supabase
                    .from('tickets')
                    .select('*', { count: 'exact', head: true })
                    .eq('status', 'cooking')
                return { value: (activeCount || 0).toString(), label: "Active Stations" }

            default:
                return { value: "-", label: "Unknown" }
        }
    },

    async spikeTicket(id: string) {
        const supabase = createClient()
        await supabase.from('tickets').delete().eq('id', id)
    }
}
