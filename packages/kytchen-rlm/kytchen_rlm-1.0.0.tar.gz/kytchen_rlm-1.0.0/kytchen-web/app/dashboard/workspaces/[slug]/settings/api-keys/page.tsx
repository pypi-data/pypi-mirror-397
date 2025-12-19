"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Copy, Plus, Trash2, ArrowLeft } from "lucide-react"
import { useState } from "react"
import Link from "next/link"

export default function ApiKeysPage({ params }: { params: { slug: string } }) {
    const [showNewKey, setShowNewKey] = useState(false)
    const newKey = "kyt_sk_live_8f7d9a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t" // Mock

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h1 className="font-serif text-3xl">API Keys</h1>
                <Dialog>
                    <DialogTrigger asChild>
                        <Button className="gap-2"><Plus className="w-4 h-4" /> Create New Key</Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create API Key</DialogTitle>
                            <DialogDescription>Enter a name for this key to identify it later.</DialogDescription>
                        </DialogHeader>
                        <div className="py-4">
                            <Input placeholder="e.g. Cursor IDE" />
                        </div>
                        <DialogFooter>
                            <Button onClick={() => setShowNewKey(true)}>Generate Key</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            {showNewKey && (
                <div className="bg-surface-elevated border border-foreground p-6 mb-8 animate-in fade-in slide-in-from-top-4">
                    <h3 className="font-bold font-mono text-sm uppercase text-accent-success mb-2">Key Generated Successfully</h3>
                    <p className="text-sm mb-4">Copy this key now. You won&apos;t be able to see it again.</p>
                    <div className="flex gap-2">
                        <Input value={newKey} readOnly className="font-mono" />
                        <Button variant="outline" size="icon"><Copy className="w-4 h-4" /></Button>
                    </div>

                    <div className="mt-6">
                        <h4 className="font-bold font-mono text-xs uppercase mb-2">MCP Configuration</h4>
                        <pre className="bg-foreground text-background p-4 text-xs font-mono overflow-x-auto">
                            {`{
  "mcpServers": {
    "kytchen": {
      "command": "kytchen",
      "env": { 
        "KYTCHEN_API_KEY": "${newKey}" 
      }
    }
  }
}`}
                        </pre>
                    </div>
                </div>
            )}

            <div className="border border-foreground">
                <div className="grid grid-cols-12 border-b border-foreground bg-surface-elevated font-mono text-xs uppercase font-bold p-3">
                    <div className="col-span-4">Name</div>
                    <div className="col-span-4">Key Prefix</div>
                    <div className="col-span-3">Created</div>
                    <div className="col-span-1 text-right">Actions</div>
                </div>
                {[1, 2].map((i) => (
                    <div key={i} className="grid grid-cols-12 border-b border-foreground/20 p-4 items-center last:border-0 hover:bg-surface-elevated transition-none text-sm font-mono">
                        <div className="col-span-4 font-bold">Cursor Dev {i}</div>
                        <div className="col-span-4 text-muted-foreground">kyt_sk_...ab3{i}</div>
                        <div className="col-span-3 text-muted-foreground">2 days ago</div>
                        <div className="col-span-1 text-right">
                            <Button variant="ghost" size="icon" className="h-8 w-8 hover:text-destructive"><Trash2 className="w-4 h-4" /></Button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="pt-4">
                <Link href={`/dashboard/workspaces/${params.slug}/settings`}>
                    <Button variant="link" className="pl-0 gap-2"><ArrowLeft className="w-4 h-4" /> Back to Settings</Button>
                </Link>
            </div>
        </div>
    )
}
