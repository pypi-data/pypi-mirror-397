import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'
import crypto from 'crypto'

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const ALLOWED_MIME_TYPES = [
    'text/plain',
    'text/csv',
    'text/markdown',
    'application/json',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.ms-excel',
]

export async function POST(request: Request) {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    try {
        const formData = await request.formData()
        const file = formData.get('file') as File | null
        const workspaceId = formData.get('workspace_id') as string | null

        if (!file) {
            return NextResponse.json({ error: 'No file provided' }, { status: 400 })
        }

        if (!workspaceId) {
            return NextResponse.json({ error: 'No workspace_id provided' }, { status: 400 })
        }

        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            return NextResponse.json({ error: 'File too large (max 10MB)' }, { status: 400 })
        }

        // Validate MIME type
        const mimeType = file.type || 'application/octet-stream'
        if (!ALLOWED_MIME_TYPES.includes(mimeType)) {
            return NextResponse.json({ error: `File type not allowed: ${mimeType}` }, { status: 400 })
        }

        // Verify user has access to workspace
        const { data: membership } = await supabase
            .from('members')
            .select('role')
            .eq('workspace_id', workspaceId)
            .eq('user_id', user.id)
            .single()

        if (!membership) {
            return NextResponse.json({ error: 'Access denied to workspace' }, { status: 403 })
        }

        // Generate unique filename
        const datasetId = crypto.randomUUID()
        const storagePath = `${workspaceId}/${datasetId}`

        // Read file content
        const arrayBuffer = await file.arrayBuffer()
        const content = new Uint8Array(arrayBuffer)

        // Compute hash
        const hash = crypto.createHash('sha256').update(content).digest('hex')
        const contentHash = `sha256:${hash}`

        // Upload to Supabase Storage (pantry bucket)
        const { error: uploadError } = await supabase.storage
            .from('pantry')
            .upload(storagePath, content, {
                contentType: mimeType,
                upsert: false,
            })

        if (uploadError) {
            console.error('Storage upload error:', uploadError)
            return NextResponse.json({ error: 'Failed to upload file' }, { status: 500 })
        }

        // Create dataset record in database
        const { data: dataset, error: insertError } = await supabase
            .from('datasets')
            .insert({
                id: datasetId,
                workspace_id: workspaceId,
                name: file.name,
                storage_bucket: 'pantry',
                storage_path: storagePath,
                size_bytes: file.size,
                content_hash: contentHash,
                mime_type: mimeType,
                status: 'uploaded',
            })
            .select()
            .single()

        if (insertError) {
            console.error('Database insert error:', insertError)
            // Clean up storage on failure
            await supabase.storage.from('pantry').remove([storagePath])
            return NextResponse.json({ error: 'Failed to create dataset record' }, { status: 500 })
        }

        // Note: In production, this would trigger a background processing job
        // For now, we'll mark it as 'ready' since we're storing the raw file
        // The Python backend handles actual processing

        return NextResponse.json({
            id: dataset.id,
            name: dataset.name,
            size_bytes: dataset.size_bytes,
            mime_type: dataset.mime_type,
            status: dataset.status,
            created_at: dataset.created_at,
        })
    } catch (error) {
        console.error('Upload error:', error)
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
    }
}

export async function GET(request: Request) {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const workspaceId = searchParams.get('workspace_id')

    if (!workspaceId) {
        return NextResponse.json({ error: 'Missing workspace_id' }, { status: 400 })
    }

    // Verify user has access to workspace
    const { data: membership } = await supabase
        .from('members')
        .select('role')
        .eq('workspace_id', workspaceId)
        .eq('user_id', user.id)
        .single()

    if (!membership) {
        return NextResponse.json({ error: 'Access denied to workspace' }, { status: 403 })
    }

    // Fetch datasets
    const { data: datasets, error } = await supabase
        .from('datasets')
        .select('*')
        .eq('workspace_id', workspaceId)
        .order('created_at', { ascending: false })

    if (error) {
        console.error('Database query error:', error)
        return NextResponse.json({ error: 'Failed to fetch datasets' }, { status: 500 })
    }

    return NextResponse.json({ datasets })
}

export async function DELETE(request: Request) {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const datasetId = searchParams.get('id')
    const workspaceId = searchParams.get('workspace_id')

    if (!datasetId || !workspaceId) {
        return NextResponse.json({ error: 'Missing id or workspace_id' }, { status: 400 })
    }

    // Verify user has access to workspace
    const { data: membership } = await supabase
        .from('members')
        .select('role')
        .eq('workspace_id', workspaceId)
        .eq('user_id', user.id)
        .single()

    if (!membership) {
        return NextResponse.json({ error: 'Access denied to workspace' }, { status: 403 })
    }

    // Get dataset to find storage path
    const { data: dataset, error: fetchError } = await supabase
        .from('datasets')
        .select('storage_path')
        .eq('id', datasetId)
        .eq('workspace_id', workspaceId)
        .single()

    if (fetchError || !dataset) {
        return NextResponse.json({ error: 'Dataset not found' }, { status: 404 })
    }

    // Delete from storage
    const { error: storageError } = await supabase.storage
        .from('pantry')
        .remove([dataset.storage_path])

    if (storageError) {
        console.error('Storage delete error:', storageError)
        // Continue anyway to delete the record
    }

    // Delete from database
    const { error: deleteError } = await supabase
        .from('datasets')
        .delete()
        .eq('id', datasetId)
        .eq('workspace_id', workspaceId)

    if (deleteError) {
        console.error('Database delete error:', deleteError)
        return NextResponse.json({ error: 'Failed to delete dataset' }, { status: 500 })
    }

    return NextResponse.json({ deleted: true })
}
