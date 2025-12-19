"use client"

import * as React from "react"

interface HeatKnobProps {
    value: number
    min?: number
    max?: number
    step?: number
    label?: string
    onChange: (value: number) => void
}

export function HeatKnob({ value, min = 0, max = 1, step = 0.1, label, onChange }: HeatKnobProps) {
    const [isDragging, setIsDragging] = React.useState(false)
    const [startY, setStartY] = React.useState(0)
    const startValue = React.useRef(value)

    React.useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!isDragging) return
            const dy = startY - e.clientY
            const range = max - min
            const change = (dy / 200) * range // 200px drag for full range
            let newValue = Math.min(max, Math.max(min, startValue.current + change))

            // Snap to step
            if (step) {
                newValue = Math.round(newValue / step) * step
            }

            onChange(Number(newValue.toFixed(2)))
        }

        const handleMouseUp = () => {
            setIsDragging(false)
            document.body.style.cursor = 'default'
        }

        if (isDragging) {
            window.addEventListener('mousemove', handleMouseMove)
            window.addEventListener('mouseup', handleMouseUp)
            document.body.style.cursor = 'ns-resize'
        }

        return () => {
            window.removeEventListener('mousemove', handleMouseMove)
            window.removeEventListener('mouseup', handleMouseUp)
        }
    }, [isDragging, startY, min, max, step, onChange])

    const handleMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true)
        setStartY(e.clientY)
        startValue.current = value
    }

    // Calculate rotation: -135deg (min) to 135deg (max)
    const percentage = (value - min) / (max - min)
    const rotation = -135 + (percentage * 270)

    // Heat color: Blue (cool) to Red (hot)
    // 0 = #2563EB (Blue Tape)
    // 1 = #EF4444 (Ticket Red)
    // Interpolation roughly
    const heatColor = percentage > 0.5
        ? `rgba(239, 68, 68, ${percentage})`
        : `rgba(37, 99, 235, ${1 - percentage})`

    return (
        <div className="flex flex-col items-center gap-2 group cursor-ns-resize select-none" onMouseDown={handleMouseDown}>
            <div className="relative w-16 h-16 rounded-full bg-stone-200 border-2 border-slate-300 shadow-sm flex items-center justify-center transition-all group-hover:border-slate-400 group-active:scale-95 group-active:border-slate-500">
                {/* Glow Container */}
                <div
                    className="absolute inset-0 rounded-full opacity-20 transition-colors duration-300"
                    style={{ backgroundColor: heatColor, boxShadow: `0 0 15px ${heatColor}` }}
                />

                {/* The Knob */}
                <div
                    className="w-full h-full rounded-full relative"
                    style={{ transform: `rotate(${rotation}deg)` }}
                >
                    {/* Tick Mark */}
                    <div className="absolute top-2 left-1/2 -translate-x-1/2 w-1.5 h-3 bg-slate-800 rounded-sm" />
                </div>
            </div>
            {label && (
                <div className="text-center font-mono text-[10px] uppercase tracking-widest text-slate-500">
                    <span className="block mb-0.5">{label}</span>
                    <span className="text-slate-900 font-bold">{value}</span>
                </div>
            )}
        </div>
    )
}
