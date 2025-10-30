# Catalog DDD Pilot - GET /store/catalog/skus

Objetivo: migrar a rota de listagem de SKUs para a nova arquitetura DDD + CQRS como prova de conceito.

Como habilitar:

1. Defina a variável de ambiente no ambiente local ou no container:

```powershell
$env:CATALOG_DDD_ENABLED = 'true'
```

2. Reinicie o servidor Medusa/Backend.

Como testar:

1. Request HTTP:

```bash
curl 'http://localhost:9000/store/catalog/skus?page=1&limit=20&search=solar'
```

2. Logs: verifique logs para `ListSKUsHandler` e cache hits

Observações:

- A implementação usa `ProductRepository.listSKUs(...)` como adaptação para leitura.
- O cache TTL padrão é 1 hora. Invalidação deve ocorrer via eventos `catalog.product.updated`.

Próximos passos:

- Implementar/confirmar `ProductRepository` em `domains/catalog/infrastructure/repositories`.
- Adicionar testes unitários para `ListSKUsHandler` (cache hit/miss).
- Medir e otimizar latência P95 (<150ms).
