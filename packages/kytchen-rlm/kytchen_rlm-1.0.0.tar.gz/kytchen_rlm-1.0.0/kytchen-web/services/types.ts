export interface TicketItem {
    id: string
    title: string
    status: "queued" | "cooking" | "ready" | "error"
    meta: string
    annotations?: string[]
}

export interface MetricCard {
    value: string
    label: string
    unit?: string
    meta?: React.ReactNode
}

export interface KytchenService {
    getTickets(): Promise<TicketItem[]>
    getMetric(key: string): Promise<MetricCard>
    spikeTicket(id: string): Promise<void>
}
