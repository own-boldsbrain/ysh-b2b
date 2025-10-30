---
id: quick-start-full-stack
title: Quick Start da Stack Completa
sidebar_label: Stack Completa
sidebar_position: 2
description: Guia rápido para iniciar toda a stack OSS do YSH B2B com Docker e preparar deploy em nuvem
---

## Stack completa

### Serviços incluídos

- PostgreSQL 15 (porta 5432)
- Redis 7 (porta 6379)
- Medusa Backend (portas 9000-9002)
- Next.js Storefront (porta 8000)
- Nginx Reverse Proxy (porta 80)
- Adminer (porta 8080)
- Redis Commander (porta 8081)

### Equivalentes no AWS Free Tier

- RDS db.t4g.micro (750 h/mês)
- ElastiCache cache.t4g.micro (750 h/mês)
- S3 Standard (5 GB + 20k GET + 2k PUT)
- Application Load Balancer (750 h/mês + 15 GB)
- ECS Fargate Spot

## Pré-requisitos

- Docker 24+ com Compose
- 8 GB RAM (16 GB recomendado)
- 20 GB livres em disco

## Passo a passo

### 1. Clonar e configurar `.env`

```powershell
Copy-Item .env.example .env
notepad .env
```

### 2. Gerar secrets de produção

```powershell
$JWT_SECRET = -join ((33..126) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$COOKIE_SECRET = -join ((33..126) | Get-Random -Count 32 | ForEach-Object {[char]$_})

Add-Content .env "JWT_SECRET=$JWT_SECRET"
Add-Content .env "COOKIE_SECRET=$COOKIE_SECRET"
```

Anote os valores para uso em deploy.

### 3. Subir a stack

```powershell
docker-compose -f docker-compose.full-stack.yml up -d
docker-compose -f docker-compose.full-stack.yml logs -f
docker-compose -f docker-compose.full-stack.yml ps
```

### 4. Monitorar health checks

```powershell
docker-compose -f docker-compose.full-stack.yml ps
```

Aguarde estados `healthy` para backend, storefront, PostgreSQL e Redis (~60 segundos).

### 5. Migrações, seed e usuário admin

```powershell
docker-compose -f docker-compose.full-stack.yml exec backend yarn medusa db:migrate
docker-compose -f docker-compose.full-stack.yml exec backend yarn run seed
docker-compose -f docker-compose.full-stack.yml exec backend yarn medusa user -e admin@yellosolar.com -p supersecret123 -i admin
```

### 6. Obter publishable key

```powershell
docker-compose -f docker-compose.full-stack.yml exec postgres psql -U yshuser -d yshdb -c "SELECT id FROM publishable_api_key LIMIT 1;"
```

Ou via Adminer em [http://localhost:8080](http://localhost:8080). Atualize `NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY` no `.env` da storefront.

## URLs e credenciais

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Storefront | [http://localhost:8000](http://localhost:8000) | N/A |
| Backend API | [http://localhost:9000](http://localhost:9000) | N/A |
| Admin Dashboard | [http://localhost:9000/app](http://localhost:9000/app) | `admin@yellosolar.com` / `supersecret123` |
| Adminer | [http://localhost:8080](http://localhost:8080) | postgres / yshuser / yshpass |
| Redis Commander | [http://localhost:8081](http://localhost:8081) | `admin` / `admin` |

## Operações comuns

### Gerenciamento de serviços

```powershell
docker-compose -f docker-compose.full-stack.yml stop
docker-compose -f docker-compose.full-stack.yml start
docker-compose -f docker-compose.full-stack.yml restart backend
docker-compose -f docker-compose.full-stack.yml down
docker-compose -f docker-compose.full-stack.yml down -v
```

### Logs e debugging

```powershell
docker-compose -f docker-compose.full-stack.yml logs -f
docker-compose -f docker-compose.full-stack.yml logs -f backend
docker-compose -f docker-compose.full-stack.yml logs --tail=100 backend
docker-compose -f docker-compose.full-stack.yml exec backend sh
docker-compose -f docker-compose.full-stack.yml exec storefront sh
```

### Banco de dados

```powershell
docker-compose -f docker-compose.full-stack.yml exec postgres psql -U yshuser -d yshdb
docker-compose -f docker-compose.full-stack.yml exec postgres pg_dump -U yshuser yshdb > backup.sql
Get-Content backup.sql | docker-compose -f docker-compose.full-stack.yml exec -T postgres psql -U yshuser -d yshdb
docker-compose -f docker-compose.full-stack.yml exec postgres psql -U yshuser -d yshdb -c "\\dt"
```

### Redis métricas

```powershell
docker-compose -f docker-compose.full-stack.yml exec redis redis-cli
docker-compose -f docker-compose.full-stack.yml exec redis redis-cli KEYS "*"
docker-compose -f docker-compose.full-stack.yml exec redis redis-cli FLUSHALL
```

### Build e atualização

```powershell
docker-compose -f docker-compose.full-stack.yml up -d --build backend
docker-compose -f docker-compose.full-stack.yml up -d --build
docker-compose -f docker-compose.full-stack.yml pull
```

## Monitoramento

### Health checks

```powershell
curl http://localhost:9000/health
curl http://localhost:8000/
curl http://localhost/health
```

### Uso de recursos

```powershell
docker stats
docker system df
docker system prune -a
```

## Deploy para AWS (resumo)

1. Instale e configure AWS CLI (`aws configure`).
2. Valide e crie stack CloudFormation com `aws/cloudformation-free-tier.yml`.
3. Faça build/tag/push das imagens para ECR.
4. Atualize tarefas ECS com as novas imagens.

## Checklist de segurança

- [ ] Atualizar secrets e senhas
- [ ] Configurar HTTPS e firewall
- [ ] Habilitar backups automáticos do PostgreSQL
- [ ] Ativar monitoramento/alertas (CloudWatch)
- [ ] Revisar CORS e rate limiting
- [ ] Configurar WAF se necessário

## Otimizações

### PostgreSQL

```sql
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

VACUUM ANALYZE;
```

### Redis

```bash
redis-cli INFO stats
redis-cli INFO memory
```

### Next.js

```powershell
cd storefront
yarn build
yarn start
```

## Troubleshooting

### Backend não inicia

```powershell
docker-compose -f docker-compose.full-stack.yml logs backend
docker-compose -f docker-compose.full-stack.yml exec backend yarn medusa db:migrate
docker-compose -f docker-compose.full-stack.yml down
docker volume rm ysh-postgres-data
docker-compose -f docker-compose.full-stack.yml up -d
```

### Storefront com erro 500

```powershell
docker-compose -f docker-compose.full-stack.yml exec storefront env | Select-String NEXT_PUBLIC
docker-compose -f docker-compose.full-stack.yml exec postgres psql -U yshuser -d yshdb -c "SELECT * FROM publishable_api_key;"
docker-compose -f docker-compose.full-stack.yml up -d --build storefront
```

### Porta em uso

```powershell
Get-NetTCPConnection -LocalPort 8000
Stop-Process -Id <PID> -Force
```

## Recursos adicionais

- [Medusa.js Docs](https://docs.medusajs.com)
- [Next.js Docs](https://nextjs.org/docs)
- [AWS Free Tier](https://aws.amazon.com/free)
- [Docker Docs](https://docs.docker.com)

## Suporte

1. Verifique os logs com `docker-compose logs -f`.
2. Consulte a documentação acima.
3. Abra uma issue no repositório caso necessário.
