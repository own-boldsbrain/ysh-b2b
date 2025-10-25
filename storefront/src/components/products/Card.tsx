import { Product } from "@medusajs/medusa"
import Link from "next/link"
import { formatAmount } from "@/lib/util/prices"

interface ProductCardProps {
  product: Product;
  countryCode: string;
}

export default function ProductCard({ product, countryCode }: ProductCardProps) {
  const price = product.variants?.[0]?.prices?.[0]
  const amount = price?.amount
  const currencyCode = price?.currency_code

  return (
    <Link href={`/${countryCode}/kits-hibridos/${product.id}`} passHref>
      <div className="border rounded-lg p-4 cursor-pointer h-full flex flex-col">
        <div className="flex-grow">
          <h2 className="text-lg font-semibold mb-2">{product.title}</h2>
          <div className="text-sm text-gray-600 space-y-1">
            <p>⚡ {product.metadata?.kwp || "N/A"} kWp</p>
            <p>🏗 {product.metadata?.estrutura || "N/A"}</p>
            <p>📦 {product.metadata?.centro_distribuicao || "N/A"}</p>
          </div>
        </div>
        <div className="mt-4">
          <p className="text-lg font-bold">
            {amount && currencyCode ? formatAmount({ amount, currencyCode, locale: countryCode }) : "N/A"}
          </p>
        </div>
      </div>
    </Link>
  )
}
