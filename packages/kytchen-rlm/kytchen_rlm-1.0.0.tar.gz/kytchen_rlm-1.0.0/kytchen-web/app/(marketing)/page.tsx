"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Flame, FileText, Terminal, Code2, Cpu, ChevronRight, Activity, Layers, ShieldCheck } from "lucide-react"

export default function LandingPage() {
    return (
        <>
            {/* Hero Section */}
            <section className="relative py-32 px-6 border-b border-white/10 bg-background overflow-hidden min-h-[90vh] flex items-center">
                {/* Background Pattern */}
                <div className="absolute inset-0 opacity-[0.05] pointer-events-none" style={{ backgroundImage: 'radial-gradient(#FFF 1px, transparent 1px)', backgroundSize: '32px 32px' }}></div>

                <div className="max-w-7xl mx-auto relative z-10 w-full">
                    <div className="flex flex-col lg:flex-row items-center gap-20">
                        <div className="flex-1 text-center lg:text-left space-y-10">
                            <div className="inline-flex items-center gap-2 bg-slate-surface/50 text-electric-blue px-3 py-1 text-xs font-mono font-bold uppercase tracking-[0.2em] border border-white/10 text-glow">
                                <span className="w-2 h-2 bg-electric-blue rounded-full animate-pulse"></span>
                                Recursive Language Model (RLM)
                            </div>

                            <h1 className="font-heading text-6xl sm:text-8xl lg:text-[7rem] leading-[0.8] uppercase tracking-tighter text-foreground">
                                Let Agents<br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-electric-blue to-white">
                                    Browse.
                                </span>
                            </h1>

                            <p className="text-xl md:text-2xl font-light text-gray-400 leading-relaxed max-w-2xl">
                                Stop stuffing context windows. Kytchen gives your agents <span className="text-white font-medium">Agentic Paging</span>—the ability to <span className="font-mono text-electric-blue">grep</span>, <span className="font-mono text-electric-blue">read</span>, and <span className="font-mono text-electric-blue">reason</span> over massive datasets recursively.
                            </p>

                            <div className="flex flex-col sm:flex-row gap-6 justify-center lg:justify-start pt-6">
                                <Link href="#start">
                                    <Button size="lg" className="w-full sm:w-auto h-16 text-lg font-bold tracking-widest uppercase bg-electric-blue text-black hover:bg-blue-400 hover:scale-105 transition-all rounded-none border-0">
                                        <Terminal className="mr-3 w-5 h-5" /> Initialize RLM
                                    </Button>
                                </Link>
                                <Link href="/docs">
                                    <Button variant="outline" size="lg" className="w-full sm:w-auto h-16 text-lg font-bold tracking-widest uppercase bg-transparent border border-white/20 text-white hover:bg-white/10 hover:border-white transition-all rounded-none">
                                        Read Docs
                                    </Button>
                                </Link>
                            </div>

                            <div className="pt-8 text-sm text-gray-500 font-mono">
                                * Based on MIT Paper (Zhang & Omar) methodology.
                            </div>
                        </div>

                        {/* Hero Graphic / Code Snippet - The "Terminal" Look */}
                        <div className="flex-1 w-full max-w-xl lg:max-w-none">
                            <div className="bg-[#050505] rounded-none border border-white/10 shadow-glow relative group">
                                <div className="absolute -inset-1 bg-gradient-to-r from-electric-blue/20 to-purple-500/20 blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>

                                <div className="relative bg-[#050505] p-1">
                                    {/* Terminal Header */}
                                    <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-slate-surface/30">
                                        <div className="flex gap-2">
                                            <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
                                            <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                                            <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
                                        </div>
                                        <div className="font-mono text-xs text-gray-500 uppercase tracking-widest">agent_workflow.py</div>
                                    </div>

                                    {/* Code Content */}
                                    <div className="p-6 font-mono text-sm overflow-hidden text-gray-300">
                                        <div className="space-y-1">
                                            <div className="text-gray-500"># Step 1: Initialize the Recursive Agent</div>
                                            <div className="text-purple-400">from</div> kytchen <div className="text-purple-400">import</div> <span className="text-yellow-300">AgenticPager</span>

                                            <div className="h-4"></div>

                                            <div className="text-gray-500"># Step 2: Agent browses dynamically</div>
                                            <div><span className="text-blue-400">agent</span> = <span className="text-yellow-300">AgenticPager</span>(model="claude-3-5-sonnet")</div>

                                            <div className="h-4"></div>

                                            <div className="text-gray-500"># Not RAG. The agent chooses what to read.</div>
                                            <div><span className="text-blue-400">result</span> = <span className="text-blue-400">agent</span>.explore(</div>
                                            <div className="pl-4">query="Find the hidden API key in the logs",</div>
                                            <div className="pl-4">target="./massive_server_logs.txt"</div>
                                            <div>)</div>

                                            <div className="h-4"></div>

                                            <div className="bg-slate-surface/50 p-3 border-l-2 border-electric-blue text-xs mt-4">
                                                <div className="text-electric-blue mb-1">➜ Kytchen Output Stream:</div>
                                                <div className="text-gray-400">&gt; Grepping for "API_KEY" pattern... (Found 3 matches)</div>
                                                <div className="text-gray-400">&gt; Paging explicitly to lines 4050-4100...</div>
                                                <div className="text-green-400">&gt; Found verified secret. Stopping.</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Core Concepts */}
            <section id="concepts" className="grid grid-cols-1 md:grid-cols-3 border-b border-white/10 divide-y md:divide-y-0 md:divide-x divide-white/10 bg-background">
                {/* Concept 1: Model Agnostic */}
                <div className="p-12 hover:bg-white/5 transition-colors group relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-5 font-heading text-9xl leading-none select-none text-white">01</div>
                    <Layers className="w-10 h-10 text-electric-blue mb-6" />
                    <h3 className="font-heading text-3xl uppercase mb-4 text-white tracking-wide">Model Agnostic</h3>
                    <p className="text-lg text-gray-400 leading-relaxed font-light">
                        Bring Your Own LLM. Whether it's Claude, GPT-4, or a local Llama 3 via Ollama. Kytchen provides the tool interface; you control the intelligence.
                    </p>
                </div>

                {/* Concept 2: Open Kytchen */}
                <div className="p-12 hover:bg-white/5 transition-colors group relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-5 font-heading text-9xl leading-none select-none text-white">02</div>
                    <ShieldCheck className="w-10 h-10 text-electric-blue mb-6" />
                    <h3 className="font-heading text-3xl uppercase mb-4 text-white tracking-wide">Open Kytchen</h3>
                    <p className="text-lg text-gray-400 leading-relaxed font-light">
                        <span className="text-white font-medium">Traceability is key.</span> See exactly what your agent read, searched, and discarded. A complete audit trail of the agent's thought process.
                    </p>
                </div>

                {/* Concept 3: MCP Native */}
                <div className="p-12 hover:bg-white/5 transition-colors group relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-5 font-heading text-9xl leading-none select-none text-white">03</div>
                    <Activity className="w-10 h-10 text-electric-blue mb-6" />
                    <h3 className="font-heading text-3xl uppercase mb-4 text-white tracking-wide">MCP Native</h3>
                    <p className="text-lg text-gray-400 leading-relaxed font-light">
                        Built for the Model Context Protocol. Drop Kytchen directly into Cursor, Windsurf, or Claude Desktop as a server. Zero friction integration.
                    </p>
                </div>
            </section>

            {/* CTA / Footer-ish */}
            <section id="start" className="py-32 px-6 bg-slate-surface border-b border-white/10 text-center">
                <div className="max-w-4xl mx-auto space-y-8">
                    <h2 className="font-heading text-5xl md:text-7xl uppercase tracking-tighter leading-none text-white">
                        Ready to<br />
                        <span className="text-electric-blue">Standardize?</span>
                    </h2>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto font-light">
                        Join the repo. Fork the protocols. Build better agents.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-6 justify-center pt-8">
                        <Button size="lg" className="h-16 px-8 text-xl font-bold uppercase tracking-widest bg-white text-black hover:bg-gray-200 rounded-none">
                            <Code2 className="mr-2 w-6 h-6" /> GitHub
                        </Button>
                        <Button variant="outline" size="lg" className="h-16 px-8 text-xl font-bold uppercase tracking-widest border border-white/20 text-white hover:bg-white/10 rounded-none">
                            Discord
                        </Button>
                    </div>
                </div>
            </section>
        </>
    )
}
