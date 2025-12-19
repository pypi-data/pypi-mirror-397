"use client"

import * as React from "react"
import { useParams } from "next/navigation";
import { OpenKitchen } from "@/components/runs/open-kitchen";
import { TicketRail, TicketItem } from "@/components/runs/ticket-rail";
import { StepTimeline } from "@/components/runs/step-timeline";
import { LiveIndicator } from "@/components/live-indicator";
import { useRunStream } from "@/lib/hooks/use-run-stream";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Share2, Download } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function RunDetailPage() {
    const params = useParams();
    const runId = params?.id as string || "unknown";
    const { events, status } = useRunStream({
        kytchenId: "",
        query: "",
        enabled: false,
    });
    
    // Mock ticket for the rail
    const [ticket, setTicket] = React.useState<TicketItem>({
        id: runId,
        title: "Contract Analysis: Indemnity Clauses",
        status: "cooking",
        meta: "gpt-4-turbo | 128k context",
        annotations: ["Processing...", "Reading Docs"]
    });

    React.useEffect(() => {
        if (status === 'closed') {
            setTicket(prev => ({
                ...prev,
                status: 'ready',
                annotations: ['Done', 'Saved 89% Tokens']
            }));
        }
    }, [status]);

    const handleSpike = (id: string) => {
        toast.success(`Run #${id} spiked.`);
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/dashboard">
                        <Button variant="ghost" size="icon">
                            <ArrowLeft className="w-5 h-5" />
                        </Button>
                    </Link>
                    <div>
                        <div className="flex items-center gap-3">
                            <h1 className="font-heading text-4xl uppercase tracking-tighter">Run #{runId}</h1>
                            {status === 'connected' && <LiveIndicator />}
                        </div>
                        <p className="font-mono text-sm text-slate-500 uppercase tracking-wide">
                            Started {new Date().toLocaleDateString()} | {status}
                        </p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" className="gap-2 border-black">
                        <Share2 className="w-4 h-4" /> Share
                    </Button>
                    <Button variant="outline" className="gap-2 border-black">
                        <Download className="w-4 h-4" /> Log
                    </Button>
                </div>
            </div>

            {/* Ticket Rail Single View */}
            <div className="h-40 -mx-4 sm:mx-0 overflow-hidden">
                <TicketRail 
                    tickets={[ticket]} 
                    onSpike={handleSpike}
                    onOpen={() => {}} 
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[600px]">
                {/* Main: Live Terminal */}
                <div className="lg:col-span-2 flex flex-col h-full">
                    <h2 className="font-mono text-sm uppercase tracking-widest mb-4 border-b-2 border-sharpie-black pb-2 inline-block">
                        The Line
                    </h2>
                    <div className="flex-1 min-h-0 border-2 border-black shadow-[4px_4px_0_#000]">
                        <OpenKitchen runId={runId} events={events} status={status} />
                    </div>
                </div>

                {/* Sidebar: Timeline & Stats */}
                <div className="flex flex-col h-full overflow-hidden">
                    <h2 className="font-mono text-sm uppercase tracking-widest mb-4 border-b-2 border-sharpie-black pb-2 inline-block">
                        Prep Sequence
                    </h2>
                    <div className="flex-1 overflow-y-auto pr-2 bg-slate-50 border border-slate-200 p-4 shadow-inner">
                        <StepTimeline events={events} />
                    </div>
                    
                    {/* Live Stats Box */}
                    <div className="mt-6 bg-[#faf9f7] border border-black p-4 shadow-[2px_2px_0_#000]">
                        <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-2">Current Efficiency</div>
                        <div className="flex justify-between items-baseline mb-1">
                            <span className="text-3xl font-bold font-mono">87%</span>
                            <span className="text-xs text-green-600 font-bold">OPTIMIZED</span>
                        </div>
                        <div className="w-full bg-slate-200 h-1.5 mt-2">
                            <div className="bg-black h-1.5 w-[87%]"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
