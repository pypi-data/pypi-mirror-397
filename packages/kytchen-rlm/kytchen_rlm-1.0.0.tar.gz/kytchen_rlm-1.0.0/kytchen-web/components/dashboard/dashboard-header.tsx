"use client"

import { createClient } from "@/lib/supabase/client"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"

export function DashboardHeader() {
    const router = useRouter()
    const supabase = createClient()

    const handleLogout = async () => {
        await supabase.auth.signOut()
        router.push("/login")
        router.refresh()
    }

    return (
        <header className="h-16 border-b-2 border-sharpie-black flex items-center justify-between px-6 bg-white">
            <div className="font-mono text-sm uppercase tracking-widest">
                Location: Dallas &gt; Station: Grill
            </div>
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={handleLogout} className="font-mono uppercase text-xs text-ticket-red hover:bg-red-50 hover:text-red-600">
                    86 Me
                </Button>
            </div>
        </header>
    )
}
