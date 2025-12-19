"use client"

import { TokenMetrics } from "@/lib/api/metrics";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface SavingsChartProps {
    data: TokenMetrics[];
    className?: string;
}

export function SavingsChart({ data, className }: SavingsChartProps) {
    // Sort data by date
    const sortedData = [...data].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

    return (
        <Card className={cn("shadow-hard border-2 border-sharpie-black bg-white", className)}>
            <CardHeader className="border-b-2 border-slate-200 pb-2">
                <CardTitle className="text-xl font-heading uppercase tracking-wide">Usage Timeline</CardTitle>
            </CardHeader>
            <CardContent className="pt-6 h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                        data={sortedData}
                        margin={{
                            top: 10,
                            right: 30,
                            left: 0,
                            bottom: 0,
                        }}
                    >
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                        <XAxis 
                            dataKey="timestamp" 
                            tickFormatter={(value) => new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                            tick={{ fontFamily: 'monospace', fontSize: 10 }}
                            axisLine={false}
                            tickLine={false}
                            dy={10}
                        />
                        <YAxis 
                            tick={{ fontFamily: 'monospace', fontSize: 10 }}
                            axisLine={false}
                            tickLine={false}
                            dx={-10}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Area 
                            type="monotone" 
                            dataKey="baseline_tokens" 
                            stackId="1" 
                            stroke="#94a3b8" 
                            fill="#f1f5f9" 
                            strokeDasharray="5 5"
                        />
                        <Area 
                            type="monotone" 
                            dataKey="tokens_served" 
                            stackId="2" 
                            stroke="#2563EB" 
                            fill="#2563EB" 
                            fillOpacity={0.2}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}

interface TooltipPayload {
    value: number;
    name?: string;
    payload?: unknown;
}

function CustomTooltip({ active, payload, label }: { active?: boolean, payload?: TooltipPayload[], label?: string }) {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#faf9f7] border border-black p-3 shadow-[4px_4px_0_#000] font-mono text-xs">
                <p className="mb-2 font-bold uppercase">{label ? new Date(label).toLocaleDateString() : ''}</p>
                <p className="text-slate-500">
                    Baseline: <span className="text-black font-bold">{payload[0].value.toLocaleString()}</span>
                </p>
                <p className="text-blue-600">
                    Served: <span className="font-bold">{payload[1].value.toLocaleString()}</span>
                </p>
                <p className="text-green-600 mt-1 border-t border-dashed border-slate-300 pt-1">
                    Saved: {((payload[0].value - payload[1].value) / payload[0].value * 100).toFixed(1)}%
                </p>
            </div>
        );
    }
    return null;
}
