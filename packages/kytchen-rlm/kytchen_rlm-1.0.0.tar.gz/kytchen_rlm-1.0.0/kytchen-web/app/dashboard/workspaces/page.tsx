import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Plus, ArrowRight } from "lucide-react"

export default function WorkspacesPage() {
    // This would fetch real workspaces in the future
    const workspaces = [
        { id: 1, name: "Legal Research", slug: "legal-research", members: 3, plan: "Pro" },
        { id: 2, name: "Personal Sandbox", slug: "personal", members: 1, plan: "Free" }
    ]

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h1 className="font-serif text-3xl">Workspaces</h1>
                <Link href="/dashboard/workspaces/new">
                    <Button className="gap-2">
                        <Plus className="w-4 h-4" /> New Workspace
                    </Button>
                </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {workspaces.map((ws) => (
                    <Card key={ws.slug} className="group shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-shadow">
                        <CardHeader>
                            <div className="flex justify-between items-start">
                                <CardTitle className="text-xl">{ws.name}</CardTitle>
                                <span className="font-mono text-xs uppercase border border-foreground px-2 py-0.5">{ws.plan}</span>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <p className="font-mono text-xs text-muted-foreground">{ws.members} member{ws.members !== 1 && 's'}</p>
                        </CardContent>
                        <CardFooter>
                            <Link href={`/dashboard/workspaces/${ws.slug}`} className="w-full">
                                <Button variant="outline" className="w-full justify-between group-hover:bg-foreground group-hover:text-background">
                                    Enter <ArrowRight className="w-4 h-4" />
                                </Button>
                            </Link>
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    )
}
