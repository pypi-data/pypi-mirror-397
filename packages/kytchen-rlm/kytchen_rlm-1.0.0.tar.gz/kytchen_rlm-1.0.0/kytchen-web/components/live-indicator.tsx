import { cn } from "@/lib/utils";

interface LiveIndicatorProps {
    className?: string;
    label?: string;
}

export function LiveIndicator({ className, label = "LIVE" }: LiveIndicatorProps) {
    return (
        <div className={cn("flex items-center gap-2", className)}>
            <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
            </span>
            <span className="text-[10px] font-bold tracking-widest text-red-500 uppercase">{label}</span>
        </div>
    )
}
