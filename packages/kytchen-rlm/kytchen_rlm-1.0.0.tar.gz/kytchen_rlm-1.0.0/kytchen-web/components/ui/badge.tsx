import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
    "inline-flex items-center border px-2 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 font-mono uppercase tracking-wider rounded-none shadow-sm rotate-1",
    {
        variants: {
            variant: {
                default:
                    "border-transparent bg-blue-tape text-white hover:bg-blue-700 shadow-sm",
                secondary:
                    "border-transparent bg-stone-200 text-sharpie-black hover:bg-stone-300",
                destructive:
                    "border-transparent bg-ticket-red text-white hover:bg-red-600",
                outline: "text-foreground border-2 border-sharpie-black rotate-0 shadow-none",
            },
        },
        defaultVariants: {
            variant: "default",
        },
    }
)

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> { }

function Badge({ className, variant, ...props }: BadgeProps) {
    return (
        <div className={cn(badgeVariants({ variant }), className)} {...props} />
    )
}

export { Badge, badgeVariants }
