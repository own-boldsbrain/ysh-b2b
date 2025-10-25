import { medusaClient } from "@/lib/medusa-client";
import { cookies } from "next/headers";

export async function getSalesChannel() {
  const salesChannelId = cookies().get("sales_channel_id")?.value;

  if (!salesChannelId) {
    return null;
  }

  try {
    const { sales_channel } = await medusaClient.get(`/store/sales-channels/${salesChannelId}`);
    return sales_channel;
  } catch (error) {
    console.error("Failed to fetch sales channel", error);
    return null;
  }
}
