import * as React from "react";
import { TokenMetrics } from "@/lib/api/metrics";
import { cn } from "@/lib/utils";
import { ArrowDown, DollarSign, Zap } from "lucide-react";

interface TokenArbitrageProps {
    metrics: TokenMetrics[];
    className?: string;
}

export function TokenArbitrage({ metrics, className }: TokenArbitrageProps) {
    const [id] = React.useState(() => Math.random().toString(36).substring(7).toUpperCase());
    // Calculate aggregates
    const totalBaseline = metrics.reduce((acc, m) => acc + m.baseline_tokens, 0);
    const totalServed = metrics.reduce((acc, m) => acc + m.tokens_served, 0);
    const totalSavedUSD = metrics.reduce((acc, m) => acc + m.cost_saved_usd, 0);
    
    const savingsPercent = totalBaseline > 0 
        ? ((totalBaseline - totalServed) / totalBaseline) * 100 
        : 0;

    return (
        <div className={cn("bg-[#faf9f7] border border-dashed border-[#333] shadow-[2px_2px_0_#000] p-6 font-mono", className)}>
            <div className="flex justify-between items-start mb-6 border-b-2 border-black pb-4">
                <div>
                    <h3 className="text-sm uppercase tracking-widest text-slate-500 mb-1">Efficiency Rating</h3>
                    <div className="text-5xl font-bold tracking-tighter flex items-center gap-2">
                        {savingsPercent.toFixed(1)}%
                        <ArrowDown className="w-8 h-8 text-green-600" />
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-xs uppercase tracking-widest text-slate-500 mb-1">Status</div>
                    <div className="bg-green-100 text-green-800 px-2 py-1 text-xs font-bold border border-green-800 uppercase inline-block">
                        Optimized
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-8 mb-6">
                <div>
                    <div className="text-xs uppercase tracking-widest text-slate-500 mb-2">Token Arbitrage</div>
                    <div className="flex items-baseline gap-2 mb-1">
                        <span className="text-2xl font-bold">{totalServed.toLocaleString()}</span>
                        <span className="text-xs text-slate-400">SERVED</span>
                    </div>
                    <div className="flex items-baseline gap-2 text-slate-400 line-through decoration-slate-400 decoration-2">
                        <span className="text-sm">{totalBaseline.toLocaleString()}</span>
                        <span className="text-[10px]">BASELINE</span>
                    </div>
                </div>
                <div>
                    <div className="text-xs uppercase tracking-widest text-slate-500 mb-2">Cost Recovery</div>
                    <div className="flex items-baseline gap-1">
                        <DollarSign className="w-4 h-4 text-green-600" />
                        <span className="text-2xl font-bold text-green-700">{totalSavedUSD.toFixed(2)}</span>
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">
                        ESTIMATED SAVINGS
                    </div>
                </div>
            </div>

            <div className="bg-black text-white p-3 text-xs uppercase flex justify-between items-center tracking-widest">
                <span className="flex items-center gap-2">
                    <Zap className="w-3 h-3 text-yellow-400" />
                    System Active
                </span>
                <span>ID: {id}</span>
            </div>
        </div>
    );
}
