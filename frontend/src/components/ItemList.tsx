import type { GroupedItems } from '../types'
import ItemRow from './ItemRow'

interface ItemListProps {
  groups: GroupedItems[]
}

export default function ItemList({ groups }: ItemListProps) {
  return (
    <div className="space-y-4">
      {groups.map((group) => (
        <div key={group.category?.id ?? 'uncategorized'}>
          {/* Category header */}
          <div className="flex items-center gap-2 py-2 text-gray-700 font-medium">
            <span className="text-lg">{group.category?.icon ?? '📦'}</span>
            <span>{group.category?.name_nl ?? 'Zonder categorie'}</span>
            <span className="text-gray-400 text-sm">({group.items.length})</span>
          </div>

          {/* Items */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-100 divide-y divide-gray-100">
            {group.items.map((item) => (
              <ItemRow key={item.id} item={item} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
