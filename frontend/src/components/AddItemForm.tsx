import { useState, useRef } from 'react'
import { useAddItems } from '../hooks/useItems'

export default function AddItemForm() {
  const [text, setText] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const addItems = useAddItems()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim()) return

    try {
      const result = await addItems.mutateAsync({ text, source: 'ui' })
      setMessage(result.message)
      setText('')
      setTimeout(() => setMessage(null), 3000)
    } catch (error) {
      setMessage('Er ging iets mis')
      setTimeout(() => setMessage(null), 3000)
    }
  }

  return (
    <div className="space-y-2">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          ref={inputRef}
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Voeg toe: brood, 2x melk, 500g gehakt..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-base"
          autoComplete="off"
          autoCapitalize="off"
        />
        <button
          type="submit"
          disabled={!text.trim() || addItems.isPending}
          className="px-6 py-3 bg-primary-600 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed active:bg-primary-700 transition-colors"
        >
          {addItems.isPending ? (
            <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            'Toevoegen'
          )}
        </button>
      </form>

      {/* Success/error message */}
      {message && (
        <div className={`px-4 py-2 rounded-lg text-sm ${
          message.includes('mis')
            ? 'bg-red-50 text-red-700'
            : 'bg-green-50 text-green-700'
        }`}>
          {message}
        </div>
      )}
    </div>
  )
}
