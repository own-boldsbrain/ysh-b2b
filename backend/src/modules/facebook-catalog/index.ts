import { Module } from "@medusajs/framework/utils";
import FacebookCatalogService from "./service";

export default Module("facebook-catalog", {
    service: FacebookCatalogService,
});
