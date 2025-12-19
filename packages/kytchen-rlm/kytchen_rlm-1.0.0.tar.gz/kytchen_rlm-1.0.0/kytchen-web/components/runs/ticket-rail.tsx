"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { ChefHat } from "lucide-react"
import { Action86 } from "@/components/ui/action-86"
import { HeatDistortion } from "@/components/effects"

export interface TicketItem {
    id: string
    title: string
    status: "queued" | "cooking" | "ready" | "error"
    meta: string
    // New prop for annotations
    annotations?: string[]
}

interface TicketRailProps {
    tickets: TicketItem[]
    onSpike: (id: string) => void
    onOpen: (id: string) => void
}

export function TicketRail({ tickets, onSpike, onOpen }: TicketRailProps) {
    const rotationForId = (id: string, maxAbs: number) => {
        let h = 0
        for (let i = 0; i < id.length; i++) {
            h = (h * 31 + id.charCodeAt(i)) | 0
        }
        const u = ((h >>> 0) % 1000) / 1000
        return (u * 2 - 1) * maxAbs
    }

    return (
        <div className="w-full h-32 bg-stone-300 border-b-4 border-stone-400 relative overflow-hidden shadow-inner flex items-start px-4 gap-4 perspective-[1000px]">
            {/* The Rail itself */}
            <div className="absolute top-0 left-0 right-0 h-4 bg-gradient-to-b from-stone-400 to-stone-200 border-b border-stone-500 z-20 shadow-sm" />

            {/* Ball bearings logic visual */}
            <div className="absolute top-3 left-0 right-0 h-1 flex justify-around px-2 z-20 opacity-30">
                {Array.from({ length: 20 }).map((_, i) => (
                    <div key={i} className="w-1.5 h-1.5 rounded-full bg-stone-600 shadow-inner" />
                ))}
            </div>

            <AnimatePresence>
                {tickets.map((ticket) => (
                    <motion.div
                        key={ticket.id}
                        initial={{ y: -100, opacity: 0, rotate: rotationForId(ticket.id, 2) }}
                        animate={{
                            y: 0,
                            opacity: 1,
                            // Simulating "cooking" vibration if status is cooking
                            rotate: ticket.status === 'cooking' ? [0, 1, -1, 0] : rotationForId(ticket.id, 1)
                        }}
                        exit={{ y: 200, opacity: 0, scale: 0.9 }}
                        transition={{
                            type: "spring",
                            stiffness: 300,
                            damping: 20,
                            rotate: {
                                repeat: ticket.status === 'cooking' ? Infinity : 0,
                                duration: 0.2
                            }
                        }}
                        className="relative group z-10 pt-2"
                        // Making it look like it's hanging
                        style={{ transformOrigin: "top center" }}
                    >
                        {/* The Ticket Card with Heat Effect */}
                        <div className="relative">
                            {/* Heat Distortion Overlay - only for cooking status */}
                            <HeatDistortion
                                active={ticket.status === 'cooking'}
                                intensity={0.4}
                            />
                            <div
                                onClick={() => onOpen(ticket.id)}
                                className={cn(
                                "relative w-48 bg-white border-x border-b border-stone-200 shadow-[2px_4px_8px_rgba(0,0,0,0.1)] cursor-pointer transition-transform hover:scale-[1.02]",
                                ticket.status === 'error' && "bg-red-50 border-red-200",
                                // Torn paper effect at bottom css polygon
                                "pb-6 [clip-path:polygon(0%_0%,100%_0%,100%_100%,95%_98%,90%_100%,85%_98%,80%_100%,75%_98%,70%_100%,65%_98%,60%_100%,55%_98%,50%_100%,45%_98%,40%_100%,35%_98%,30%_100%,25%_98%,20%_100%,15%_98%,10%_100%,5%_98%,0%_100%)]"
                            )}
                        >
                            {/* Header stripe */}
                            <div className={cn(
                                "h-1 w-full",
                                ticket.status === 'cooking' && "bg-blue-tape animate-pulse",
                                ticket.status === 'ready' && "bg-green-500",
                                ticket.status === 'error' && "bg-ticket-red",
                                ticket.status === 'queued' && "bg-stone-300"
                            )} />

                            <div className="p-3">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="font-mono text-xs font-bold text-slate-400">#{ticket.id}</span>
                                    {ticket.status === 'cooking' && <ChefHat className="w-3 h-3 text-blue-tape animate-bounce" />}
                                </div>
                                <h4 className="font-heading text-lg leading-tight uppercase mb-1 line-clamp-2">{ticket.title}</h4>
                                <p className="font-mono text-[10px] text-slate-500">{ticket.meta}</p>
                            </div>

                            {/* Handwritten Annotations (New) */}
                            {ticket.annotations && ticket.annotations.length > 0 && (
                                <div className="absolute -right-2 top-8 w-24 flex flex-col gap-1 items-end pointer-events-none opacity-80 rotate-2">
                                    {ticket.annotations.map((note, i) => (
                                        <span key={i} className="font-caveat text-blue-600 text-sm whitespace-nowrap bg-yellow-100/50 px-1 decoration-clone">
                                            {note}
                                        </span>
                                    ))}
                                </div>
                            )}

                            {/* Action 86 Spike Button */}
                            <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity z-20">
                                <Action86
                                    onConfirm={() => onSpike(ticket.id)}
                                    itemName="TKT"
                                    className="bg-white/90 shadow-sm border border-stone-200"
                                />
                            </div>
                            </div>
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>
        </div>
    )
}
