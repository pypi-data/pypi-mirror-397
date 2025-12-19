import Link from "next/link"
import { Terminal } from "lucide-react"

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
            {/* Left: Branding & Art */}
            <div className="hidden lg:flex flex-col justify-between p-12 bg-foreground text-background border-r border-background/20 relative overflow-hidden">
                {/* Abstract background pattern */}
                <div className="absolute inset-0 opacity-10">
                    <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <path d="M0 100 L100 0 L100 100 Z" fill="currentColor" />
                    </svg>
                </div>

                <div className="relative z-10">
                    <Link href="/" className="flex items-center gap-2 font-bold font-inter text-2xl tracking-tight">
                        <Terminal className="w-8 h-8" />
                        KYTCHEN
                    </Link>
                </div>

                <div className="relative z-10 max-w-md">
                    <blockquote className="font-serif text-3xl leading-tight mb-6">
                        &quot;The universe (which others call the Library) is composed of an indefinite and perhaps infinite number of hexagonal galleries.&quot;
                    </blockquote>
                    <cite className="font-mono text-sm uppercase tracking-widest opacity-80">
                        - Jorge Luis Borges, &quot;The Library of Babel&quot;
                    </cite>
                </div>
            </div>

            {/* Right: Form */}
            <div className="flex items-center justify-center p-8 bg-background">
                <div className="w-full max-w-md space-y-8">
                    {children}
                </div>
            </div>
        </div>
    )
}
