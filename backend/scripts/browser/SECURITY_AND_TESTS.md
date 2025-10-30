# Segurança e Plano de Testes - Integração Browser → DynamoDB

Este documento complementa o `README.md` com recomendações práticas de segurança e um plano de testes para validar a integração direta do browser com DynamoDB.

## Recomendações de Segurança

- Use um **Cognito Identity Pool** com roles com permissões estritas. Preferir roles de **usuários autenticados**.
- Política de IAM mínima (exemplo): permitir apenas `dynamodb:GetItem`, `dynamodb:Query`, `dynamodb:Scan`, `dynamodb:PutItem` na tabela específica.
- Considere restringir writes: permitir `PutItem` apenas em uma condição (por exemplo um atributo `source` igual a `webapp`), usando condition expressions e AttributeValue checks.
- Habilite CloudTrail para auditar quem fez alterações e CloudWatch Alarms para taxa de erros anormais.
- Em aplicações públicas, prefira backend validates e assina pedidos no servidor. Use integração direta apenas para casos com usuários autenticados e cenário controlado.

## Boas práticas de política IAM (exemplo)

```json
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Action":["dynamodb:GetItem","dynamodb:Query","dynamodb:Scan"],
      "Resource":"arn:aws:dynamodb:us-east-1:773235999227:table/ysh-products-catalog"
    },
    {
      "Effect":"Allow",
      "Action":["dynamodb:PutItem"],
      "Resource":"arn:aws:dynamodb:us-east-1:773235999227:table/ysh-products-catalog",
      "Condition":{
        "StringEquals":{
          "dynamodb:LeadingKeys":"webapp#*"
        }
      }
    }
  ]
}
```

> Observação: `dynamodb:LeadingKeys` requer que a tabela tenha chave primária adequada. Ajuste conforme seu schema.

## Plano de Testes

1. Teste unitário local (estático): servir `demo.html` via `npx http-server` e validar importação.
2. Validar fluxo de autenticação Cognito: obter IdentityPoolId e confirmar que a role assumida é a esperada (CloudWatch logs)
3. Testar permissões read-only: inicializar cliente e executar `getSKU` e `scanSKUs`
4. Testar write controlado: criar um SKU de teste com `putSKU` e validar política aplicada (atributos condicionais)
5. Teste de carga básico: simular múltiplos `scanSKUs` e medir latência; identificar limites de throughput provisionado
6. Teste de falhas: revogar permissão e validar mensagens de erro amigáveis no frontend

## Observações sobre CORS e Headers

- O SDK V3 assina as requisições; não há configurações adicionais de CORS no DynamoDB. Contudo, requests iniciadas do browser podem ser bloqueadas por browsers se houver problemas com certificados ou proxies. Teste em ambientes reais.
