'use client'

import { motion } from 'framer-motion'
import { X } from 'lucide-react'
import { useBowlStore } from '@/lib/stores/bowl-store'
import { Database } from '@/types/database'
import { cn } from '@/lib/utils'

type Dataset = Database['public']['Tables']['datasets']['Row']

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function getFileIcon(mimeType: string | null): string {
  if (!mimeType) return 'TXT'
  if (mimeType.includes('pdf')) return 'PDF'
  if (mimeType.includes('json')) return 'JSON'
  if (mimeType.includes('csv')) return 'CSV'
  return 'TXT'
}

interface ContextBowlItemProps {
  dataset: Dataset
}

export function ContextBowlItem({ dataset }: ContextBowlItemProps) {
  const { removeIngredient } = useBowlStore()

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.8, y: -20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.8, x: 100 }}
      transition={{
        type: 'spring',
        stiffness: 500,
        damping: 30,
        layout: { type: 'spring', stiffness: 300, damping: 25 }
      }}
      className="flex items-center gap-3 p-2 bg-white border border-foreground shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] group"
    >
      {/* File Type Badge */}
      <div className="border border-foreground p-1.5 bg-stone-50 min-w-[36px] text-center">
        <span className="font-mono text-[10px] font-bold">
          {getFileIcon(dataset.mime_type)}
        </span>
      </div>

      {/* File Info */}
      <div className="flex-1 min-w-0">
        <p className="font-mono text-xs font-bold truncate">
          {dataset.name}
        </p>
        <p className="font-mono text-[10px] text-muted-foreground">
          {formatBytes(dataset.size_bytes)}
        </p>
      </div>

      {/* Remove Button */}
      <button
        onClick={() => removeIngredient(dataset.id)}
        className={cn(
          "p-1.5 opacity-0 group-hover:opacity-100 transition-opacity",
          "hover:bg-ticket-red hover:text-white border border-transparent hover:border-foreground"
        )}
      >
        <X className="w-3 h-3" />
      </button>
    </motion.div>
  )
}
