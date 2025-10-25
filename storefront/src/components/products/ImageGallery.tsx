"use client"

import { Product } from "@medusajs/medusa"
import { useState } from "react"

interface ImageGalleryProps {
  product: Product
}

export default function ImageGallery({ product }: ImageGalleryProps) {
  const [selectedImage, setSelectedImage] = useState(product.thumbnail || "")

  return (
    <div>
      <div className="mb-4">
        <img src={selectedImage} alt={product.title || ""} className="w-full h-auto rounded-lg" />
      </div>
      <div className="flex space-x-2">
        {product.images?.map(img => (
          <img
            key={img.id}
            src={img.url}
            alt={product.title || ""}
            onClick={() => setSelectedImage(img.url)}
            className={`w-16 h-16 rounded-md cursor-pointer border ${selectedImage === img.url ? "border-blue-500" : ""}`}
          />
        ))}
      </div>
    </div>
  )
}
