import { Module } from "@medusajs/framework/utils";
import ScraperModuleService from "./service";

export const SCRAPER_MODULE = "scraper";

export default Module(SCRAPER_MODULE, {
  service: ScraperModuleService,
});
