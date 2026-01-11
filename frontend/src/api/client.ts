import type { Item, Category, AddItemsRequest, AddItemsResponse, UpdateItemRequest } from '../types'

const API_BASE = '/api/v1'

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Er ging iets mis' }))
    throw new Error(error.detail || 'Er ging iets mis')
  }

  // Handle empty responses
  const text = await response.text()
  if (!text) return {} as T

  return JSON.parse(text)
}

// Categories
export async function getCategories(): Promise<Category[]> {
  return fetchApi<Category[]>('/categories')
}

// Items
export async function getItems(status?: string): Promise<Item[]> {
  const params = status ? `?status=${status}` : ''
  return fetchApi<Item[]>(`/items${params}`)
}

export async function addItems(request: AddItemsRequest): Promise<AddItemsResponse> {
  return fetchApi<AddItemsResponse>('/items:add', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function checkItem(itemId: string): Promise<Item> {
  return fetchApi<Item>(`/items/${itemId}:check`, {
    method: 'POST',
  })
}

export async function uncheckItem(itemId: string): Promise<Item> {
  return fetchApi<Item>(`/items/${itemId}:uncheck`, {
    method: 'POST',
  })
}

export async function updateItem(itemId: string, request: UpdateItemRequest): Promise<Item> {
  return fetchApi<Item>(`/items/${itemId}`, {
    method: 'PATCH',
    body: JSON.stringify(request),
  })
}

export async function deleteItem(itemId: string): Promise<void> {
  await fetchApi(`/items/${itemId}`, {
    method: 'DELETE',
  })
}

// Export
export async function exportItems(store: string): Promise<string> {
  const response = await fetch(`${API_BASE}/export/${store}?format=plaintext`)
  if (!response.ok) {
    throw new Error('Export mislukt')
  }
  return response.text()
}

// Sync to AH
export interface SyncResponse {
  synced: number
  failed: number
  not_found: number
  details: { item: string; status: string; ah_product?: string; error?: string }[]
}

export async function syncToAH(): Promise<SyncResponse> {
  return fetchApi<SyncResponse>('/sync/ah', {
    method: 'POST',
  })
}
