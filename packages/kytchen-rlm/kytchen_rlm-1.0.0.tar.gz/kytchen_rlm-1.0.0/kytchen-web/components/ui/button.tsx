import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { Loader2 } from "lucide-react"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
    "inline-flex items-center justify-center whitespace-nowrap text-sm font-bold uppercase transition-none focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border-2 border-sharpie-black font-mono transition-none active:translate-x-[2px] active:translate-y-[2px] active:shadow-hard-sm rounded-none",
    {
        variants: {
            variant: {
                default:
                    "bg-blue-tape text-white shadow-hard hover:bg-blue-700",
                destructive:
                    "bg-ticket-red text-white shadow-hard hover:bg-red-600",
                outline:
                    "bg-white text-sharpie-black shadow-hard hover:bg-stone-100",
                secondary:
                    "bg-stone-200 text-sharpie-black shadow-hard-sm hover:bg-stone-300",
                ghost: "hover:bg-accent hover:text-accent-foreground border-transparent shadow-none active:translate-x-0 active:translate-y-0 active:shadow-none",
                link: "text-blue-tape underline-offset-4 hover:underline border-transparent shadow-none active:translate-x-0 active:translate-y-0 active:shadow-none",
            },
            size: {
                default: "h-12 px-8 py-4",
                sm: "h-9 px-4 text-xs",
                lg: "h-14 px-10 text-base",
                icon: "h-12 w-12",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "default",
        },
    }
)

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
    asChild?: boolean
    isLoading?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, asChild = false, isLoading = false, children, disabled, ...props }, ref) => {
        const Comp = asChild ? Slot : "button"
        return (
            <Comp
                className={cn(buttonVariants({ variant, size, className }))}
                disabled={isLoading || disabled}
                ref={ref}
                {...props}
            >
                {isLoading && !asChild && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {children}
            </Comp>
        )
    }
)
Button.displayName = "Button"

export { Button, buttonVariants }
