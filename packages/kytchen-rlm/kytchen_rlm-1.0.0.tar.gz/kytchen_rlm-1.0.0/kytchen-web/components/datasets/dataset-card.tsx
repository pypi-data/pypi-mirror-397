'use client'

import { memo } from 'react'
import { FileText, Trash2, Download, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { Database } from '@/types/database'

type Dataset = Database['public']['Tables']['datasets']['Row']

interface DatasetCardProps {
    dataset: Dataset
    onDelete?: (id: string) => void
    onDownload?: (id: string) => void
}

const STATUS_CONFIG: Record<string, {
    label: string
    icon: typeof Clock
    variant: 'secondary' | 'default' | 'destructive'
    animate?: boolean
}> = {
    uploaded: {
        label: 'Uploaded',
        icon: Clock,
        variant: 'secondary',
    },
    processing: {
        label: 'Processing',
        icon: Loader2,
        variant: 'secondary',
        animate: true,
    },
    ready: {
        label: 'Ready',
        icon: CheckCircle,
        variant: 'default',
    },
    failed: {
        label: 'Failed',
        icon: AlertCircle,
        variant: 'destructive',
    },
}

function formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatTimeAgo(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 60) return 'Just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hr ago`
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`
    return date.toLocaleDateString()
}

function getFileIcon(mimeType: string | null): string {
    if (!mimeType) return 'txt'
    if (mimeType.includes('pdf')) return 'PDF'
    if (mimeType.includes('word') || mimeType.includes('docx')) return 'DOC'
    if (mimeType.includes('excel') || mimeType.includes('xlsx')) return 'XLS'
    if (mimeType.includes('json')) return 'JSON'
    if (mimeType.includes('csv')) return 'CSV'
    return 'TXT'
}

export const DatasetCard = memo(function DatasetCard({ dataset, onDelete, onDownload }: DatasetCardProps) {
    const status = STATUS_CONFIG[dataset.status] || STATUS_CONFIG.uploaded
    const StatusIcon = status.icon

    return (
        <div className="flex items-center justify-between border border-foreground p-4 bg-background shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
            <div className="flex items-center gap-4">
                {/* File Type Icon */}
                <div className="border border-foreground p-2 bg-surface-elevated min-w-[48px] text-center">
                    <span className="font-mono text-xs font-bold">
                        {getFileIcon(dataset.mime_type)}
                    </span>
                </div>

                {/* File Info */}
                <div className="min-w-0">
                    <p className="font-mono text-sm font-bold truncate max-w-[200px] sm:max-w-none">
                        {dataset.name}
                    </p>
                    <p className="font-mono text-xs text-muted-foreground">
                        {formatBytes(dataset.size_bytes)} • {formatTimeAgo(dataset.created_at)}
                    </p>
                    {dataset.processing_error && (
                        <p className="font-mono text-xs text-ticket-red mt-1">
                            {dataset.processing_error}
                        </p>
                    )}
                </div>
            </div>

            {/* Status & Actions */}
            <div className="flex items-center gap-3">
                {/* Status Badge */}
                <Badge variant={status.variant} className="flex items-center gap-1">
                    <StatusIcon className={cn(
                        "w-3 h-3",
                        status.animate && "animate-spin"
                    )} />
                    <span>{status.label}</span>
                </Badge>

                {/* Actions */}
                <div className="flex items-center gap-1">
                    {onDownload && dataset.status === 'ready' && (
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => onDownload(dataset.id)}
                            title="Download"
                        >
                            <Download className="w-4 h-4" />
                        </Button>
                    )}
                    {onDelete && (
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 hover:bg-destructive hover:text-destructive-foreground"
                            onClick={() => onDelete(dataset.id)}
                            title="Delete"
                        >
                            <Trash2 className="w-4 h-4" />
                        </Button>
                    )}
                </div>
            </div>
        </div>
    )
})

interface DatasetListProps {
    datasets: Dataset[]
    onDelete?: (id: string) => void
    onDownload?: (id: string) => void
    isLoading?: boolean
}

export function DatasetList({ datasets, onDelete, onDownload, isLoading }: DatasetListProps) {
    if (isLoading) {
        return (
            <div className="text-center py-12">
                <Loader2 className="w-8 h-8 mx-auto animate-spin opacity-50" />
                <p className="font-mono text-sm mt-4 opacity-50">Loading datasets...</p>
            </div>
        )
    }

    if (datasets.length === 0) {
        return (
            <div className="text-center py-12 border-2 border-dashed border-foreground/30">
                <FileText className="w-12 h-12 mx-auto opacity-30" />
                <p className="font-mono text-sm mt-4 opacity-50">No datasets yet</p>
                <p className="font-mono text-xs mt-2 opacity-30">
                    Upload files to get started
                </p>
            </div>
        )
    }

    return (
        <div className="grid grid-cols-1 gap-4">
            {datasets.map((dataset) => (
                <DatasetCard
                    key={dataset.id}
                    dataset={dataset}
                    onDelete={onDelete}
                    onDownload={onDownload}
                />
            ))}
        </div>
    )
}
