import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"

export default function AccountPage() {
    return (
        <div className="space-y-8 max-w-2xl">
            <h1 className="font-serif text-3xl">Account Settings</h1>

            <Card>
                <CardHeader>
                    <CardTitle>Profile</CardTitle>
                    <CardDescription>Manage your personal information.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-mono uppercase font-bold">Email</label>
                        <Input defaultValue="user@example.com" disabled />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-mono uppercase font-bold">Full Name</label>
                        <Input defaultValue="Hunter Bown" />
                    </div>
                </CardContent>
                <CardFooter className="justify-end">
                    <Button>Save Profile</Button>
                </CardFooter>
            </Card>
        </div>
    )
}
