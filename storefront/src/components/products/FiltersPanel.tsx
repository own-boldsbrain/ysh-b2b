"use client"

import { Product } from "@medusajs/medusa"

interface FiltersPanelProps {
  products: Product[];
  filters: {
    kwp: string;
    structure: string;
    distributionCenter: string;
  };
  onFilterChange: (filters: { kwp: string; structure: string; distributionCenter: string }) => void;
}

export default function FiltersPanel({ products, filters, onFilterChange }: FiltersPanelProps) {
  const structures = [...new Set(products.map(p => p.metadata?.estrutura as string).filter(Boolean))]
  const distributionCenters = [...new Set(products.map(p => p.metadata?.centro_distribuicao as string).filter(Boolean))]

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    onFilterChange({ ...filters, [e.target.name]: e.target.value });
  }

  return (
    <div className="p-4 border rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Filtros</h3>
      <div className="space-y-4">
        <div>
          <label htmlFor="kwp" className="block text-sm font-medium text-gray-700">
            kWp Mínimo
          </label>
          <input
            type="number"
            id="kwp"
            name="kwp"
            value={filters.kwp}
            onChange={handleInputChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>
        <div>
          <label htmlFor="structure" className="block text-sm font-medium text-gray-700">
            Estrutura
          </label>
          <select
            id="structure"
            name="structure"
            value={filters.structure}
            onChange={handleInputChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          >
            <option value="">Todos</option>
            {structures.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="distributionCenter" className="block text-sm font-medium text-gray-700">
            Centro de Distribuição
          </label>
          <select
            id="distributionCenter"
            name="distributionCenter"
            value={filters.distributionCenter}
            onChange={handleInputChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          >
            <option value="">Todos</option>
            {distributionCenters.map(dc => <option key={dc} value={dc}>{dc}</option>)}
          </select>
        </div>
      </div>
    </div>
  )
}
