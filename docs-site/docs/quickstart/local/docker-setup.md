---
id: docker-setup
title: Setup Local com Docker Desktop
sidebar_label: Docker Desktop
sidebar_position: 1
description: Guia completo para configurar Docker Desktop e preparar o ambiente local do YSH B2B
---

## Pré-requisitos

- Windows 10/11 (64-bit) Pro, Enterprise ou Education
- WSL 2 habilitado
- Virtualização ativa na BIOS
- 4 GB RAM (8 GB+ recomendado)
- 20 GB livres em disco

## Passo 1 · Instalar Docker Desktop

### Download

Acesse o site oficial [Docker Desktop](https://www.docker.com/products/docker-desktop/) ou execute:

```powershell
Start-Process "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
```

### Instalação

1. Execute `Docker Desktop Installer.exe`.
2. Mantenha as opções padrão (WSL 2 e atalho na área de trabalho).
3. Clique em **Install** e aguarde 5-10 minutos.
4. Reinicie o computador se solicitado.

### Primeira execução

1. Abra Docker Desktop.
2. Aceite os termos de serviço.
3. Faça login ou pule (opcional).
4. Aguarde o ícone verde na bandeja de sistema.

## Passo 2 · Validar instalação

Execute no PowerShell:

```powershell
# Versão do Docker
docker --version

# Versão do Compose
docker-compose --version

# Teste rápido
docker run hello-world
```

Saídas esperadas:

- `Docker version 24.x` ou superior
- `Docker Compose version v2.x` ou superior
- Mensagem "Hello from Docker!" no teste

## Passo 3 · Habilitar Yarn 4 (Corepack)

```powershell
corepack enable
yarn --version
```

A versão retornada deve ser `4.4.1` ou superior.

## Passo 4 · Preparar arquivos .env

### Backend

```powershell
cd backend
Copy-Item .env.template .env
```

Edite `backend/.env` (valores padrão funcionam):

```bash
DATABASE_URL=postgresql://yshuser:yshpass@postgres:5432/yshdb
REDIS_URL=redis://redis:6379
JWT_SECRET=dev-jwt-secret-change-in-production-min-32-chars
COOKIE_SECRET=dev-cookie-secret-change-in-production-min-32-chars
STORE_CORS=http://localhost:8000,http://localhost:80
ADMIN_CORS=http://localhost:9000,http://localhost:7001,http://localhost:80
```

### Storefront

```powershell
cd ..\storefront
Copy-Item .env.template .env
```

Edite `storefront/.env`:

```bash
NEXT_PUBLIC_MEDUSA_BACKEND_URL=http://localhost:9000
NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY=pk_01JYKZBQN77AG2MRGBC4NPPQGR
NEXT_PUBLIC_BASE_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_REGION=br
```

:::info Publishable Key
A chave será gerada após rodar migrações/seed e criar usuário admin (ver Passo 6).
:::

### Opcional (raiz)

```powershell
cd ..
Copy-Item .env.example .env
```

## Passo 5 · Subir a stack

### Build e start

```powershell
docker-compose -f docker-compose.full-stack.yml up --build
```

Serviços iniciados: PostgreSQL, Redis, Backend, Storefront, Adminer, Redis Commander e Nginx.

### Monitorar inicialização

Aguarde mensagens como:

```text
ysh-backend     | Server is ready on port: 9000
ysh-storefront  | Ready started server on 0.0.0.0:8000
ysh-postgres    | database system is ready to accept connections
```

Mantenha o terminal aberto. Para sair, use `Ctrl+C`.

## Passo 6 · Migrações, seed e usuário admin

Abra um novo PowerShell:

```powershell
cd C:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b

docker-compose -f docker-compose.full-stack.yml exec backend yarn medusa db:migrate
docker-compose -f docker-compose.full-stack.yml exec backend yarn run seed
docker-compose -f docker-compose.full-stack.yml exec backend yarn medusa user -e admin@ysh.com -p Admin123! -i admin_ysh
```

## Passo 7 · Configurar Publishable Key

1. Acesse [http://localhost:9000/app](http://localhost:9000/app).
2. Login: `admin@ysh.com` / `Admin123!`.
3. Vá em **Settings → Publishable API Keys** e copie a chave (pk_...).
4. Atualize `storefront/.env` com a chave.
5. Reinicie a stack (`docker-compose up`).

## Passo 8 · URLs principais

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Storefront | [http://localhost:8000](http://localhost:8000) | N/A |
| Backend API | [http://localhost:9000](http://localhost:9000) | N/A |
| Medusa Admin | [http://localhost:9000/app](http://localhost:9000/app) | `admin@ysh.com` / `Admin123!` |
| Adminer | [http://localhost:8080](http://localhost:8080) | Server: postgres · User: yshuser · Pass: yshpass · DB: yshdb |
| Redis Commander | [http://localhost:8081](http://localhost:8081) | `admin` / `admin` |
| Nginx Proxy | [http://localhost:80](http://localhost:80) | N/A |

## Comandos úteis

### Containers

```powershell
docker-compose -f docker-compose.full-stack.yml ps
docker-compose -f docker-compose.full-stack.yml logs backend -f
docker-compose -f docker-compose.full-stack.yml down
docker-compose -f docker-compose.full-stack.yml down -v
docker-compose -f docker-compose.full-stack.yml up --build backend
```

### Acesso ao shell dos containers

```powershell
docker-compose -f docker-compose.full-stack.yml exec backend sh
docker-compose -f docker-compose.full-stack.yml exec postgres psql -U yshuser -d yshdb
```

### Desenvolvimento

```powershell
docker-compose -f docker-compose.full-stack.yml exec backend yarn medusa --help
docker-compose -f docker-compose.full-stack.yml exec backend yarn medusa db:generate CompanyModule
docker-compose -f docker-compose.full-stack.yml exec backend yarn test:unit
docker-compose -f docker-compose.full-stack.yml exec backend yarn test:integration:http
```

## Troubleshooting

### Porta em uso

```powershell
netstat -ano | findstr :9000
taskkill /PID <PID> /F
```

### Docker daemon não inicializa

Verifique se Docker Desktop está em execução:

```powershell
Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
```

### Containers encerram após start

```powershell
docker-compose -f docker-compose.full-stack.yml logs backend
docker-compose -f docker-compose.full-stack.yml logs postgres
Test-Path backend\.env
Test-Path storefront\.env
```

### Backend esperando PostgreSQL

Certifique-se de que o healthcheck está saudável:

```powershell
docker-compose -f docker-compose.full-stack.yml ps postgres
```

### Hot reload

A stack já usa polling (`CHOKIDAR_USEPOLLING=true`). Se necessário, edite arquivos diretamente no container `/app`.

## Monitoramento de recursos

```powershell
docker stats
docker image prune -a
docker volume prune
docker system prune -a --volumes
```

## Checklist final

- [ ] Docker Desktop instalado e ativo
- [ ] `docker --version` e `docker-compose --version` executam sem erro
- [ ] `yarn --version` retorna 4.4.1+
- [ ] `.env` criados em `backend/` e `storefront/`
- [ ] Stack executando com `docker-compose up`
- [ ] Migrações e seed concluídos
- [ ] Usuário admin criado
- [ ] Publishable key configurada
- [ ] Storefront acessível em [http://localhost:8000](http://localhost:8000)
- [ ] Medusa Admin acessível em [http://localhost:9000/app](http://localhost:9000/app)

## Recursos adicionais

- [Documentação Medusa](https://docs.medusajs.com)
- [Documentação Docker Desktop](https://docs.docker.com/desktop/windows/)
- [Guia WSL 2](https://learn.microsoft.com/pt-br/windows/wsl/install)
- [Troubleshooting Docker](https://docs.docker.com/desktop/troubleshoot/overview/)
