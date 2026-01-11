import { useState } from 'react'
import { useItems, useCategories, groupItemsByCategory } from './hooks/useItems'
import AddItemForm from './components/AddItemForm'
import ItemList from './components/ItemList'
import ExportButtons from './components/ExportButtons'

function App() {
  const [showChecked, setShowChecked] = useState(false)
  const { data: items, isLoading, error, refetch } = useItems()
  const { data: categories } = useCategories()

  const openItems = items?.filter((item) => item.status === 'open') ?? []
  const checkedItems = items?.filter((item) => item.status === 'checked') ?? []

  const groupedOpenItems = groupItemsByCategory(openItems, categories ?? [])
  const groupedCheckedItems = groupItemsByCategory(checkedItems, categories ?? [])

  const handleRefresh = async () => {
    await refetch()
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-safe-bottom">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-primary-600 text-white shadow-lg pt-safe-top">
        <div className="px-4 py-4">
          <h1 className="text-xl font-bold">Boodschappenlijst</h1>
          <p className="text-primary-100 text-sm">
            {openItems.length} {openItems.length === 1 ? 'item' : 'items'} open
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="px-4 py-4 space-y-6">
        {/* Add item form */}
        <AddItemForm />

        {/* Error state */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            Er ging iets mis: {error.message}
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        )}

        {/* Open items */}
        {!isLoading && groupedOpenItems.length > 0 && (
          <section>
            <ItemList groups={groupedOpenItems} />
          </section>
        )}

        {/* Empty state */}
        {!isLoading && openItems.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg">Geen boodschappen</p>
            <p className="text-sm mt-1">Voeg items toe met het formulier hierboven</p>
          </div>
        )}

        {/* Checked items toggle */}
        {checkedItems.length > 0 && (
          <section>
            <button
              onClick={() => setShowChecked(!showChecked)}
              className="flex items-center justify-between w-full py-3 text-left text-gray-600"
            >
              <span className="font-medium">
                Afgevinkt ({checkedItems.length})
              </span>
              <svg
                className={`w-5 h-5 transition-transform ${showChecked ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showChecked && (
              <div className="opacity-60">
                <ItemList groups={groupedCheckedItems} />
              </div>
            )}
          </section>
        )}

        {/* Export buttons */}
        {openItems.length > 0 && <ExportButtons />}

        {/* Refresh button */}
        <button
          onClick={handleRefresh}
          className="w-full py-3 text-primary-600 font-medium"
        >
          Vernieuwen
        </button>
      </main>
    </div>
  )
}

export default App
