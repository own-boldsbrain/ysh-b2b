import { medusaClient } from "@/lib/medusa-client"
import { Product } from "@medusajs/medusa"
import ProductCard from "@/components/products/Card"
import FiltersPanel from "@/components/products/FiltersPanel"
import { getSalesChannel } from "@/lib/data/sales-channels"
import ProductList from "@/components/products/ProductList"

async function getProducts(countryCode: string) {
  const salesChannel = await getSalesChannel()
  const salesChannelId = salesChannel?.id

  const { products } = await medusaClient.get<{ products: Product[] }>("/store/products", {
    query: {
      region_id: countryCode, // Assuming region_id maps to countryCode for simplicity
      sales_channel_id: salesChannelId
    }
  })
  return products
}

export default async function KitsHibridosPage({ params }: { params: { countryCode: string } }) {
  const products = await getProducts(params.countryCode)

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Kits Híbridos</h1>
      <ProductList products={products} countryCode={params.countryCode} />
    </div>
  )
}
