"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, Database, Play, Settings, CreditCard, ChevronLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export function Sidebar() {
    const pathname = usePathname()

    // Extract workspace slug if present
    // /dashboard/workspaces/[slug]/...
    const segments = pathname.split('/')
    const isWorkspace = segments[2] === 'workspaces' && segments[3] && segments[3] !== 'new'
    const workspaceSlug = isWorkspace ? segments[3] : null

    return (
        <aside className="hidden md:flex flex-col w-64 border-r border-slate-700 bg-slate-900 text-slate-300 h-screen sticky top-0 font-mono">
            <div className="p-6 border-b border-slate-700 bg-slate-900 text-white">
                <Link href="/dashboard" className="font-bold font-heading text-2xl tracking-wide flex items-center gap-2 uppercase">
                    KYTCHEN
                </Link>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {!isWorkspace ? (
                    <>
                        <div className="px-2 py-1 mb-2">
                            <h2 className="font-mono text-xs uppercase tracking-widest opacity-60 text-slate-500">The Pass</h2>
                        </div>
                        <NavItem href="/dashboard" icon={<LayoutDashboard className="w-4 h-4" />} label="Expo" active={pathname === "/dashboard"} />
                        <NavItem href="/dashboard/workspaces" icon={<Database className="w-4 h-4" />} label="Stations" active={pathname === "/dashboard/workspaces"} />
                        <NavItem href="/dashboard/account" icon={<Settings className="w-4 h-4" />} label="Prep List" active={pathname === "/dashboard/account"} />
                    </>
                ) : (
                    <>
                        <Button variant="ghost" asChild className="w-full justify-start px-2 mb-4 font-mono text-xs uppercase tracking-wider text-slate-400 hover:text-white hover:bg-slate-800">
                            <Link href="/dashboard/workspaces">
                                <ChevronLeft className="w-4 h-4 mr-2" /> All Stations
                            </Link>
                        </Button>

                        <div className="px-2 py-1 mb-2">
                            <h2 className="font-mono text-xs uppercase tracking-widest opacity-60 text-slate-500">Station</h2>
                        </div>
                        <NavItem href={`/dashboard/workspaces/${workspaceSlug}`} icon={<LayoutDashboard className="w-4 h-4" />} label="Overview" exact />
                        <NavItem href={`/dashboard/workspaces/${workspaceSlug}/datasets`} icon={<Database className="w-4 h-4" />} label="Pantry" />
                        <NavItem href={`/dashboard/workspaces/${workspaceSlug}/runs`} icon={<Play className="w-4 h-4" />} label="Service" />
                        <NavItem href={`/dashboard/workspaces/${workspaceSlug}/settings`} icon={<Settings className="w-4 h-4" />} label="Prep List" />
                    </>
                )}
            </nav>

            <div className="p-4 border-t border-slate-700">
                <NavItem href="/dashboard/billing" icon={<CreditCard className="w-4 h-4" />} label="The Check" active={pathname === "/dashboard/billing"} />
            </div>
        </aside>
    )
}

function NavItem({ href, icon, label, active, exact }: { href: string; icon: React.ReactNode; label: string; active?: boolean; exact?: boolean }) {
    const pathname = usePathname()
    const isActive = active !== undefined ? active : (exact ? pathname === href : pathname.startsWith(href))

    return (
        <Link href={href}>
            <div className={cn(
                "flex items-center gap-3 px-3 py-2 text-sm font-mono transition-none hover:bg-slate-800 hover:text-white border border-transparent text-slate-400",
                isActive && "bg-blue-tape text-white border-transparent shadow-none hover:bg-blue-600"
            )}>
                {icon}
                <span>{label}</span>
            </div>
        </Link>
    )
}
