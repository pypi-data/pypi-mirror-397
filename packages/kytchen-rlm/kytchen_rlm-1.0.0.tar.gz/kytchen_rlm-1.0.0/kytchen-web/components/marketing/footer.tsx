import Link from "next/link"
import { Layers } from "lucide-react"

export function Footer() {
    return (
        <footer className="bg-slate-surface py-12 px-6 border-t border-white/10">
            <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="flex items-center gap-2">
                    <div className="bg-electric-blue text-black p-1 shadow-glow">
                        <Layers className="w-5 h-5" />
                    </div>
                    <span className="font-heading font-bold text-xl uppercase tracking-tighter text-white">Kytchen</span>
                </div>

                <div className="flex gap-6 font-mono text-sm uppercase font-bold text-gray-500">
                    <Link href="/docs" className="hover:text-electric-blue hover:text-glow transition-all">Docs</Link>
                    <Link href="https://github.com/shannon-labs/kytchen" className="hover:text-electric-blue hover:text-glow transition-all">GitHub</Link>
                    <Link href="#" className="hover:text-electric-blue hover:text-glow transition-all">Discord</Link>
                </div>

                <div className="font-mono text-xs uppercase text-gray-600">
                    &copy; 2025 Kytchen Systems Inc. // All rights reserved.
                </div>
            </div>
        </footer>
    )
}
