import { NextResponse } from 'next/server'
import { headers } from 'next/headers'
import Stripe from 'stripe'
import { createClient, SupabaseClient } from '@supabase/supabase-js'

function getStripe() {
    return new Stripe(process.env.STRIPE_SECRET_KEY!, {
        apiVersion: '2025-12-15.clover',
    })
}

function getSupabase() {
    return createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.SUPABASE_SERVICE_ROLE_KEY!
    )
}

function getPriceToPlans() {
    const PRICE_CHEF = process.env.STRIPE_PRICE_CHEF || ''
    const PRICE_SOUSCHEF = process.env.STRIPE_PRICE_SOUSCHEF || ''
    return {
        [PRICE_CHEF]: 'pro',
        [PRICE_SOUSCHEF]: 'team',
    } as Record<string, string>
}

export async function POST(request: Request) {
    const stripe = getStripe()
    const supabase = getSupabase()
    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!
    const PRICE_TO_PLAN = getPriceToPlans()

    const body = await request.text()
    const headersList = await headers()
    const signature = headersList.get('stripe-signature')

    if (!signature) {
        return NextResponse.json({ error: 'Missing signature' }, { status: 400 })
    }

    let event: Stripe.Event

    try {
        event = stripe.webhooks.constructEvent(body, signature, webhookSecret)
    } catch (err) {
        console.error('Webhook signature verification failed:', err)
        return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
    }

    try {
        switch (event.type) {
            case 'checkout.session.completed':
                await handleCheckoutCompleted(event.data.object as Stripe.Checkout.Session, stripe, supabase, PRICE_TO_PLAN)
                break
            case 'customer.subscription.updated':
                await handleSubscriptionUpdated(event.data.object as Stripe.Subscription, supabase, PRICE_TO_PLAN)
                break
            case 'customer.subscription.deleted':
                await handleSubscriptionDeleted(event.data.object as Stripe.Subscription, supabase)
                break
            case 'invoice.payment_failed':
                await handlePaymentFailed(event.data.object as Stripe.Invoice, supabase)
                break
            default:
                console.log(`Unhandled event type: ${event.type}`)
        }

        return NextResponse.json({ received: true })
    } catch (error) {
        console.error('Webhook handler error:', error)
        return NextResponse.json(
            { error: 'Webhook handler failed' },
            { status: 500 }
        )
    }
}

async function handleCheckoutCompleted(
    session: Stripe.Checkout.Session,
    stripe: Stripe,
    supabase: SupabaseClient,
    PRICE_TO_PLAN: Record<string, string>
) {
    const workspaceId = session.metadata?.workspace_id
    const customerId = session.customer as string
    const subscriptionId = session.subscription as string

    if (!workspaceId || !subscriptionId) {
        console.error('Missing workspace_id or subscription in checkout session')
        return
    }

    // Get subscription details
    const subscriptionResponse = await stripe.subscriptions.retrieve(subscriptionId)
    const subscription = subscriptionResponse as Stripe.Subscription
    const priceId = subscription.items.data[0]?.price.id
    const newPlan = PRICE_TO_PLAN[priceId] || 'free'

    // Get period from the first subscription item
    const item = subscription.items.data[0]
    const periodStart = item?.current_period_start
    const periodEnd = item?.current_period_end

    // Update workspace plan
    await supabase
        .from('workspaces')
        .update({
            plan: newPlan,
            stripe_customer_id: customerId,
        })
        .eq('id', workspaceId)

    // Upsert billing record
    await supabase
        .from('billing')
        .upsert({
            workspace_id: workspaceId,
            stripe_customer_id: customerId,
            stripe_subscription_id: subscriptionId,
            stripe_price_id: priceId,
            subscription_status: subscription.status,
            current_period_start: periodStart ? new Date(periodStart * 1000).toISOString() : null,
            current_period_end: periodEnd ? new Date(periodEnd * 1000).toISOString() : null,
            cancel_at_period_end: subscription.cancel_at_period_end,
        }, {
            onConflict: 'workspace_id',
        })

    console.log(`Checkout completed: workspace ${workspaceId} upgraded to ${newPlan}`)
}

async function handleSubscriptionUpdated(
    subscription: Stripe.Subscription,
    supabase: SupabaseClient,
    PRICE_TO_PLAN: Record<string, string>
) {
    const customerId = subscription.customer as string
    const priceId = subscription.items.data[0]?.price.id
    const newPlan = PRICE_TO_PLAN[priceId] || 'free'

    // Get period from the first subscription item
    const item = subscription.items.data[0]
    const periodStart = item?.current_period_start
    const periodEnd = item?.current_period_end

    // Find workspace by customer ID
    const { data: workspace } = await supabase
        .from('workspaces')
        .select('id')
        .eq('stripe_customer_id', customerId)
        .single()

    if (!workspace) {
        console.error('No workspace found for customer:', customerId)
        return
    }

    // Update workspace plan if active
    if (subscription.status === 'active') {
        await supabase
            .from('workspaces')
            .update({ plan: newPlan })
            .eq('id', workspace.id)
    }

    // Update billing record
    await supabase
        .from('billing')
        .update({
            stripe_subscription_id: subscription.id,
            stripe_price_id: priceId,
            subscription_status: subscription.status,
            current_period_start: periodStart ? new Date(periodStart * 1000).toISOString() : null,
            current_period_end: periodEnd ? new Date(periodEnd * 1000).toISOString() : null,
            cancel_at_period_end: subscription.cancel_at_period_end,
        })
        .eq('workspace_id', workspace.id)

    console.log(`Subscription updated: workspace ${workspace.id} status ${subscription.status}`)
}

async function handleSubscriptionDeleted(
    subscription: Stripe.Subscription,
    supabase: SupabaseClient
) {
    const customerId = subscription.customer as string

    // Find workspace by customer ID
    const { data: workspace } = await supabase
        .from('workspaces')
        .select('id')
        .eq('stripe_customer_id', customerId)
        .single()

    if (!workspace) {
        console.error('No workspace found for customer:', customerId)
        return
    }

    // Downgrade to free
    await supabase
        .from('workspaces')
        .update({ plan: 'free' })
        .eq('id', workspace.id)

    // Update billing record
    await supabase
        .from('billing')
        .update({
            subscription_status: 'canceled',
            cancel_at_period_end: false,
        })
        .eq('workspace_id', workspace.id)

    console.log(`Subscription deleted: workspace ${workspace.id} downgraded to free`)
}

async function handlePaymentFailed(
    invoice: Stripe.Invoice,
    supabase: SupabaseClient
) {
    // Access subscription ID from the invoice - use type assertion for API version compatibility
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const invoiceData = invoice as any
    const subscriptionId = String(invoiceData.subscription ?? invoiceData.subscription_details?.subscription ?? '')

    if (!subscriptionId) return

    // Find billing record by subscription ID
    const { data: billing } = await supabase
        .from('billing')
        .select('workspace_id')
        .eq('stripe_subscription_id', subscriptionId)
        .single()

    if (!billing) {
        console.error('No billing record found for subscription:', subscriptionId)
        return
    }

    // Mark as past_due
    await supabase
        .from('billing')
        .update({ subscription_status: 'past_due' })
        .eq('workspace_id', billing.workspace_id)

    console.log(`Payment failed: workspace ${billing.workspace_id} marked as past_due`)
}
