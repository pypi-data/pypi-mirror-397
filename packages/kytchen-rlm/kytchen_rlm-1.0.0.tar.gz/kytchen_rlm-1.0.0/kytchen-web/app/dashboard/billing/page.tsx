'use client'

import { Suspense, useEffect, useState, useCallback } from 'react'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Check, Loader2, ExternalLink, AlertCircle, CheckCircle } from "lucide-react"
import { Database } from '@/types/database'

type Workspace = Database['public']['Tables']['workspaces']['Row']
type Usage = Database['public']['Tables']['usage']['Row']
type Billing = Database['public']['Tables']['billing']['Row']

// Plan limits (match backend limits.py)
const PLAN_LIMITS = {
    free: { storage: 1 * 1024 * 1024 * 1024, requests: 500, egress: 1024 * 1024 * 1024, name: 'Starter', price: 0 },
    pro: { storage: 10 * 1024 * 1024 * 1024, requests: 10000, egress: 50 * 1024 * 1024 * 1024, name: 'Chef', price: 35 },
    team: { storage: 50 * 1024 * 1024 * 1024, requests: 50000, egress: 200 * 1024 * 1024 * 1024, name: 'Sous Chef', price: 99 },
}

const PLAN_FEATURES = {
    free: ['1 GB Storage', '5 Requests/min', 'REPL Sandbox'],
    pro: ['10 GB Storage', '100 Requests/min', '1 Persistent Line', 'Priority Support'],
    team: ['50 GB Storage', '200 Requests/min', '3 Persistent Lines', 'Dedicated Support'],
}

function formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

export default function BillingPage() {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin" />
            </div>
        }>
            <BillingPageContent />
        </Suspense>
    )
}

function BillingPageContent() {
    const searchParams = useSearchParams()
    const [workspace, setWorkspace] = useState<Workspace | null>(null)
    const [usage, setUsage] = useState<Usage | null>(null)
    const [billing, setBilling] = useState<Billing | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isCheckoutLoading, setIsCheckoutLoading] = useState(false)
    const [isPortalLoading, setIsPortalLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [successMessage, setSuccessMessage] = useState<string | null>(null)

    // Handle success/cancel from Stripe redirect
    useEffect(() => {
        if (searchParams.get('success') === 'true') {
            setSuccessMessage('Subscription activated! Welcome to the kitchen.')
            setTimeout(() => setSuccessMessage(null), 5000)
        }
        if (searchParams.get('canceled') === 'true') {
            setError('Checkout canceled. No changes were made.')
            setTimeout(() => setError(null), 5000)
        }
    }, [searchParams])

    const fetchData = useCallback(async () => {
        const supabase = createClient()

        // Get current user
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) {
            setError('Please sign in to view billing')
            setIsLoading(false)
            return
        }

        // Get user's first workspace (for now, single workspace per user)
        const memberResult = await supabase
            .from('members')
            .select('workspace_id')
            .eq('user_id', user.id)
            .single()

        const memberData = memberResult.data as { workspace_id: string } | null
        const workspaceId = memberData?.workspace_id
        if (!workspaceId) {
            setError('No workspace found')
            setIsLoading(false)
            return
        }

        // Fetch workspace, usage, and billing
        const { data: wsData } = await supabase
            .from('workspaces')
            .select('*')
            .eq('id', workspaceId)
            .single()
        const { data: usageData } = await supabase
            .from('usage')
            .select('*')
            .eq('workspace_id', workspaceId)
            .single()
        const { data: billingData } = await supabase
            .from('billing')
            .select('*')
            .eq('workspace_id', workspaceId)
            .single()

        if (wsData) setWorkspace(wsData as unknown as Workspace)
        if (usageData) setUsage(usageData as unknown as Usage)
        if (billingData) setBilling(billingData as unknown as Billing)

        setIsLoading(false)
    }, [])

    useEffect(() => {
        fetchData()
    }, [fetchData])

    const handleCheckout = async (priceId: string) => {
        if (!workspace) return

        setIsCheckoutLoading(true)
        setError(null)

        try {
            const response = await fetch('/api/billing/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    priceId,
                    workspaceId: workspace.id,
                    successUrl: `${window.location.origin}/dashboard/billing?success=true`,
                    cancelUrl: `${window.location.origin}/dashboard/billing?canceled=true`,
                }),
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.error || 'Checkout failed')
            }

            // Redirect to Stripe Checkout
            window.location.href = data.checkoutUrl
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Checkout failed')
            setIsCheckoutLoading(false)
        }
    }

    const handlePortal = async () => {
        if (!workspace) return

        setIsPortalLoading(true)
        setError(null)

        try {
            const response = await fetch('/api/billing/portal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    workspaceId: workspace.id,
                    returnUrl: `${window.location.origin}/dashboard/billing`,
                }),
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.error || 'Portal access failed')
            }

            // Redirect to Stripe Portal
            window.location.href = data.portalUrl
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Portal access failed')
            setIsPortalLoading(false)
        }
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin" />
            </div>
        )
    }

    const plan = (workspace?.plan || 'free') as keyof typeof PLAN_LIMITS
    const limits = PLAN_LIMITS[plan]
    const features = PLAN_FEATURES[plan]

    const storageUsed = usage?.storage_bytes || 0
    const storagePercent = Math.min(100, (storageUsed / limits.storage) * 100)

    const requestsUsed = usage?.requests_this_month || 0
    const requestsPercent = Math.min(100, (requestsUsed / limits.requests) * 100)

    const egressUsed = usage?.egress_bytes_this_month || 0
    const egressPercent = Math.min(100, (egressUsed / limits.egress) * 100)

    return (
        <div className="space-y-8 max-w-5xl">
            <h1 className="font-serif text-3xl">Billing & Usage</h1>

            {/* Success Message */}
            {successMessage && (
                <div className="flex items-center gap-2 p-4 bg-green-500/10 border border-green-500 text-green-600">
                    <CheckCircle className="w-4 h-4" />
                    <span className="font-mono text-sm">{successMessage}</span>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500 text-red-600">
                    <AlertCircle className="w-4 h-4" />
                    <span className="font-mono text-sm">{error}</span>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Usage Card */}
                <div className="md:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Usage Limits</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-8">
                            {/* Storage Meter */}
                            <div className="space-y-2">
                                <div className="flex justify-between font-mono text-sm">
                                    <span className="uppercase font-bold">Storage</span>
                                    <span>{formatBytes(storageUsed)} / {formatBytes(limits.storage)}</span>
                                </div>
                                <div className="h-4 border border-foreground p-0.5">
                                    <div
                                        className={`h-full ${storagePercent > 80 ? 'bg-accent-warning' : 'bg-foreground'}`}
                                        style={{ width: `${storagePercent}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Requests Meter */}
                            <div className="space-y-2">
                                <div className="flex justify-between font-mono text-sm">
                                    <span className="uppercase font-bold">Requests (This Month)</span>
                                    <span>{requestsUsed.toLocaleString()} / {limits.requests.toLocaleString()}</span>
                                </div>
                                <div className="h-4 border border-foreground p-0.5">
                                    <div
                                        className={`h-full ${requestsPercent > 80 ? 'bg-accent-warning' : 'bg-accent-primary'}`}
                                        style={{ width: `${requestsPercent}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Egress Meter */}
                            <div className="space-y-2">
                                <div className="flex justify-between font-mono text-sm">
                                    <span className="uppercase font-bold">Egress</span>
                                    <span>{formatBytes(egressUsed)} / {formatBytes(limits.egress)}</span>
                                </div>
                                <div className="h-4 border border-foreground p-0.5">
                                    <div
                                        className={`h-full ${egressPercent > 80 ? 'bg-accent-warning' : 'bg-accent-primary'}`}
                                        style={{ width: `${egressPercent}%` }}
                                    ></div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Subscription Info Card */}
                    {billing && billing.subscription_status && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Subscription</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex justify-between font-mono text-sm">
                                    <span>Status</span>
                                    <Badge variant={billing.subscription_status === 'active' ? 'default' : 'secondary'}>
                                        {billing.subscription_status}
                                    </Badge>
                                </div>
                                {billing.current_period_end && (
                                    <div className="flex justify-between font-mono text-sm">
                                        <span>Renews</span>
                                        <span>{new Date(billing.current_period_end).toLocaleDateString()}</span>
                                    </div>
                                )}
                                {billing.cancel_at_period_end && (
                                    <div className="text-sm text-amber-600 font-mono">
                                        Cancels at end of billing period
                                    </div>
                                )}
                                <Button
                                    variant="outline"
                                    onClick={handlePortal}
                                    disabled={isPortalLoading}
                                    className="w-full gap-2"
                                >
                                    {isPortalLoading ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <ExternalLink className="w-4 h-4" />
                                    )}
                                    Manage Subscription
                                </Button>
                            </CardContent>
                        </Card>
                    )}
                </div>

                {/* Plan Card */}
                <div className="md:col-span-1">
                    <Card className="h-full flex flex-col border-2 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                        <CardHeader>
                            <div className="flex justify-between items-start mb-2">
                                <Badge variant="outline" className="text-xs">CURRENT PLAN</Badge>
                            </div>
                            <CardTitle className="text-4xl font-serif">{limits.name}</CardTitle>
                            <div className="font-mono text-sm text-muted-foreground">
                                ${limits.price} / month
                            </div>
                        </CardHeader>
                        <CardContent className="flex-1 space-y-4 pt-6">
                            <ul className="space-y-2 font-mono text-sm">
                                {features.map((feature, i) => (
                                    <li key={i} className="flex items-center gap-2">
                                        <Check className="w-4 h-4" /> {feature}
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                        <CardFooter className="flex-col gap-4">
                            {plan === 'free' && (
                                <>
                                    <Button
                                        className="w-full"
                                        onClick={() => handleCheckout('chef')}
                                        disabled={isCheckoutLoading}
                                    >
                                        {isCheckoutLoading ? (
                                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                        ) : null}
                                        Upgrade to Chef ($35/mo)
                                    </Button>
                                    <Button
                                        variant="outline"
                                        className="w-full"
                                        onClick={() => handleCheckout('souschef')}
                                        disabled={isCheckoutLoading}
                                    >
                                        Upgrade to Sous Chef ($99/mo)
                                    </Button>
                                </>
                            )}
                            {plan === 'pro' && (
                                <Button
                                    className="w-full"
                                    onClick={() => handleCheckout('souschef')}
                                    disabled={isCheckoutLoading}
                                >
                                    {isCheckoutLoading ? (
                                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                    ) : null}
                                    Upgrade to Sous Chef ($99/mo)
                                </Button>
                            )}
                            {plan !== 'free' && (
                                <Button
                                    variant="outline"
                                    onClick={handlePortal}
                                    disabled={isPortalLoading}
                                    className="w-full gap-2"
                                >
                                    {isPortalLoading ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <ExternalLink className="w-4 h-4" />
                                    )}
                                    Manage Subscription
                                </Button>
                            )}
                            <p className="text-xs text-center text-muted-foreground">
                                Pay membership, use the kitchen. No games, no tricks.
                            </p>
                        </CardFooter>
                    </Card>
                </div>
            </div>
        </div>
    )
}
