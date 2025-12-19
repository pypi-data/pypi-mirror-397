"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface Action86Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    onConfirm: () => void
    itemName?: string
}

export function Action86({ onConfirm, itemName = "Item", className, ...props }: Action86Props) {
    const [isDeleting, setIsDeleting] = React.useState(false)

    const handleClick = (e: React.MouseEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setIsDeleting(true)

        // Wait for animation
        setTimeout(() => {
            onConfirm()
            // Reset state in case component isn't unmounted immediately
            setIsDeleting(false)
        }, 600)
    }

    return (
        <div className="relative inline-block">
            <Button
                variant="ghost"
                size="sm"
                onClick={handleClick}
                className={cn(
                    "text-ticket-red hover:bg-red-50 hover:text-red-700 font-mono text-xs uppercase transition-all duration-300",
                    isDeleting && "opacity-50 pointer-events-none",
                    className
                )}
                {...props}
            >
                86 {itemName}
            </Button>

            {/* Strikethrough Animation */}
            <span
                className={cn(
                    "absolute top-1/2 left-0 h-0.5 bg-ticket-red w-0 transition-all duration-500 ease-out pointer-events-none",
                    isDeleting && "w-full"
                )}
                style={{ transform: "translateY(-50%) rotate(-5deg)" }}
            />
        </div>
    )
}
