import { KytchenService, TicketItem } from './types'

const MOCK_TICKETS: TicketItem[] = [
    { id: "8675", title: "Analyze Legal Liability in Q3 Report", status: "cooking", meta: "GPT-4o • 45s", annotations: ["grep: 12 hits", "read: pg 12-14"] },
    { id: "8676", title: "Summarize Competitor Pricing", status: "queued", meta: "Claude 3.5" },
    { id: "8674", title: "Extract key dates from compliance docs", status: "error", meta: "Failed to parse PDF", annotations: ["err: 403 Forbidden"] },
]

export const MockKytchenService: KytchenService = {
    async getTickets() {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 500))
        return MOCK_TICKETS
    },

    async getMetric(key: string) {
        switch (key) {
            case 'pantry':
                return { value: "12.5", unit: "MB", label: "of 50 MB (Commis Plan)" }
            case 'fired':
                return { value: "142", label: "Reset in 12 days" }
            case 'stations':
                return { value: "8", label: "Active Stations" }
            default:
                return { value: "-", label: "Unknown" }
        }
    },

    async spikeTicket(id: string) {
        console.log(`Spiked ticket ${id}`)
    }
}
