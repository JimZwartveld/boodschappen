import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../api/client'
import type { Item, AddItemsRequest, UpdateItemRequest, GroupedItems, Category } from '../types'

export function useItems() {
  return useQuery({
    queryKey: ['items'],
    queryFn: () => api.getItems(),
  })
}

export function useCategories() {
  return useQuery({
    queryKey: ['categories'],
    queryFn: () => api.getCategories(),
  })
}

export function useAddItems() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (request: AddItemsRequest) => api.addItems(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })
}

export function useCheckItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (itemId: string) => api.checkItem(itemId),
    onMutate: async (itemId) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['items'] })
      const previousItems = queryClient.getQueryData<Item[]>(['items'])

      queryClient.setQueryData<Item[]>(['items'], (old) =>
        old?.map((item) =>
          item.id === itemId ? { ...item, status: 'checked' as const } : item
        )
      )

      return { previousItems }
    },
    onError: (_err, _itemId, context) => {
      queryClient.setQueryData(['items'], context?.previousItems)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })
}

export function useUncheckItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (itemId: string) => api.uncheckItem(itemId),
    onMutate: async (itemId) => {
      await queryClient.cancelQueries({ queryKey: ['items'] })
      const previousItems = queryClient.getQueryData<Item[]>(['items'])

      queryClient.setQueryData<Item[]>(['items'], (old) =>
        old?.map((item) =>
          item.id === itemId ? { ...item, status: 'open' as const } : item
        )
      )

      return { previousItems }
    },
    onError: (_err, _itemId, context) => {
      queryClient.setQueryData(['items'], context?.previousItems)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })
}

export function useUpdateItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ itemId, request }: { itemId: string; request: UpdateItemRequest }) =>
      api.updateItem(itemId, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })
}

export function useDeleteItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (itemId: string) => api.deleteItem(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })
}

// Helper to group items by category
export function groupItemsByCategory(items: Item[], categories: Category[]): GroupedItems[] {
  const categoryMap = new Map<string | null, Item[]>()

  // Initialize with categories in order
  for (const category of categories) {
    categoryMap.set(category.id, [])
  }
  categoryMap.set(null, []) // Uncategorized

  // Group items
  for (const item of items) {
    const categoryId = item.category?.id ?? null
    const group = categoryMap.get(categoryId) ?? []
    group.push(item)
    categoryMap.set(categoryId, group)
  }

  // Convert to array, maintaining category order
  const result: GroupedItems[] = []

  for (const category of categories) {
    const items = categoryMap.get(category.id) ?? []
    if (items.length > 0) {
      result.push({ category, items })
    }
  }

  // Add uncategorized at the end
  const uncategorized = categoryMap.get(null) ?? []
  if (uncategorized.length > 0) {
    result.push({ category: null, items: uncategorized })
  }

  return result
}
