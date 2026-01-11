import { useState } from 'react'
import type { Item } from '../types'
import { useCheckItem, useUncheckItem, useDeleteItem, useUpdateItem } from '../hooks/useItems'

interface ItemRowProps {
  item: Item
}

export default function ItemRow({ item }: ItemRowProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editQty, setEditQty] = useState(item.qty.toString())

  const checkItem = useCheckItem()
  const uncheckItem = useUncheckItem()
  const deleteItem = useDeleteItem()
  const updateItem = useUpdateItem()

  const isChecked = item.status === 'checked'

  const handleToggle = () => {
    if (isChecked) {
      uncheckItem.mutate(item.id)
    } else {
      checkItem.mutate(item.id)
    }
  }

  const handleDelete = () => {
    if (window.confirm(`'${item.name_raw}' verwijderen?`)) {
      deleteItem.mutate(item.id)
    }
  }

  const handleQtyChange = () => {
    const newQty = parseFloat(editQty)
    if (!isNaN(newQty) && newQty > 0 && newQty !== item.qty) {
      updateItem.mutate({
        itemId: item.id,
        request: { qty: newQty },
      })
    }
    setIsEditing(false)
  }

  const formatQty = (qty: number, unit: string | null) => {
    const qtyStr = qty === Math.floor(qty) ? qty.toString() : qty.toFixed(1)
    if (unit) {
      return `${qtyStr}${unit}`
    }
    return qty !== 1 ? `${qtyStr}x` : ''
  }

  return (
    <div className="flex items-center gap-3 px-4 py-3 min-h-[56px]">
      {/* Checkbox */}
      <button
        onClick={handleToggle}
        className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${
          isChecked
            ? 'bg-primary-600 border-primary-600 text-white'
            : 'border-gray-300 hover:border-primary-500'
        }`}
        disabled={checkItem.isPending || uncheckItem.isPending}
      >
        {isChecked && (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </button>

      {/* Item details */}
      <div className="flex-1 min-w-0">
        <div className={`font-medium ${isChecked ? 'line-through text-gray-400' : 'text-gray-900'}`}>
          {item.name_raw}
        </div>
        {item.notes && (
          <div className="text-sm text-gray-500 truncate">{item.notes}</div>
        )}
      </div>

      {/* Quantity */}
      {isEditing ? (
        <input
          type="number"
          value={editQty}
          onChange={(e) => setEditQty(e.target.value)}
          onBlur={handleQtyChange}
          onKeyDown={(e) => e.key === 'Enter' && handleQtyChange()}
          className="w-16 px-2 py-1 text-right border border-gray-300 rounded"
          autoFocus
          step="0.1"
          min="0.1"
        />
      ) : (
        <button
          onClick={() => setIsEditing(true)}
          className="text-gray-500 text-sm px-2 py-1 rounded hover:bg-gray-100"
        >
          {formatQty(item.qty, item.unit) || '1x'}
        </button>
      )}

      {/* Delete button */}
      <button
        onClick={handleDelete}
        className="flex-shrink-0 p-2 text-gray-400 hover:text-red-500 transition-colors"
        disabled={deleteItem.isPending}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  )
}
