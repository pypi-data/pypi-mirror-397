"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Terminal, Search, FileText, Bot, Database, ChevronRight } from "lucide-react"
import type { RunEvent } from "@/lib/hooks/use-run-stream"

interface OpenKitchenProps {
    runId?: string;
    events: RunEvent[];
    status: 'connecting' | 'connected' | 'error' | 'closed';
    className?: string;
}

export function OpenKitchen({ runId, events, status, className }: OpenKitchenProps) {
    const scrollRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [events]);

    return (
        <div className={cn("w-full h-full bg-[#0F172A] text-slate-300 font-mono text-xs p-4 rounded-none border-2 border-slate-600 shadow-inner overflow-hidden flex flex-col", className)}>
            <div className="flex items-center justify-between border-b border-slate-700 pb-2 mb-2">
                <div className="flex items-center gap-2 text-slate-400">
                    <Terminal className="w-4 h-4" />
                    <span className="uppercase tracking-widest font-bold">The Line{runId ? `: #${runId}` : ''}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className={cn("w-2 h-2 rounded-full", status === 'connected' ? "bg-green-500 animate-pulse" : "bg-slate-500")}></span>
                    <span className="text-[10px] uppercase">{status}</span>
                </div>
            </div>

            <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-2 no-scrollbar">
                {events.length === 0 && (
                     <div className="text-slate-600 italic">Waiting for signal...</div>
                )}
                {events.map((log) => (
                    <div key={log.id} className="grid grid-cols-[80px_30px_1fr_auto] gap-2 items-start hover:bg-slate-800/50 p-1 rounded animate-in fade-in slide-in-from-left-2 duration-300">
                        <span className="opacity-50">{new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3 })}</span>
                        <span className={cn(
                            "flex justify-center",
                            log.type === 'grep' && "text-yellow-400",
                            log.type === 'llm' && "text-blue-400",
                            log.type === 'read' && "text-green-400",
                            log.type === 'db' && "text-purple-400",
                            log.type === 'system' && "text-slate-500"
                        )}>
                            {log.type === 'grep' && <Search className="w-3 h-3" />}
                            {log.type === 'llm' && <Bot className="w-3 h-3" />}
                            {log.type === 'read' && <FileText className="w-3 h-3" />}
                            {log.type === 'db' && <Database className="w-3 h-3" />}
                            {log.type === 'system' && <Terminal className="w-3 h-3" />}
                        </span>
                        <span className="break-all">{log.message}</span>
                        {log.duration && <span className="opacity-40 text-[10px] whitespace-nowrap">{log.duration}</span>}
                    </div>
                ))}

                {/* Simulated cursor */}
                {status === 'connected' && (
                    <div className="flex items-center gap-2 mt-2 animate-pulse">
                        <ChevronRight className="w-4 h-4 text-green-500" />
                        <span className="w-2 h-4 bg-slate-400"></span>
                    </div>
                )}
            </div>
        </div>
    );
}
