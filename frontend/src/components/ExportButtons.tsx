import { useState } from 'react'
import { exportItems } from '../api/client'

export default function ExportButtons() {
  const [exporting, setExporting] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleExport = async () => {
    setExporting(true)
    try {
      const text = await exportItems('all')

      // Check if clipboard is available (requires HTTPS)
      const isSecure = window.isSecureContext

      if (isSecure && navigator.clipboard) {
        try {
          await navigator.clipboard.writeText(text)
          setCopied(true)
          setTimeout(() => setCopied(false), 2000)
          return
        } catch {
          // Fall through to prompt
        }
      }

      // Fallback: show prompt for manual copy
      window.prompt('Kopieer deze tekst (selecteer alles met Ctrl+A):', text)
    } catch (error) {
      alert('Export mislukt')
    } finally {
      setExporting(false)
    }
  }

  return (
    <button
      onClick={handleExport}
      disabled={exporting}
      className="w-full flex items-center justify-center gap-2 py-4 bg-blue-600 text-white font-medium rounded-lg disabled:opacity-50 active:bg-blue-700 transition-colors"
    >
      {exporting ? (
        <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
      ) : copied ? (
        <>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Gekopieerd!
        </>
      ) : (
        <>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
          </svg>
          Kopieer lijst
        </>
      )}
    </button>
  )
}
