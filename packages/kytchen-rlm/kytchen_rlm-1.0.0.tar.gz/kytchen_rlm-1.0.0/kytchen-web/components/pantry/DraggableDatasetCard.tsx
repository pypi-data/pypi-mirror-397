'use client'

import { memo } from 'react'
import { useDraggable } from '@dnd-kit/core'
import { CSS } from '@dnd-kit/utilities'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { DatasetCard } from '@/components/datasets/dataset-card'
import { Database } from '@/types/database'
import { GripVertical } from 'lucide-react'

type Dataset = Database['public']['Tables']['datasets']['Row']

interface DraggableDatasetCardProps {
  dataset: Dataset
  onDelete?: (id: string) => void
  onDownload?: (id: string) => void
}

export const DraggableDatasetCard = memo(function DraggableDatasetCard({
  dataset,
  onDelete,
  onDownload
}: DraggableDatasetCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging
  } = useDraggable({
    id: dataset.id,
    data: { dataset } // Pass dataset in drag data
  })

  return (
    <motion.div
      ref={setNodeRef}
      style={{
        transform: CSS.Translate.toString(transform),
      }}
      animate={{
        scale: isDragging ? 1.03 : 1,
        boxShadow: isDragging
          ? '8px 8px 0px 0px rgba(0,0,0,0.8)'
          : '2px 2px 0px 0px rgba(0,0,0,1)',
        opacity: isDragging ? 0.9 : 1,
        zIndex: isDragging ? 50 : 1,
        rotate: isDragging ? 2 : 0,
      }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      className={cn(
        "relative",
        isDragging && "cursor-grabbing"
      )}
    >
      {/* Drag Handle */}
      <div
        {...attributes}
        {...listeners}
        className={cn(
          "absolute left-0 top-0 bottom-0 w-10 flex items-center justify-center z-10",
          "cursor-grab active:cursor-grabbing",
          "bg-stone-100 border-r border-foreground",
          "hover:bg-blue-tape/10 transition-colors"
        )}
      >
        <GripVertical className="w-4 h-4 text-stone-400" />
      </div>

      {/* Dataset Card with padding for handle */}
      <div className="pl-10">
        <DatasetCard
          dataset={dataset}
          onDelete={onDelete}
          onDownload={onDownload}
        />
      </div>
    </motion.div>
  )
})
