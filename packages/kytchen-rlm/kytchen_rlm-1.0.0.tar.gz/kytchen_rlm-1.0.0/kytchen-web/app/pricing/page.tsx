import { Header } from "@/components/marketing/header"
import { Footer } from "@/components/marketing/footer"
import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"

export default function PricingPage() {
    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 py-16 md:py-24">
                <div className="container mx-auto px-4">
                    <div className="text-center mb-16">
                        <h1 className="font-serif text-5xl md:text-6xl mb-6">Simple, Transparent Pricing.</h1>
                        <p className="font-mono text-lg text-muted-foreground">Start for free. Scale when you need more context.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                        {/* Starter */}
                        <div className="border border-foreground p-8 flex flex-col bg-background">
                            <h3 className="font-mono text-xl font-bold uppercase mb-2">Starter</h3>
                            <div className="font-serif text-4xl mb-6">$0</div>
                            <ul className="space-y-4 mb-8 font-mono text-sm flex-1">
                                <li className="flex gap-2"><Check className="w-4 h-4" /> 1 GB Storage</li>
                                <li className="flex gap-2"><Check className="w-4 h-4" /> 5 requests/min</li>
                                <li className="flex gap-2"><Check className="w-4 h-4" /> REPL Sandbox</li>
                            </ul>
                            <Button variant="outline" className="w-full">Get Started</Button>
                        </div>

                        {/* Chef */}
                        <div className="border border-foreground p-8 flex flex-col bg-foreground text-background shadow-[8px_8px_0px_0px_rgba(0,0,0,0.5)] transform md:-translate-y-4">
                            <h3 className="font-mono text-xl font-bold uppercase mb-2">Chef</h3>
                            <div className="font-serif text-4xl mb-6">$35<span className="text-sm opacity-60">/mo</span></div>
                            <ul className="space-y-4 mb-8 font-mono text-sm flex-1">
                                <li className="flex gap-2"><Check className="w-4 h-4" /> 10 GB Storage</li>
                                <li className="flex gap-2"><Check className="w-4 h-4" /> 100 requests/min</li>
                                <li className="flex gap-2"><Check className="w-4 h-4" /> 1 Persistent Line</li>
                                <li className="flex gap-2"><Check className="w-4 h-4" /> Priority Support</li>
                            </ul>
                            <Button variant="secondary" className="w-full text-foreground hover:bg-background hover:text-foreground">Get Chef</Button>
                        </div>

                        {/* Sous Chef */}
                        <div className="border border-foreground p-8 flex flex-col bg-background">
                            <h3 className="font-mono text-xl font-bold uppercase mb-2">Sous Chef</h3>
                            <div className="font-serif text-4xl mb-6">$99<span className="text-sm opacity-60">/mo</span></div>
                            <ul className="space-y-4 mb-8 font-mono text-sm flex-1">
                                <li className="flex gap-2"><Check className="w-4 h-4" /> 50 GB Storage</li>
                                <li className="flex gap-2"><Check className="w-4 h-4" /> 200 requests/min</li>
                                <li className="flex gap-2"><Check className="w-4 h-4" /> 3 Persistent Lines</li>
                                <li className="flex gap-2"><Check className="w-4 h-4" /> Dedicated Support</li>
                            </ul>
                            <Button variant="outline" className="w-full">Get Sous Chef</Button>
                        </div>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    )
}
