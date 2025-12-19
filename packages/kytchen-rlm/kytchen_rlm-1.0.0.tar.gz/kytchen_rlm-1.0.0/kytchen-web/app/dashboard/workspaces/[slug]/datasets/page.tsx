'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { UploadZone } from '@/components/datasets/upload-zone'
import { Button } from '@/components/ui/button'
import { RefreshCw, AlertCircle } from 'lucide-react'
import { Database } from '@/types/database'
import { PantryContext, PantryGrid, ContextBowl } from '@/components/pantry'

type Dataset = Database['public']['Tables']['datasets']['Row']
type Workspace = Database['public']['Tables']['workspaces']['Row']

export default function DatasetsPage() {
    const params = useParams()
    const router = useRouter()
    const slug = params.slug as string

    const [workspaceId, setWorkspaceId] = useState<string | null>(null)
    const [datasets, setDatasets] = useState<Dataset[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    // Keep a ref to datasets for stable callbacks
    const datasetsRef = useRef(datasets)
    useEffect(() => {
        datasetsRef.current = datasets
    }, [datasets])

    const fetchWorkspaceAndDatasets = useCallback(async () => {
        const supabase = createClient()

        // First, get the workspace ID from slug
        const { data: workspace, error: wsError } = await supabase
            .from('workspaces')
            .select('*')
            .eq('slug', slug)
            .single() as { data: Workspace | null; error: unknown }

        if (wsError || !workspace) {
            setError('Workspace not found')
            setIsLoading(false)
            return
        }

        setWorkspaceId(workspace.id)

        // Fetch datasets for this workspace
        const { data: datasetsData, error: dsError } = await supabase
            .from('datasets')
            .select('*')
            .eq('workspace_id', workspace.id)
            .order('created_at', { ascending: false }) as { data: Dataset[] | null; error: unknown }

        if (dsError) {
            setError('Failed to fetch datasets')
            setIsLoading(false)
            return
        }

        setDatasets(datasetsData || [])
        setIsLoading(false)
    }, [slug])

    useEffect(() => {
        fetchWorkspaceAndDatasets()
    }, [fetchWorkspaceAndDatasets])

    // Poll for processing updates
    useEffect(() => {
        const hasProcessing = datasets.some(d => d.status === 'processing' || d.status === 'uploaded')
        if (!hasProcessing) return

        const interval = setInterval(fetchWorkspaceAndDatasets, 3000)
        return () => clearInterval(interval)
    }, [datasets, fetchWorkspaceAndDatasets])

    const handleUploadComplete = useCallback((dataset: { id: string; name: string; status: string }) => {
        // Refresh the list
        fetchWorkspaceAndDatasets()
    }, [fetchWorkspaceAndDatasets])

    const handleError = useCallback((error: string) => {
        setError(error)
        setTimeout(() => setError(null), 5000)
    }, [])

    const handleDelete = useCallback(async (datasetId: string) => {
        if (!workspaceId) return

        const confirmed = window.confirm('Are you sure you want to delete this dataset?')
        if (!confirmed) return

        try {
            const response = await fetch(
                `/api/datasets?id=${datasetId}&workspace_id=${workspaceId}`,
                { method: 'DELETE' }
            )

            if (!response.ok) {
                const data = await response.json()
                throw new Error(data.error || 'Delete failed')
            }

            // Remove from local state
            setDatasets(prev => prev.filter(d => d.id !== datasetId))
        } catch (err) {
            handleError(err instanceof Error ? err.message : 'Delete failed')
        }
    }, [workspaceId, handleError])

    const handleDownload = useCallback(async (datasetId: string) => {
        if (!workspaceId) return

        const supabase = createClient()
        // Use ref to avoid dependency on datasets
        const dataset = datasetsRef.current.find(d => d.id === datasetId)
        if (!dataset) return

        const { data, error } = await supabase.storage
            .from('pantry')
            .download(dataset.storage_path)

        if (error) {
            handleError('Download failed')
            return
        }

        // Create download link
        const url = URL.createObjectURL(data)
        const a = document.createElement('a')
        a.href = url
        a.download = dataset.name
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
    }, [workspaceId, handleError])

    const handleFireTicket = useCallback((datasetIds: string[]) => {
        // Navigate to create new run with selected datasets
        router.push(`/dashboard/workspaces/${slug}/runs/new?datasets=${datasetIds.join(',')}`)
    }, [router, slug])

    return (
        <PantryContext>
            <div className="space-y-8">
                <div className="flex items-center justify-between">
                    <h1 className="font-heading text-3xl uppercase">Pantry</h1>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={fetchWorkspaceAndDatasets}
                        disabled={isLoading}
                        className="gap-2"
                    >
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                </div>

                {/* Error Banner */}
                {error && (
                    <div className="flex items-center gap-2 p-4 bg-ticket-red/10 border border-ticket-red text-ticket-red">
                        <AlertCircle className="w-4 h-4" />
                        <span className="font-mono text-sm">{error}</span>
                    </div>
                )}

                {/* Upload Zone */}
                {workspaceId && (
                    <UploadZone
                        workspaceId={workspaceId}
                        onUploadComplete={handleUploadComplete}
                        onError={handleError}
                    />
                )}

                {/* Split Layout: Pantry Grid + Context Bowl */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Pantry Grid - Takes 2/3 */}
                    <div className="lg:col-span-2">
                        <h2 className="font-mono text-xs uppercase tracking-widest mb-4">
                            Ingredients
                        </h2>
                        <PantryGrid
                            datasets={datasets}
                            onDelete={handleDelete}
                            onDownload={handleDownload}
                            isLoading={isLoading}
                        />
                    </div>

                    {/* Context Bowl - Takes 1/3, sticky */}
                    <div className="lg:col-span-1">
                        <div className="sticky top-4">
                            <ContextBowl onFireTicket={handleFireTicket} />
                        </div>
                    </div>
                </div>
            </div>
        </PantryContext>
    )
}
