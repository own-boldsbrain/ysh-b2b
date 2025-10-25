"use client"

import { Product } from "@medusajs/medusa"
import { useCart } from "medusa-react"
import { formatAmount } from "@/lib/util/prices"

interface ProductDetailsProps {
  product: Product;
  countryCode: string;
}

export default function ProductDetails({ product, countryCode }: ProductDetailsProps) {
  const { cart, createCart, updateCart } = useCart()

  const handleAddToCart = async () => {
    if (!cart?.id) {
      await createCart.mutateAsync({
        region_id: countryCode, // Assuming region_id maps to countryCode
        items: [{ variant_id: product.variants[0].id, quantity: 1 }],
      })
    } else {
      await updateCart.mutateAsync({
        cartId: cart.id,
        updates: { items: [{ variant_id: product.variants[0].id, quantity: 1 }] },
      })
    }
  }

  const price = product.variants?.[0]?.prices?.[0]

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">{product.title}</h1>
      <div className="text-lg text-gray-600 space-y-2 mb-4">
        <p>⚡ {product.metadata?.kwp || "N/A"} kWp</p>
        <p>🏗 {product.metadata?.estrutura || "N/A"}</p>
        <p>📦 {product.metadata?.centro_distribuicao || "N/A"}</p>
      </div>
      <div className="flex space-x-4 items-center">
        <div>
          <p className="text-2xl font-bold">
            {price ? formatAmount({ amount: price.amount, currency_code: price.currency_code, locale: countryCode }) : "N/A"}
          </p>
        </div>
        <button className="bg-blue-500 text-white px-6 py-2 rounded-lg">
          Solicitar Cotação (B2B)
        </button>
        <button
          onClick={handleAddToCart}
          className="bg-green-500 text-white px-6 py-2 rounded-lg"
        >
          Adicionar ao Carrinho
        </button>
      </div>
    </div>
  )
}
