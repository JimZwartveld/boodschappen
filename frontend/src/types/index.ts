// API Types

export interface Category {
  id: string
  name: string
  name_nl: string
  icon: string | null
  sort_order: number
}

export type ItemStatus = 'open' | 'checked' | 'removed'
export type Store = 'AH' | 'Jumbo'

export interface Item {
  id: string
  name_raw: string
  name_norm: string
  category: Category | null
  qty: number
  unit: string | null
  notes: string | null
  status: ItemStatus
  preferred_store: Store | null
  snooze_until: string | null
  created_at: string
  updated_at: string
  last_added_at: string
}

export interface AddedItem {
  id: string
  name: string
  qty: number
  unit: string | null
  is_new: boolean
}

export interface AddItemsResponse {
  count: number
  items: AddedItem[]
  message: string
}

export interface AddItemsRequest {
  text: string
  source?: string
  category?: string
  preferred_store?: Store
}

export interface UpdateItemRequest {
  name_raw?: string
  qty?: number
  unit?: string | null
  notes?: string | null
  category_id?: string | null
  preferred_store?: Store | null
  snooze_until?: string | null
}

// Grouped items by category
export interface GroupedItems {
  category: Category | null
  items: Item[]
}
