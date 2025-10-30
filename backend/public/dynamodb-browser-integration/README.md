# DynamoDB Browser Integration (Leitura direta)

Este diretório contém um demo leve para ler dados do DynamoDB diretamente do navegador usando um Cognito Identity Pool (sem server-side API). Use apenas para dashboards internas e debugging. Não exponha permissões de escrita.

## Arquivos
- `index.html` — página demo com inputs para região, IdentityPoolId e tabela.
- `app.js` — lógica do browser usando AWS SDK v3 via CDN (jsdelivr). Faz `Scan` e `Get` e valida SKUs localmente.

## Requisitos (AWS)
1. Criar um Cognito Identity Pool (federated identities) e habilitar identidades não autenticadas ou autenticadas conforme seu fluxo.
2. Criar uma role IAM com política restringida ao mínimo — leitura somente na tabela DynamoDB:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Scan",
        "dynamodb:GetItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/ysh-products-catalog"
    }
  ]
}
```

3. Associate role to unauthenticated/authenticated identities in the Identity Pool settings.

## Como usar (local)
1. Abrir `public/dynamodb-browser-integration/index.html` no browser (recomendo usar um servidor local como `npx http-server` ou `python -m http.server 8080`).

2. Preencher:
   - Região AWS (ex: `us-east-1`)
   - Cognito Identity Pool ID (ex: `us-east-1:xxxx-xxxx-xxxx`)
   - DynamoDB Table (ex: `ysh-products-catalog`)

3. Clique em `Scan` para carregar (até 100 itens) e validar se existem campos obrigatórios.

## Segurança
- Nunca forneça permissões de escrita. Use políticas de apenas leitura.
- Para produção, prefira uma API intermediária com autorização e rate-limiting.

## Observações
- Para ambientes com CORS, certifique-se de que o endpoint DynamoDB pode ser acessado (Cognito + SDK v3 padrão leva em conta CORS). Este demo assume permissões corretas e role vinculada ao identity pool.
- Se preferir, use AWS Amplify para simplificar a configuração do Identity Pool.

---

Se quiser, eu configuro os arquivos da role/policy e um passo a passo detalhado para criar o Identity Pool (screenshots e CLI commands).