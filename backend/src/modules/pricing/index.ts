import { Module } from "@medusajs/framework/utils";
import PricingModuleService from "./service";

export const PRICING_MODULE = "pricing";

export default Module(PRICING_MODULE, {
  service: PricingModuleService,
});
