import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

type CreateWorkspaceBody = {
    name?: string
}

export async function POST(request: Request) {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const json = (await request.json()) as CreateWorkspaceBody
    const name = typeof json?.name === 'string' ? json.name : ''
    if (!name) {
        return NextResponse.json({ error: 'Missing name' }, { status: 400 })
    }
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-')

    const { data, error } = await supabase
        .from('workspaces')
        .insert({ name, slug, plan: 'free' })
        .select()
        .single()

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 400 })
    }

    // Add user as owner
    const { error: memberError } = await supabase
        .from('members')
        .insert({ workspace_id: data.id, user_id: user.id, role: 'owner' })

    if (memberError) {
        return NextResponse.json({ error: memberError.message }, { status: 400 })
    }

    return NextResponse.json(data)
}

export async function GET() {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // RLS will handle filtering, but we can also filter explicitly if needed
    const { data, error } = await supabase.from('workspaces').select('*')

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 400 })
    }

    return NextResponse.json(data)
}
