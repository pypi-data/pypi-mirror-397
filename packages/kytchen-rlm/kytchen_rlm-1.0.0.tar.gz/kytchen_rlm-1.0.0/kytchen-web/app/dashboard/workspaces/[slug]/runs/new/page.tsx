"use client"

import * as React from "react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ArrowLeft } from "lucide-react"
import { OpenKitchen } from "@/components/runs/open-kitchen"
import { StepTimeline } from "@/components/runs/step-timeline"
import { useRunStream } from "@/lib/hooks/use-run-stream"
import { addDatasetToPantry, ensureKytchenForWorkspaceSlug } from "@/services/kytchen-api"

export default function NewRunPage({ params }: { params: { slug: string } }) {
    const searchParams = useSearchParams()
    const datasetIds = React.useMemo(() => {
        const raw = searchParams.get("datasets")
        if (!raw) return []
        return raw
            .split(",")
            .map((x) => x.trim())
            .filter(Boolean)
    }, [searchParams])

    const [kytchenId, setKytchenId] = React.useState<string>("")
    const [query, setQuery] = React.useState("")
    const [submittedQuery, setSubmittedQuery] = React.useState<string | null>(null)
    const [isPreparing, setIsPreparing] = React.useState(false)
    const [prepError, setPrepError] = React.useState<string | null>(null)

    React.useEffect(() => {
        let cancelled = false

        const prepare = async () => {
            try {
                setPrepError(null)
                setIsPreparing(true)

                const kytchen = await ensureKytchenForWorkspaceSlug(params.slug)
                if (cancelled) return
                setKytchenId(kytchen.id)

                for (const datasetId of datasetIds) {
                    await addDatasetToPantry(kytchen.id, datasetId)
                }
            } catch (e) {
                if (cancelled) return
                setPrepError(e instanceof Error ? e.message : "Failed to prepare run")
            } finally {
                if (cancelled) return
                setIsPreparing(false)
            }
        }

        prepare()
        return () => {
            cancelled = true
        }
    }, [params.slug, datasetIds.join(",")])

    const { events, status, runId, error } = useRunStream({
        kytchenId,
        query: submittedQuery || "",
        datasetIds: datasetIds.length > 0 ? datasetIds : undefined,
        enabled: Boolean(submittedQuery),
    })

    React.useEffect(() => {
        if (status === "closed" || status === "error") {
            setSubmittedQuery((prev) => prev)
        }
    }, [status])

    const canFire = !isPreparing && Boolean(kytchenId) && query.trim().length > 0 && !submittedQuery

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-4">
                <Link href={`/dashboard/workspaces/${params.slug}/runs`}>
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="w-5 h-5" />
                    </Button>
                </Link>
                <div className="flex-1">
                    <h1 className="font-heading text-4xl uppercase tracking-tighter">New Run</h1>
                    <p className="font-mono text-xs uppercase text-muted-foreground">
                        Station: {params.slug}
                    </p>
                </div>
            </div>

            <div className="space-y-3">
                <Input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question..."
                    disabled={Boolean(submittedQuery)}
                />

                <div className="flex items-center justify-between">
                    <div className="font-mono text-xs text-muted-foreground">
                        {datasetIds.length > 0 ? `${datasetIds.length} datasets selected` : "No datasets selected"}
                    </div>
                    <Button
                        className="gap-2"
                        disabled={!canFire}
                        onClick={() => setSubmittedQuery(query.trim())}
                    >
                        Fire Ticket
                    </Button>
                </div>

                {isPreparing && (
                    <div className="border border-foreground bg-background p-4 font-mono text-sm text-muted-foreground">
                        Preparing...
                    </div>
                )}

                {prepError && (
                    <div className="border border-foreground bg-background p-4 font-mono text-sm text-ticket-red">
                        {prepError}
                    </div>
                )}

                {error && (
                    <div className="border border-foreground bg-background p-4 font-mono text-sm text-ticket-red">
                        {error}
                    </div>
                )}

                {runId && (
                    <div className="border border-foreground bg-background p-4 font-mono text-sm">
                        Run ID: <span className="font-bold">{runId}</span>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[600px]">
                <div className="lg:col-span-2 flex flex-col h-full">
                    <h2 className="font-mono text-sm uppercase tracking-widest mb-4 border-b-2 border-sharpie-black pb-2 inline-block">
                        The Line
                    </h2>
                    <div className="flex-1 min-h-0 border-2 border-black shadow-[4px_4px_0_#000]">
                        <OpenKitchen runId={runId || undefined} events={events} status={status} />
                    </div>
                </div>

                <div className="flex flex-col h-full overflow-hidden">
                    <h2 className="font-mono text-sm uppercase tracking-widest mb-4 border-b-2 border-sharpie-black pb-2 inline-block">
                        Prep Sequence
                    </h2>
                    <div className="flex-1 overflow-y-auto pr-2 bg-slate-50 border border-slate-200 p-4 shadow-inner">
                        <StepTimeline events={events} />
                    </div>
                </div>
            </div>
        </div>
    )
}
