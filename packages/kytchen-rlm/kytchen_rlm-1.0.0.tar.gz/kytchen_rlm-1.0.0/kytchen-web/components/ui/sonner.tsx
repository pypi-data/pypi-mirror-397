"use client"

import { useTheme } from "next-themes"
import { Toaster as Sonner } from "sonner"
import { Check, X } from "lucide-react"

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
    const { theme = "system" } = useTheme()

    return (
        <Sonner
            theme={theme as ToasterProps["theme"]}
            className="toaster group font-mono"
            toastOptions={{
                classNames: {
                    toast:
                        "group toast group-[.toaster]:bg-white group-[.toaster]:text-sharpie-black group-[.toaster]:border-2 group-[.toaster]:border-sharpie-black group-[.toaster]:shadow-hard group-[.toaster]:rounded-none group-[.toaster]:p-4",
                    description: "group-[.toast]:text-slate-500",
                    actionButton:
                        "group-[.toast]:bg-blue-tape group-[.toast]:text-white",
                    cancelButton:
                        "group-[.toast]:bg-stone-200 group-[.toast]:text-slate-700",
                    error: "group-[.toast]:border-ticket-red group-[.toast]:text-ticket-red",
                    success: "group-[.toast]:border-blue-tape",
                },
            }}
            icons={{
                success: <div className="bg-blue-tape text-white p-0.5 mr-2"><Check className="w-3 h-3" /></div>,
                error: <div className="bg-ticket-red text-white p-0.5 mr-2"><X className="w-3 h-3" /></div>,
            }}
            {...props}
        />
    )
}

export { Toaster }
