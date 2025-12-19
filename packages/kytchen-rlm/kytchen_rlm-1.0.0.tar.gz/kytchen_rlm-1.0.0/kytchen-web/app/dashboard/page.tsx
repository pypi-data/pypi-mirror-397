
"use client"

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Plus, Utensils, Flame, ChefHat } from "lucide-react"
import { TicketRail, TicketItem } from "@/components/ui/ticket-rail"
import { ThermalReceipt } from "@/components/ui/thermal-receipt"
import { HeatKnob } from "@/components/ui/heat-knob"
import { Action86 } from "@/components/ui/action-86"
import { toast } from "sonner"
import { OpenKitchen } from "@/components/runs/open-kitchen"
import { SupabaseKytchenService } from "@/services/supabase-api"
import { MetricCard } from "@/services/types"

const MOCK_RECEIPT = {
    title: "Ticket #8673",
    timestamp: "2025-12-15 20:42:12",
    items: [
        { label: "Search Index", value: "3 docs", cost: "50ms" },
        { label: "Context Window", value: "12k toks", cost: "$0.04" },
        { label: "Reasoning Chain", value: "7 steps", cost: "12s" },
        { label: "Final Output", value: "Success" }
    ],
    total: "0m 14s"
}

export default function DashboardPage() {
    const [tickets, setTickets] = React.useState<TicketItem[]>([])
    const [metrics, setMetrics] = React.useState<Record<string, MetricCard>>({})
    const [loading, setLoading] = React.useState(true)

    React.useEffect(() => {
        const loadData = async () => {
            try {
                // Don't set loading on poll
                const [t, mPantry, mFired, mStations] = await Promise.all([
                    SupabaseKytchenService.getTickets(),
                    SupabaseKytchenService.getMetric('pantry'),
                    SupabaseKytchenService.getMetric('fired'),
                    SupabaseKytchenService.getMetric('stations')
                ])
                setTickets(t)
                setMetrics({
                    pantry: mPantry,
                    fired: mFired,
                    stations: mStations
                })
            } catch (error) {
                console.error("Failed to load prep line", error)
                // Only toast on initial load failure or significant error
            } finally {
                setLoading(false)
            }
        }

        loadData()
        const interval = setInterval(loadData, 30000) // Poll every 30s
        return () => clearInterval(interval)
    }, [])

    const handleSpike = async (id: string) => {
        await SupabaseKytchenService.spikeTicket(id)
        setTickets(prev => prev.filter(t => t.id !== id))
        toast.success(`Ticket #${id} spiked. Heard.`)
    }

    return (
        <div className="space-y-8">
            <TicketRail
                tickets={tickets}
                onSpike={handleSpike}
                onOpen={(id) => console.log("Open", id)}
            />

            <div className="flex items-center justify-between">
                <h1 className="font-heading text-6xl uppercase tracking-tighter">Expo Window</h1>
                <Link href="/dashboard/workspaces/new">
                    <Button className="gap-2 text-lg px-6 py-6 shadow-hard">
                        <Plus className="w-5 h-5" /> New Workspace
                    </Button>
                </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="shadow-hard border-2 border-sharpie-black bg-white hover:-translate-y-1 transition-transform">
                    <CardHeader className="border-b-2 border-slate-200 pb-2">
                        <CardTitle className="text-xl flex items-center justify-between">
                            <span>Pantry Load</span>
                            <Utensils className="w-5 h-5 text-slate-400" />
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-6">
                        <div className="text-4xl font-mono font-bold">{loading ? "..." : metrics.pantry?.value} {metrics.pantry?.unit}</div>
                        <p className="text-sm font-mono text-slate-500 mt-2 uppercas tracking-wide">{loading ? "Loading..." : metrics.pantry?.label}</p>
                        <div className="mt-4 pt-4 border-t border-dashed border-slate-300 flex justify-between items-center">
                            <span className="text-xs font-mono uppercase">Top P</span>
                            <div className="scale-75 origin-right">
                                <HeatKnob value={0.7} onChange={() => { }} step={0.1} />
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card className="shadow-hard border-2 border-sharpie-black bg-white hover:-translate-y-1 transition-transform">
                    <CardHeader className="border-b-2 border-slate-200 pb-2">
                        <CardTitle className="text-xl flex items-center justify-between">
                            <span>Tickets Fired</span>
                            <Flame className="w-5 h-5 text-ticket-red" />
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-6">
                        <div className="text-4xl font-mono font-bold">{loading ? "..." : metrics.fired?.value}</div>
                        <p className="text-sm font-mono text-slate-500 mt-2 uppercase tracking-wide">{loading ? "Loading..." : metrics.fired?.label}</p>
                    </CardContent>
                </Card>
                <Card className="shadow-hard border-2 border-sharpie-black bg-white hover:-translate-y-1 transition-transform">
                    <CardHeader className="border-b-2 border-slate-200 pb-2">
                        <CardTitle className="text-xl flex items-center justify-between">
                            <span>Active Stations</span>
                            <ChefHat className="w-5 h-5 text-blue-tape" />
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-6">
                        <div className="text-4xl font-mono font-bold">{loading ? "..." : metrics.stations?.value}</div>
                        <div className="mt-4 text-right">
                            <Action86 onConfirm={() => toast.success("Station 86'd. Heard.")} itemName="Station" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-[500px]">
                <div className="flex flex-col h-full">
                    <h2 className="font-mono text-sm uppercase tracking-widest mb-4 border-b-2 border-sharpie-black pb-2 inline-block">The Line</h2>
                    <div className="flex-1 min-h-0">
                        <OpenKitchen events={[]} status="closed" />
                    </div>
                </div>

                <div className="flex flex-col h-full">
                    <h2 className="font-mono text-sm uppercase tracking-widest mb-4 border-b-2 border-sharpie-black pb-2 inline-block">Chain of Custody</h2>
                    <ThermalReceipt
                        title={MOCK_RECEIPT.title}
                        timestamp={MOCK_RECEIPT.timestamp}
                        items={MOCK_RECEIPT.items}
                        total={MOCK_RECEIPT.total}
                        className="mt-4"
                    />
                </div>
            </div>
        </div>
    )
}
