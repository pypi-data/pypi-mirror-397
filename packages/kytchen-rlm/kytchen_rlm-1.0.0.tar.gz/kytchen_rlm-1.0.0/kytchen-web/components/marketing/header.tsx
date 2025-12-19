import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Terminal, ArrowRight, Layers } from "lucide-react"

export function Header() {
    return (
        <header className="px-6 h-16 flex items-center justify-between border-b border-white/10 bg-background/80 backdrop-blur-md sticky top-0 z-50">
            <div className="flex items-center gap-2">
                <div className="bg-electric-blue text-black p-1 transform shadow-glow text-glow">
                    <Layers className="w-5 h-5" />
                </div>
                <Link href="/" className="font-heading font-bold text-2xl tracking-tighter uppercase text-foreground bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                    Kytchen
                </Link>
            </div>
            <nav className="hidden md:flex gap-8 font-mono text-sm uppercase tracking-widest font-bold text-gray-400">
                <Link href="/#concepts" className="hover:text-electric-blue hover:text-glow transition-all">Concepts</Link>
                <Link href="/#start" className="hover:text-electric-blue hover:text-glow transition-all">Get Started</Link>
                <Link href="/docs" className="hover:text-electric-blue hover:text-glow transition-all">Docs</Link>
            </nav>
            <div className="flex items-center gap-4">
                <Link href="/login" className="font-mono text-sm uppercase font-bold text-gray-400 hover:text-electric-blue">Login</Link>
                <Link href="/dashboard">
                    <Button className="font-bold uppercase tracking-widest text-xs h-9 px-6 border border-white/20 bg-white/5 text-white hover:bg-electric-blue hover:text-black hover:border-electric-blue hover:shadow-glow transition-all rounded-none">
                        Console <ArrowRight className="ml-2 w-3 h-3" />
                    </Button>
                </Link>
            </div>
        </header>
    )
}
