"use client"

import Link from "next/link"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from "lucide-react"

export default function LoginPage() {
    const router = useRouter()
    const supabase = createClient()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const { error } = await supabase.auth.signInWithPassword({
                email,
                password,
            })

            if (error) {
                throw error
            }

            router.push("/dashboard")
            router.refresh()
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : "Login failed"
            setError(msg)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Card className="border-0 shadow-none sm:border sm:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <CardHeader>
                <CardTitle>Welcome back</CardTitle>
                <CardDescription>Enter your credentials to access your workspace.</CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleLogin} className="space-y-4">
                    <div className="space-y-2">
                        <label htmlFor="email" className="text-sm font-mono uppercase font-bold">Email</label>
                        <Input
                            id="email"
                            type="email"
                            placeholder="name@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <label htmlFor="password" className="text-sm font-mono uppercase font-bold">Password</label>
                            <Link href="/forgot-password" className="text-xs font-mono underline hover:text-accent-primary">Forgot?</Link>
                        </div>
                        <Input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    {error && (
                        <div className="text-sm text-accent-error font-mono bg-accent-error/10 p-2 border border-accent-error">
                            {error}
                        </div>
                    )}
                    <Button type="submit" className="w-full" disabled={loading}>
                        {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Sign In"}
                    </Button>
                </form>
            </CardContent>
            <CardFooter className="flex flex-col gap-4">
                <div className="relative w-full">
                    <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t border-foreground opacity-20" />
                    </div>
                    <div className="relative flex justify-center text-xs font-mono uppercase">
                        <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
                    </div>
                </div>
                <Button variant="outline" className="w-full" type="button" disabled>
                    GitHub (Coming Soon)
                </Button>
                <div className="text-center text-sm font-mono mt-4">
                    Don&apos;t have an account?{" "}
                    <Link href="/signup" className="underline hover:text-accent-primary">
                        Sign up
                    </Link>
                </div>
            </CardFooter>
        </Card>
    )
}
