import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import Stripe from 'stripe'

function getStripe() {
    return new Stripe(process.env.STRIPE_SECRET_KEY!, {
        apiVersion: '2025-12-15.clover',
    })
}

export async function POST(request: Request) {
    const stripe = getStripe()
    try {
        const supabase = await createClient()

        // Get current user
        const { data: { user }, error: authError } = await supabase.auth.getUser()
        if (authError || !user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
        }

        const body = await request.json()
        const { workspaceId, returnUrl } = body

        if (!workspaceId) {
            return NextResponse.json({ error: 'Missing workspaceId' }, { status: 400 })
        }

        // Verify user has access to workspace
        const { data: member } = await supabase
            .from('members')
            .select('role')
            .eq('workspace_id', workspaceId)
            .eq('user_id', user.id)
            .single()

        if (!member) {
            return NextResponse.json({ error: 'Access denied' }, { status: 403 })
        }

        // Get workspace
        const { data: workspace, error: wsError } = await supabase
            .from('workspaces')
            .select('id, stripe_customer_id')
            .eq('id', workspaceId)
            .single()

        if (wsError || !workspace) {
            return NextResponse.json({ error: 'Workspace not found' }, { status: 404 })
        }

        if (!workspace.stripe_customer_id) {
            return NextResponse.json(
                { error: 'No billing account. Subscribe to a plan first.' },
                { status: 400 }
            )
        }

        // Create portal session
        const session = await stripe.billingPortal.sessions.create({
            customer: workspace.stripe_customer_id,
            return_url: returnUrl || `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/dashboard/billing`,
        })

        return NextResponse.json({
            portalUrl: session.url,
        })
    } catch (error) {
        console.error('Portal error:', error)
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Portal access failed' },
            { status: 500 }
        )
    }
}
