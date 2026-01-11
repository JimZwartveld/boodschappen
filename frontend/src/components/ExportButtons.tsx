import { useState } from 'react'
import { exportItems } from '../api/client'

export default function ExportButtons() {
  const [exporting, setExporting] = useState<string | null>(null)
  const [copied, setCopied] = useState<string | null>(null)

  const handleExport = async (store: string) => {
    setExporting(store)
    try {
      const text = await exportItems(store)

      // Copy to clipboard
      await navigator.clipboard.writeText(text)
      setCopied(store)
      setTimeout(() => setCopied(null), 2000)

      // Show preview
      alert(text)
    } catch (error) {
      alert('Export mislukt')
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className="grid grid-cols-2 gap-3">
      <button
        onClick={() => handleExport('AH')}
        disabled={exporting !== null}
        className="flex items-center justify-center gap-2 py-4 bg-blue-600 text-white font-medium rounded-lg disabled:opacity-50 active:bg-blue-700 transition-colors"
      >
        {exporting === 'AH' ? (
          <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : copied === 'AH' ? (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Gekopieerd!
          </>
        ) : (
          <>
            <span className="text-lg">🛒</span>
            Export AH
          </>
        )}
      </button>

      <button
        onClick={() => handleExport('Jumbo')}
        disabled={exporting !== null}
        className="flex items-center justify-center gap-2 py-4 bg-yellow-500 text-white font-medium rounded-lg disabled:opacity-50 active:bg-yellow-600 transition-colors"
      >
        {exporting === 'Jumbo' ? (
          <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : copied === 'Jumbo' ? (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Gekopieerd!
          </>
        ) : (
          <>
            <span className="text-lg">🛒</span>
            Export Jumbo
          </>
        )}
      </button>
    </div>
  )
}
