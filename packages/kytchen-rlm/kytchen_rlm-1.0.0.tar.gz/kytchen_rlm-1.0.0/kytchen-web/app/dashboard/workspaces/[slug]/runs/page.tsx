"use client"

import * as React from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Play, ArrowRight, Clock } from "lucide-react"
import { ensureKytchenForWorkspaceSlug, listTickets } from "@/services/kytchen-api"

export default function RunsPage({ params }: { params: { slug: string } }) {
    const [runs, setRuns] = React.useState<
        { id: string; query: string; status: "completed" | "failed" | "running" | "pending"; time: string; date: string }[]
    >([])
    const [isLoading, setIsLoading] = React.useState(true)
    const [error, setError] = React.useState<string | null>(null)

    React.useEffect(() => {
        let cancelled = false

        const load = async () => {
            try {
                setError(null)
                setIsLoading(true)

                const kytchen = await ensureKytchenForWorkspaceSlug(params.slug)
                const res = await listTickets(kytchen.id)

                if (cancelled) return

                setRuns(
                    res.tickets.map((t) => {
                        const createdAt = new Date(t.created_at)
                        const completedAt = t.completed_at ? new Date(t.completed_at) : null
                        const seconds = completedAt
                            ? Math.max(0, Math.round((completedAt.getTime() - createdAt.getTime()) / 1000))
                            : null

                        return {
                            id: t.id,
                            query: t.query,
                            status: t.status,
                            time: seconds != null ? `${seconds}s` : "-",
                            date: createdAt.toLocaleString(),
                        }
                    })
                )
            } catch (e) {
                if (cancelled) return
                setError(e instanceof Error ? e.message : "Failed to load runs")
            } finally {
                if (cancelled) return
                setIsLoading(false)
            }
        }

        load()
        return () => {
            cancelled = true
        }
    }, [params.slug])

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h1 className="font-serif text-3xl">Runs History</h1>
                <Link href={`/dashboard/workspaces/${params.slug}/runs/new`}>
                    <Button className="gap-2">
                        <Play className="w-4 h-4" /> New Run
                    </Button>
                </Link>
            </div>

            <div className="space-y-4">
                {error && (
                    <div className="border border-foreground bg-background p-4 font-mono text-sm text-ticket-red">
                        {error}
                    </div>
                )}

                {!error && isLoading && (
                    <div className="border border-foreground bg-background p-4 font-mono text-sm text-muted-foreground">
                        Loading runs...
                    </div>
                )}

                {!error && !isLoading && runs.length === 0 && (
                    <div className="border border-foreground bg-background p-4 font-mono text-sm text-muted-foreground">
                        No runs yet.
                    </div>
                )}

                {runs.map((run) => (
                    <Link key={run.id} href={`/dashboard/workspaces/${params.slug}/runs/${run.id}`}>
                        <div className="group border border-foreground bg-background p-4 flex items-center justify-between hover:bg-surface-elevated transition-none cursor-pointer shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                            <div className="space-y-1">
                                <p className="font-serif text-lg truncate max-w-xl font-medium group-hover:underline decoration-1 underline-offset-4">{run.query}</p>
                                <div className="flex items-center gap-4 text-xs font-mono text-muted-foreground">
                                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {run.time}</span>
                                    <span>{run.date}</span>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <Badge variant={run.status === 'completed' ? 'default' : 'destructive'}>
                                    {run.status.toUpperCase()}
                                </Badge>
                                <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-none" />
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    )
}
