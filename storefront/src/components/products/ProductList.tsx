"use client"

import { useState, useMemo } from "react"
import { Product } from "@medusajs/medusa"
import ProductCard from "@/components/products/Card"
import FiltersPanel from "@/components/products/FiltersPanel"

interface ProductListProps {
  products: Product[];
  countryCode: string;
}

export default function ProductList({ products, countryCode }: ProductListProps) {
  const [filters, setFilters] = useState({
    kwp: "",
    structure: "",
    distributionCenter: "",
  })

  const filteredProducts = useMemo(() => {
    return products.filter(p => {
      const kwp = p.metadata?.kwp as number ?? 0
      const structure = p.metadata?.estrutura as string ?? ""
      const distributionCenter = p.metadata?.centro_distribuicao as string ?? ""

      if (filters.kwp && kwp < parseFloat(filters.kwp)) return false
      if (filters.structure && structure !== filters.structure) return false
      if (filters.distributionCenter && distributionCenter !== filters.distributionCenter) return false

      return true
    })
  }, [products, filters])

  return (
    <div className="grid grid-cols-12 gap-4">
      <div className="col-span-3">
        <FiltersPanel products={products} filters={filters} onFilterChange={setFilters} />
      </div>
      <div className="col-span-9 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredProducts.map((product) => (
          <ProductCard key={product.id} product={product} countryCode={countryCode} />
        ))}
      </div>
    </div>
  )
}
