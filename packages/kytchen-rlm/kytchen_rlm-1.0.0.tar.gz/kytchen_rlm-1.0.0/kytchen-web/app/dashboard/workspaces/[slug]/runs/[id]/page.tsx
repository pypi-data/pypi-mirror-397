"use client"

import * as React from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { ensureKytchenForWorkspaceSlug, getTicket } from "@/services/kytchen-api"

export default function RunDetailPage({ params }: { params: { slug: string; id: string } }) {
   const [isLoading, setIsLoading] = React.useState(true)
   const [error, setError] = React.useState<string | null>(null)
   const [run, setRun] = React.useState<{
      id: string
      query: string
      status: "pending" | "running" | "completed" | "failed"
      answer?: string | null
      error?: string | null
      metrics?: {
         baseline_tokens: number
         tokens_served: number
         iterations: number
         cost_usd: number
      } | null
      created_at?: string
      completed_at?: string | null
   } | null>(null)

   React.useEffect(() => {
      let cancelled = false

      const load = async () => {
         try {
            setError(null)
            setIsLoading(true)

            const kytchen = await ensureKytchenForWorkspaceSlug(params.slug)
            const ticket = await getTicket(kytchen.id, params.id)

            if (cancelled) return

            setRun({
               id: ticket.id,
               query: ticket.query,
               status: ticket.status,
               answer: ticket.answer ?? null,
               error: ticket.error ?? null,
               metrics: ticket.metrics ?? null,
               created_at: ticket.created_at,
               completed_at: ticket.completed_at ?? null,
            })
         } catch (e) {
            if (cancelled) return
            setError(e instanceof Error ? e.message : "Failed to load run")
         } finally {
            if (cancelled) return
            setIsLoading(false)
         }
      }

      load()
      return () => {
         cancelled = true
      }
   }, [params.slug, params.id])

   const status = run?.status || "pending"
   const badgeVariant: "default" | "destructive" = status === "failed" ? "destructive" : "default"
   const badgeText = status.toUpperCase()

   const timeline = run?.metrics
      ? [
           {
              name: "iterations",
              detail: String(run.metrics.iterations),
           },
           {
              name: "tokens",
              detail: `${run.metrics.tokens_served} / baseline ${run.metrics.baseline_tokens}`,
           },
           {
              name: "cost_usd",
              detail: String(run.metrics.cost_usd),
           },
        ]
      : []

   return (
      <div className="space-y-8 max-w-5xl mx-auto">
         <div className="flex items-center gap-4 mb-8">
            <Link href={`/dashboard/workspaces/${params.slug}/runs`}>
               <Button variant="ghost" size="icon">
                  <ArrowLeft className="w-4 h-4" />
               </Button>
            </Link>
            <div className="flex items-center gap-2">
               <span className="font-mono text-xs uppercase text-muted-foreground">Run ID: {params.id}</span>
               <Badge variant={badgeVariant}>{badgeText}</Badge>
            </div>
         </div>

         {/* Query */}
         <div className="border-b border-foreground pb-8">
            <h1 className="font-serif text-3xl md:text-4xl leading-tight">
               {isLoading ? "Loading..." : error ? "Failed to load" : `\"${run?.query || ""}\"`}
            </h1>
         </div>

         <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            {/* Main Content: Answer & Evidence */}
            <div className="lg:col-span-2 space-y-12">

               {error && (
                  <div className="border border-foreground p-4 font-mono text-sm text-ticket-red">
                     {error}
                  </div>
               )}

               {/* Final Answer */}
               <div className="bg-foreground text-background p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,0.2)]">
                  <h2 className="font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Final Synthesis</h2>
                  <div className="font-serif text-lg whitespace-pre-wrap">
                     {isLoading
                        ? "Loading..."
                        : run?.status === "failed"
                          ? run?.error || "Run failed"
                          : run?.answer || ""}
                  </div>
               </div>

               {/* Evidence */}
               <div>
                  <h2 className="font-mono text-xs uppercase tracking-widest mb-4">Cited Evidence</h2>
                  <div className="border border-foreground p-4 font-mono text-sm text-muted-foreground">
                     Evidence is not persisted for v1 tickets yet.
                  </div>
               </div>
            </div>

            {/* Sidebar: Timeline */}
            <div className="lg:col-span-1">
               <div className="sticky top-24">
                  <h2 className="font-mono text-xs uppercase tracking-widest mb-6">Execution Timeline</h2>
                  <div className="border-l-2 border-foreground pl-6 space-y-8">
                     {timeline.length === 0 && (
                        <div className="font-mono text-xs text-muted-foreground">
                           No timeline available.
                        </div>
                     )}
                     {timeline.map((step, i) => (
                        <div key={`${step.name}-${i}`} className="relative group">
                           <div className="absolute -left-[31px] w-4 h-4 bg-foreground group-hover:scale-125 transition-transform"></div>
                           <div className="font-mono text-xs uppercase mb-1 font-bold">{step.name}</div>
                           <div className="font-mono text-xs opacity-70 border-l border-foreground/20 pl-2">
                              {step.detail}
                           </div>
                        </div>
                     ))}
                     <div className="relative">
                        <div className="absolute -left-[31px] w-4 h-4 border-2 border-foreground bg-background"></div>
                        <div className="font-mono text-xs uppercase mb-2">COMPLETE</div>
                     </div>
                  </div>
               </div>
            </div>
         </div>
      </div>
   )
}
