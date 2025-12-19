import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import Stripe from 'stripe'

function getStripe() {
    return new Stripe(process.env.STRIPE_SECRET_KEY!, {
        apiVersion: '2025-12-15.clover',
    })
}

// Price IDs - set these in .env.local after creating products in Stripe
const PRICE_CHEF = process.env.STRIPE_PRICE_CHEF || ''
const PRICE_SOUSCHEF = process.env.STRIPE_PRICE_SOUSCHEF || ''

// Map tier names to price IDs
const TIER_TO_PRICE: Record<string, string> = {
    'chef': PRICE_CHEF,
    'souschef': PRICE_SOUSCHEF,
}

// Map price IDs to plan names
const PRICE_TO_PLAN: Record<string, string> = {
    [PRICE_CHEF]: 'pro',
    [PRICE_SOUSCHEF]: 'team',
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
        const { priceId: tierOrPriceId, workspaceId, successUrl, cancelUrl } = body

        if (!tierOrPriceId || !workspaceId) {
            return NextResponse.json({ error: 'Missing priceId or workspaceId' }, { status: 400 })
        }

        // Resolve tier name to price ID if needed
        const priceId = TIER_TO_PRICE[tierOrPriceId] || tierOrPriceId

        if (!priceId) {
            return NextResponse.json({
                error: 'Price not configured. Please set STRIPE_PRICE_CHEF and STRIPE_PRICE_SOUSCHEF in environment.'
            }, { status: 500 })
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
            .select('id, slug, name, stripe_customer_id')
            .eq('id', workspaceId)
            .single()

        if (wsError || !workspace) {
            return NextResponse.json({ error: 'Workspace not found' }, { status: 404 })
        }

        // Get or create Stripe customer
        let customerId = workspace.stripe_customer_id
        if (!customerId) {
            const customer = await stripe.customers.create({
                email: user.email,
                metadata: {
                    workspace_id: workspace.id,
                    workspace_slug: workspace.slug,
                    user_id: user.id,
                },
            })
            customerId = customer.id

            // Update workspace with customer ID
            await supabase
                .from('workspaces')
                .update({ stripe_customer_id: customerId })
                .eq('id', workspaceId)
        }

        // Create checkout session
        const session = await stripe.checkout.sessions.create({
            customer: customerId,
            payment_method_types: ['card'],
            line_items: [{
                price: priceId,
                quantity: 1,
            }],
            mode: 'subscription',
            success_url: successUrl || `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/dashboard/billing?success=true`,
            cancel_url: cancelUrl || `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/dashboard/billing?canceled=true`,
            metadata: {
                workspace_id: workspaceId,
            },
        })

        return NextResponse.json({
            checkoutUrl: session.url,
            sessionId: session.id,
        })
    } catch (error) {
        console.error('Checkout error:', error)
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Checkout failed' },
            { status: 500 }
        )
    }
}
