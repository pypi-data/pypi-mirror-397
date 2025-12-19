"use client"

import { cn } from "@/lib/utils";
import { CheckCircle2, Circle, Clock, Loader2 } from "lucide-react";
import { RunEvent } from "@/lib/hooks/use-run-stream";

interface StepTimelineProps {
    events: RunEvent[];
    className?: string;
}

export function StepTimeline({ events, className }: StepTimelineProps) {
    // Filter for major steps if needed, or just show all events as a timeline
    // For this prototype, we'll just show the last 5 events or specific types
    const steps = events.filter(e => ['grep', 'read', 'llm', 'db'].includes(e.type));

    return (
        <div className={cn("space-y-4 font-mono text-sm", className)}>
            {steps.length === 0 && (
                <div className="text-slate-400 italic text-xs">Waiting for steps...</div>
            )}
            {steps.map((step, i) => (
                <div key={step.id} className="flex gap-4 relative">
                    {/* Line */}
                    {i !== steps.length - 1 && (
                        <div className="absolute left-[9px] top-6 bottom-[-16px] w-[2px] bg-slate-200" />
                    )}
                    
                    <div className="flex-none mt-0.5">
                        {i === steps.length - 1 ? (
                            <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                        ) : (
                            <CheckCircle2 className="w-5 h-5 text-green-600" />
                        )}
                    </div>
                    
                    <div className="flex-1 pb-1">
                        <div className="flex justify-between items-baseline mb-1">
                            <span className="font-bold uppercase text-xs tracking-wider text-slate-700">{step.type}</span>
                            <span className="text-[10px] text-slate-400">{new Date(step.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <div className="text-slate-600 text-xs bg-slate-50 p-2 border border-slate-200 rounded">
                            {step.message}
                            {step.duration && <span className="block mt-1 text-[10px] text-slate-400">Duration: {step.duration}</span>}
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
