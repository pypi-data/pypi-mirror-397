'use client'

import { DndContext, DragEndEvent, DragOverlay, DragStartEvent, closestCenter } from '@dnd-kit/core'
import { useState, ReactNode } from 'react'
import { useBowlStore } from '@/lib/stores/bowl-store'
import { Database } from '@/types/database'
import { DatasetCard } from '@/components/datasets/dataset-card'

type Dataset = Database['public']['Tables']['datasets']['Row']

interface PantryContextProps {
  children: ReactNode
}

export function PantryContext({ children }: PantryContextProps) {
  const { addIngredient } = useBowlStore()
  const [activeDataset, setActiveDataset] = useState<Dataset | null>(null)

  function handleDragStart(event: DragStartEvent) {
    const dataset = event.active.data.current?.dataset as Dataset | undefined
    if (dataset) {
      setActiveDataset(dataset)
    }
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    setActiveDataset(null)

    // Check if dropped on the bowl
    if (over?.id === 'context-bowl') {
      const dataset = active.data.current?.dataset as Dataset | undefined
      if (dataset) {
        addIngredient(dataset)
      }
    }
  }

  return (
    <DndContext
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      {children}

      {/* Drag Overlay - Shows preview while dragging */}
      <DragOverlay dropAnimation={{
        duration: 200,
        easing: 'cubic-bezier(0.18, 0.67, 0.6, 1.22)',
      }}>
        {activeDataset && (
          <div className="opacity-80 rotate-2 scale-105">
            <DatasetCard dataset={activeDataset} />
          </div>
        )}
      </DragOverlay>
    </DndContext>
  )
}
