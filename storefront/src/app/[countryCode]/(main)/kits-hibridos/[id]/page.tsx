import { medusaClient } from "@/lib/medusa-client"
import { Product } from "@medusajs/medusa"
import { notFound } from "next/navigation"
import ImageGallery from "@/components/products/ImageGallery"
import ProductDetails from "@/components/products/ProductDetails"
import { getSalesChannel } from "@/lib/data/sales-channels"

async function getProduct(id: string) {
  const salesChannel = await getSalesChannel()
  const salesChannelId = salesChannel?.id

  const { product } = await medusaClient.get<{ product: Product }>(`/store/products/${id}`, {
    query: {
      sales_channel_id: salesChannelId
    }
  })
  return product
}

export default async function KitHibridoPage({ params }: { params: { id: string, countryCode: string } }) {
  const product = await getProduct(params.id)

  if (!product) {
    notFound()
  }

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <ImageGallery product={product} />
        </div>
        <div>
          <ProductDetails product={product} countryCode={params.countryCode} />
        </div>
      </div>
    </div>
  )
}
