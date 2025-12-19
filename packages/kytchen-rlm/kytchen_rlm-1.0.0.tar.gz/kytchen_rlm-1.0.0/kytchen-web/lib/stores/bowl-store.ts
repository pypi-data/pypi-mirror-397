import { create } from 'zustand'
import { Database } from '@/types/database'

type Dataset = Database['public']['Tables']['datasets']['Row']

interface BowlState {
  // Datasets currently in the bowl
  ingredients: Dataset[]
  // Add a dataset to the bowl
  addIngredient: (dataset: Dataset) => void
  // Remove a dataset from the bowl
  removeIngredient: (id: string) => void
  // Clear the bowl
  clearBowl: () => void
  // Reorder ingredients (for sortable)
  reorderIngredients: (activeId: string, overId: string) => void
}

export const useBowlStore = create<BowlState>((set) => ({
  ingredients: [],

  addIngredient: (dataset) => set((state) => {
    // Prevent duplicates
    if (state.ingredients.some(i => i.id === dataset.id)) {
      return state
    }
    return { ingredients: [...state.ingredients, dataset] }
  }),

  removeIngredient: (id) => set((state) => ({
    ingredients: state.ingredients.filter(i => i.id !== id)
  })),

  clearBowl: () => set({ ingredients: [] }),

  reorderIngredients: (activeId, overId) => set((state) => {
    const oldIndex = state.ingredients.findIndex(i => i.id === activeId)
    const newIndex = state.ingredients.findIndex(i => i.id === overId)
    if (oldIndex === -1 || newIndex === -1) return state

    const newIngredients = [...state.ingredients]
    const [removed] = newIngredients.splice(oldIndex, 1)
    newIngredients.splice(newIndex, 0, removed)

    return { ingredients: newIngredients }
  })
}))
