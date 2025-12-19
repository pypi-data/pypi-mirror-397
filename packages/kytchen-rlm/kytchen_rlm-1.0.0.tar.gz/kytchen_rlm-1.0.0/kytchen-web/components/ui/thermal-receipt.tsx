import * as React from "react"
import { cn } from "@/lib/utils"

interface ReceiptItem {
    label: string
    value: string | number
    cost?: string
}

interface ThermalReceiptProps {
    title: string
    timestamp: string
    items: ReceiptItem[]
    total?: string
    className?: string
}

export function ThermalReceipt({ title, timestamp, items, total, className }: ThermalReceiptProps) {
    return (
        <div className={cn("relative w-full max-w-sm mx-auto bg-[#fdfbf7] shadow-sm font-mono text-xs text-slate-800 drop-shadow-md", className)}>
            {/* Torn Top */}
            <div
                className="h-3 w-full absolute -top-3 left-0 bg-[#fdfbf7]"
                style={{
                    clipPath: 'polygon(0% 100%, 5% 0%, 10% 100%, 15% 0%, 20% 100%, 25% 0%, 30% 100%, 35% 0%, 40% 100%, 45% 0%, 50% 100%, 55% 0%, 60% 100%, 65% 0%, 70% 100%, 75% 0%, 80% 100%, 85% 0%, 90% 100%, 95% 0%, 100% 100%)'
                }}
            />

            <div className="p-6 pb-8">
                {/* Header */}
                <div className="text-center mb-6 border-b-2 border-slate-800 pb-4 border-dashed">
                    <h3 className="font-heading text-2xl uppercase tracking-tighter mb-1">{title}</h3>
                    <p className="opacity-60 text-[10px] uppercase tracking-widest">{timestamp}</p>
                </div>

                {/* Items */}
                <div className="space-y-3 mb-6">
                    {items.map((item, i) => (
                        <div key={i} className="flex justify-between items-end border-b border-dotted border-slate-300 pb-1">
                            <span className="uppercase">{item.label}</span>
                            <div className="flex gap-4">
                                <span>{item.value}</span>
                                {item.cost && <span className="opacity-50">{item.cost}</span>}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Total */}
                <div className="pt-4 border-t-2 border-slate-800 flex justify-between items-center text-sm font-bold mb-6">
                    <span className="uppercase">Total</span>
                    <span>{total || "---"}</span>
                </div>

                {/* Chain of Custody (New) */}
                <div className="mb-6">
                    <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-2 text-center border-b border-slate-300 pb-1">Chain of Custody</div>
                    <div className="flex justify-between items-center text-[10px]">
                        <span>Audit Hash:</span>
                        <span className="font-mono bg-slate-100 px-1 py-0.5 border border-slate-200">0x7f...a92b</span>
                    </div>
                </div>

                {/* Token Arbitrage (New) */}
                <div className="bg-slate-100 p-3 border border-dashed border-slate-400 text-center mb-6">
                    <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Token Arbitrage</div>
                    <div className="flex justify-between text-xs mb-1">
                        <span>Raw:</span>
                        <span className="line-through opacity-50">50,000</span>
                    </div>
                    <div className="flex justify-between text-xs font-bold text-blue-800">
                        <span>Cooked:</span>
                        <span>500</span>
                    </div>
                    <div className="mt-2 text-[10px] uppercase bg-slate-800 text-white py-1">
                        Savings: $0.45
                    </div>
                </div>

                {/* Barcode Mockup */}
                <div className="opacity-40">
                    <div className="h-8 w-full bg-[url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAQAAAABCAYAAAD5PA/NAAAAFklEQVR42mN88f/rfwYGBgYGEA0DQAQA/QoD6t4+1jMAAAAASUVORK5CYII=')] bg-repeat-x" />
                    <p className="text-center text-[8px] mt-1">KYTCHEN-SYS-86</p>
                </div>
            </div>

            {/* Torn Bottom */}
            <div
                className="h-3 w-full absolute -bottom-3 left-0 bg-[#fdfbf7]"
                style={{
                    clipPath: 'polygon(0% 0%, 5% 100%, 10% 0%, 15% 100%, 20% 0%, 25% 100%, 30% 0%, 35% 100%, 40% 0%, 45% 100%, 50% 0%, 55% 100%, 60% 0%, 65% 100%, 70% 0%, 75% 100%, 80% 0%, 85% 100%, 90% 0%, 95% 100%, 100% 0%)'
                }}
            />
        </div>
    )
}
