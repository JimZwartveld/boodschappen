import { useState } from 'react'
import { exportItems, syncToAH } from '../api/client'

export default function ExportButtons() {
  const [exporting, setExporting] = useState<string | null>(null)
  const [copied, setCopied] = useState<string | null>(null)
  const [syncing, setSyncing] = useState(false)
  const [syncResult, setSyncResult] = useState<string | null>(null)

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

  const handleSyncToAH = async () => {
    setSyncing(true)
    setSyncResult(null)
    try {
      const result = await syncToAH()
      const message = `${result.synced} toegevoegd aan Appie` +
        (result.not_found > 0 ? `, ${result.not_found} niet gevonden` : '') +
        (result.failed > 0 ? `, ${result.failed} mislukt` : '')
      setSyncResult(message)
      setTimeout(() => setSyncResult(null), 3000)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Sync mislukt')
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="space-y-3">
      {/* Sync to AH button */}
      <button
        onClick={handleSyncToAH}
        disabled={syncing || exporting !== null}
        className="w-full flex items-center justify-center gap-2 py-4 bg-blue-600 text-white font-medium rounded-lg disabled:opacity-50 active:bg-blue-700 transition-colors"
      >
        {syncing ? (
          <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : syncResult ? (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {syncResult}
          </>
        ) : (
          <>
            <span className="text-lg">📲</span>
            Sync naar Appie
          </>
        )}
      </button>

      {/* Export buttons */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => handleExport('AH')}
          disabled={exporting !== null || syncing}
          className="flex items-center justify-center gap-2 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg disabled:opacity-50 active:bg-gray-300 transition-colors text-sm"
        >
          {exporting === 'AH' ? (
            <span className="inline-block w-4 h-4 border-2 border-gray-500 border-t-transparent rounded-full animate-spin" />
          ) : copied === 'AH' ? (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Gekopieerd
            </>
          ) : (
            <>Kopieer AH</>
          )}
        </button>

        <button
          onClick={() => handleExport('Jumbo')}
          disabled={exporting !== null || syncing}
          className="flex items-center justify-center gap-2 py-3 bg-yellow-100 text-yellow-800 font-medium rounded-lg disabled:opacity-50 active:bg-yellow-200 transition-colors text-sm"
        >
          {exporting === 'Jumbo' ? (
            <span className="inline-block w-4 h-4 border-2 border-yellow-600 border-t-transparent rounded-full animate-spin" />
          ) : copied === 'Jumbo' ? (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Gekopieerd
            </>
          ) : (
            <>Kopieer Jumbo</>
          )}
        </button>
      </div>
    </div>
  )
}
