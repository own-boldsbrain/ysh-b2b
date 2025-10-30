# Domain: Catalog

Camadas:
- domain: entidades, value objects, regras
- application: casos de uso (ex.: ImportProducts, SearchSkus)
- infrastructure: repositórios/adapters (DB, cache, storage)
- interfaces: DTOs, mapeadores, validadores

Pontos de integração: módulos Medusa `@medusajs/product`, `inventory`, `pricing` e `src/modules/unified-catalog`.

