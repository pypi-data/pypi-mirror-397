"use client"

import { useEffect, useState } from "react";
import { MetricsApi, TokenMetrics } from "@/lib/api/metrics";
import { TokenArbitrage } from "@/components/savings/token-arbitrage";
import { SavingsChart } from "@/components/savings/savings-chart";
import { ExportButton } from "@/components/savings/export-button";

export default function SavingsPage() {
    const [metrics, setMetrics] = useState<TokenMetrics[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadMetrics = async () => {
            try {
                const data = await MetricsApi.getRuns();
                setMetrics(data);
            } catch (error) {
                console.error("Failed to load metrics", error);
            } finally {
                setLoading(false);
            }
        };

        loadMetrics();
    }, []);

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="font-heading text-6xl uppercase tracking-tighter">Savings</h1>
                    <p className="font-mono text-slate-500 mt-2 uppercase tracking-wide">Token Arbitrage & Efficiency Reports</p>
                </div>
                <ExportButton data={metrics} />
            </div>

            {loading ? (
                <div className="h-64 flex items-center justify-center font-mono text-slate-400 animate-pulse">
                    Calculating Efficiency...
                </div>
            ) : (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-1">
                            <TokenArbitrage metrics={metrics} className="h-full" />
                        </div>
                        <div className="lg:col-span-2">
                             <SavingsChart data={metrics} className="h-full" />
                        </div>
                    </div>

                    <div className="border-t-2 border-black pt-8">
                         <h2 className="font-heading text-3xl uppercase tracking-tighter mb-6">Recent Runs</h2>
                         <div className="bg-white border-2 border-black shadow-[4px_4px_0_#000] overflow-hidden">
                            <table className="w-full font-mono text-sm text-left">
                                <thead className="bg-slate-100 border-b-2 border-black">
                                    <tr>
                                        <th className="p-4 uppercase tracking-widest text-xs">Run ID</th>
                                        <th className="p-4 uppercase tracking-widest text-xs">Date</th>
                                        <th className="p-4 uppercase tracking-widest text-xs text-right">Baseline</th>
                                        <th className="p-4 uppercase tracking-widest text-xs text-right">Served</th>
                                        <th className="p-4 uppercase tracking-widest text-xs text-right">Savings</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {metrics.map((run, i) => (
                                        <tr key={run.run_id} className="border-b border-slate-200 hover:bg-slate-50">
                                            <td className="p-4">{run.run_id}</td>
                                            <td className="p-4">{new Date(run.timestamp).toLocaleDateString()}</td>
                                            <td className="p-4 text-right text-slate-500 line-through decoration-slate-400">{run.baseline_tokens.toLocaleString()}</td>
                                            <td className="p-4 text-right font-bold">{run.tokens_served.toLocaleString()}</td>
                                            <td className="p-4 text-right text-green-600 font-bold">{run.savings_percent.toFixed(1)}%</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                         </div>
                    </div>
                </>
            )}
        </div>
    );
}
