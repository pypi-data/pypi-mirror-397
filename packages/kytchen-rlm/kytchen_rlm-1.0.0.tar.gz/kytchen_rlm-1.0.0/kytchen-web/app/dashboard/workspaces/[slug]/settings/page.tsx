import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Separator } from "@radix-ui/react-separator"
import Link from "next/link"
import { Key } from "lucide-react"

export default function SettingsPage({ params }: { params: { slug: string } }) {
    return (
        <div className="space-y-8 max-w-4xl">
            <h1 className="font-serif text-3xl">Settings</h1>

            <div className="flex flex-col gap-6">
                <Link href={`/dashboard/workspaces/${params.slug}/settings/api-keys`}>
                    <Button variant="outline" className="w-full justify-start gap-2 h-auto py-6">
                        <Key className="w-5 h-5" />
                        <div className="text-left">
                            <div className="font-bold">Manage API Keys</div>
                            <div className="text-xs text-muted-foreground font-normal">Create and revoke access keys for the MCP server</div>
                        </div>
                    </Button>
                </Link>
            </div>

            <Separator className="my-8 border-t border-foreground" />

            <Card>
                <CardHeader>
                    <CardTitle>Generalized Settings</CardTitle>
                    <CardDescription>Update your workspace details.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-mono uppercase font-bold">Workspace Name</label>
                        <Input defaultValue="Legal Research" />
                    </div>
                </CardContent>
                <CardFooter className="justify-end">
                    <Button>Save Changes</Button>
                </CardFooter>
            </Card>

            <Card className="border-accent-error">
                <CardHeader>
                    <CardTitle className="text-accent-error">Danger Zone</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm font-mono mb-4">Permanently delete this workspace and all associated data.</p>
                    <Button variant="destructive">Delete Workspace</Button>
                </CardContent>
            </Card>
        </div>
    )
}
