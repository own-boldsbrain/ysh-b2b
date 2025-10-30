# Integração direta DynamoDB (Browser)

Este diretório contém um exemplo de integração direta do browser com a tabela DynamoDB `ysh-products-catalog` usando o AWS SDK v3 e um Cognito Identity Pool para obter credenciais temporárias.

Arquivos:

- `dynamodb-browser-integration.mjs` - Módulo ES que cria um cliente DocumentClient para uso no browser.
- `demo.html` - Exemplo mínimo que demonstra como inicializar o cliente e consultar um SKU.

Pré-requisitos AWS (resumo):

1. Criar um Cognito Identity Pool (Federated Identities) e anotar o `IdentityPoolId` (ex: `us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx`).
2. Configurar as roles (unauthenticated/authenticated) com permissões mínimas. Para teste rápido, a role pode permitir `dynamodb:GetItem`, `dynamodb:Scan`, `dynamodb:PutItem` apenas na tabela `ysh-products-catalog`.

Exemplo de policy mínima (ajuste às melhores práticas):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem","dynamodb:Scan","dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:773235999227:table/ysh-products-catalog"
    }
  ]
}
```

Segurança e CORS:

- O browser precisa obter credenciais assinadas (Cognito) para assinar as requisições SigV4.
- Limite as permissões ao mínimo necessário e, de preferência, exija autenticação (usuários autenticados via Cognito User Pool or social providers).
- Não exponha uma identidade pool com permissões de escrita ao público sem revisões de segurança.

Como testar localmente:

1. Servir a pasta com um server estático (ex: `npx serve` ou `npx http-server`) e abrir `demo.html`.
2. No demo, informe o `IdentityPoolId` e inicialize o cliente.
3. Teste `Get SKU` com um `sku` existente.

Notas:

- Para produção é recomendável usar um backend que exponha apenas operações necessárias e/ou um proxy que aplique validações e limites de taxa. A integração direta do browser é adequada para aplicações SPA com usuários autenticados via Cognito.
