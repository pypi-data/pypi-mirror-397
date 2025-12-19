'use client'

import { useDroppable } from '@dnd-kit/core'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { useBowlStore } from '@/lib/stores/bowl-store'
import { ContextBowlItem } from './ContextBowlItem'
import { Soup, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ContextBowlProps {
  onFireTicket?: (datasetIds: string[]) => void
}

export function ContextBowl({ onFireTicket }: ContextBowlProps) {
  const { ingredients, clearBowl } = useBowlStore()

  const { isOver, setNodeRef } = useDroppable({
    id: 'context-bowl',
  })

  const handleFireTicket = () => {
    if (onFireTicket && ingredients.length > 0) {
      onFireTicket(ingredients.map(i => i.id))
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Bowl Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-mono text-xs uppercase tracking-widest flex items-center gap-2">
          <Soup className="w-4 h-4" />
          Context Bowl
        </h3>
        {ingredients.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearBowl}
            className="h-6 px-2 text-xs hover:bg-ticket-red/10 hover:text-ticket-red"
          >
            <Trash2 className="w-3 h-3 mr-1" />
            Clear
          </Button>
        )}
      </div>

      {/* Drop Zone */}
      <motion.div
        ref={setNodeRef}
        animate={{
          scale: isOver ? 1.02 : 1,
          borderColor: isOver ? '#2563EB' : '#0F172A', // blue-tape : sharpie-black
          boxShadow: isOver
            ? '0 0 20px rgba(37, 99, 235, 0.3)'
            : '4px 4px 0px 0px rgba(0,0,0,1)',
        }}
        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
        className={cn(
          "flex-1 min-h-[200px] border-2 border-dashed p-4",
          "bg-stone-50 transition-colors",
          isOver && "bg-blue-tape/5"
        )}
      >
        {ingredients.length === 0 ? (
          <motion.div
            className="h-full flex flex-col items-center justify-center text-center py-8"
            animate={{ opacity: isOver ? 1 : 0.5 }}
          >
            <Soup className={cn(
              "w-12 h-12 mb-4 transition-colors",
              isOver ? "text-blue-tape" : "text-stone-300"
            )} />
            <p className="font-mono text-sm">
              {isOver ? (
                <span className="text-blue-tape font-bold">Drop to add ingredient</span>
              ) : (
                <span className="text-stone-400">Drag datasets here</span>
              )}
            </p>
            <p className="font-mono text-xs text-stone-400 mt-2">
              {ingredients.length} ingredients
            </p>
          </motion.div>
        ) : (
          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {ingredients.map((dataset) => (
                <ContextBowlItem key={dataset.id} dataset={dataset} />
              ))}
            </AnimatePresence>
          </div>
        )}
      </motion.div>

      {/* Bowl Footer - Fire Button */}
      {ingredients.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4"
        >
          <Button
            onClick={handleFireTicket}
            className="w-full shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] font-mono uppercase tracking-wider border-2 border-foreground"
          >
            Fire Ticket ({ingredients.length} {ingredients.length === 1 ? 'ingredient' : 'ingredients'})
          </Button>
        </motion.div>
      )}
    </div>
  )
}
