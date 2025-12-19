"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Terminal, Search, FileText, Bot, Database, ChevronRight } from "lucide-react"

export interface LogEntry {
    id: string
    timestamp: string
    type: "grep" | "read" | "llm" | "db" | "system"
    message: string
    duration?: string
}

const MOCK_LOGS: LogEntry[] = [
    { id: "1", timestamp: "20:42:01.120", type: "system", message: "INIT_PREP_SEQUENCE: Workspace #872" },
    { id: "2", timestamp: "20:42:01.450", type: "db", message: "FETCH context_window (128k limit)" },
    { id: "3", timestamp: "20:42:01.890", type: "grep", message: "SCAN patterns=['liability', 'indemnity'] in /docs", duration: "12ms" },
    { id: "4", timestamp: "20:42:02.100", type: "read", message: "READ legal_contract_v2.pdf (Pages 12-14)" },
    { id: "5", timestamp: "20:42:02.350", type: "system", message: "COMPRESS 45,000 tokens -> 650 tokens" },
    { id: "6", timestamp: "20:42:03.100", type: "llm", message: "POST /v1/chat/completions (Claude 3.5 Sonnet)", duration: "1.2s" },
    { id: "7", timestamp: "20:42:04.400", type: "system", message: "FINAL_OUTPUT_GENERATED" },
]

export function OpenKitchen() {
    const scrollRef = React.useRef<HTMLDivElement>(null)

    React.useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [])

    return (
        <div className="w-full h-full bg-[#0F172A] text-slate-300 font-mono text-xs p-4 rounded-none border-2 border-slate-600 shadow-inner overflow-hidden flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-700 pb-2 mb-2">
                <div className="flex items-center gap-2 text-slate-400">
                    <Terminal className="w-4 h-4" />
                    <span className="uppercase tracking-widest font-bold">The Line</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    <span className="text-[10px] uppercase">Online</span>
                </div>
            </div>

            <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-2 no-scrollbar">
                {MOCK_LOGS.map((log) => (
                    <div key={log.id} className="grid grid-cols-[80px_30px_1fr_auto] gap-2 items-start hover:bg-slate-800/50 p-1 rounded">
                        <span className="opacity-50">{log.timestamp.split(' ')[0]}</span>
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
                        <span>{log.message}</span>
                        {log.duration && <span className="opacity-40 text-[10px]">{log.duration}</span>}
                    </div>
                ))}

                {/* Simulated cursor */}
                <div className="flex items-center gap-2 mt-2 animate-pulse">
                    <ChevronRight className="w-4 h-4 text-green-500" />
                    <span className="w-2 h-4 bg-slate-400"></span>
                </div>
            </div>
        </div>
    )
}
