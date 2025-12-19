'use client'

import { DraggableDatasetCard } from './DraggableDatasetCard'
import { Database } from '@/types/database'
import { FileText, Loader2 } from 'lucide-react'

type Dataset = Database['public']['Tables']['datasets']['Row']

interface PantryGridProps {
  datasets: Dataset[]
  onDelete?: (id: string) => void
  onDownload?: (id: string) => void
  isLoading?: boolean
}

export function PantryGrid({
  datasets,
  onDelete,
  onDownload,
  isLoading
}: PantryGridProps) {
  if (isLoading) {
    return (
      <div className="text-center py-12">
        <Loader2 className="w-8 h-8 mx-auto animate-spin opacity-50" />
        <p className="font-mono text-sm mt-4 opacity-50">Loading pantry...</p>
      </div>
    )
  }

  if (datasets.length === 0) {
    return (
      <div className="text-center py-12 border-2 border-dashed border-foreground/30">
        <FileText className="w-12 h-12 mx-auto opacity-30" />
        <p className="font-mono text-sm mt-4 opacity-50">Pantry is empty</p>
        <p className="font-mono text-xs mt-2 opacity-30">
          Upload ingredients to get started
        </p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {datasets.map((dataset) => (
        <DraggableDatasetCard
          key={dataset.id}
          dataset={dataset}
          onDelete={onDelete}
          onDownload={onDownload}
        />
      ))}
    </div>
  )
}
