GOOGLE_CLIENT_ID

GOOGLE_CLIENT_SECRET

NEXTAUTH_SECRET

Don't show again


![[paypal-300x115 1.png]]

```
6b3d6261894ff22d2641285deb3fdba76bb93160c947454c61eff065051c7487
```

#### Connect Together AI Account
product@boldsbrain.ai
Rookie@010100DashboardPlaygrounds

```
6b3d6261894ff22d2641285deb3fdba76bb93160c947454c61eff065051c7487
```
#### Integrate #Together.ai

---
#HYPERTUNE

```
NEXT_PUBLIC_HYPERTUNE_TOKEN="U2FsdGVkX1/WzNja1tpWbvrVC1jk1KAIkChnfg3w2b0="
EXPERIMENTATION_CONFIG_ITEM_KEY="hypertune_4856"
```

---

```tsx
import { Identify } from "flags";
import { dedupe, flag } from "flags/next";
import { createHypertuneAdapter } from "@flags-sdk/hypertune";
import {
  createSource,
  flagFallbacks,
  vercelFlagDefinitions as flagDefinitions,
  Context,
  RootFlagValues,
} from "./generated/hypertune";

const identify: Identify<Context> = dedupe(
  async ({ headers, cookies }) => {
    return {
      environment: process.env.NODE_ENV,
      user: { id: "1", name: "Test User", email: "hi@test.com" },
    };
  },
);

const hypertuneAdapter = createHypertuneAdapter<
  RootFlagValues,
  Context
>({
  createSource,
  flagFallbacks,
  flagDefinitions,
  identify,
});

export const exampleFlagFlag = flag(
  hypertuneAdapter.declarations.exampleFlag,
);

export const enableDesignV2Flag = flag(
  hypertuneAdapter.declarations.enableDesignV2,
);
```

```tsx
import "server-only";
import { VercelEdgeConfigInitDataProvider } from "hypertune";
import { createClient } from "@vercel/edge-config";
import { unstable_noStore as noStore } from "next/cache";
import { createSource } from "@/generated/hypertune";

const hypertuneSource = createSource({
  token: process.env.NEXT_PUBLIC_HYPERTUNE_TOKEN!,
  initDataProvider:
    process.env.EXPERIMENTATION_CONFIG &&
    process.env.EXPERIMENTATION_CONFIG_ITEM_KEY
      ? new VercelEdgeConfigInitDataProvider({
          edgeConfigClient: createClient(
            process.env.EXPERIMENTATION_CONFIG,
          ),
          itemKey: process.env.EXPERIMENTATION_CONFIG_ITEM_KEY,
        })
      : undefined,
});

export default async function getHypertune() {
  noStore();
  await hypertuneSource.initIfNeeded(); // Check for flag updates

  return hypertuneSource.root({
    args: {
      context: {
        environment: process.env.NODE_ENV,
        // Pass current user details here
        user: { id: "1", name: "Test", email: "test@example.com" },
      },
    },
  });
}
```

##### #GITHUB #API

```
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

```

---
#senha
```
Rookie@010100@boldsbrain.ai
```
#celular #telefone #phone
```
(21) 9792-09021
```

#senha

```
product@boldsbrain.ai
```


```
Rookie@010100
```


https://www.bv.com.br/solar-simulador/solar/dados-cliente

---
#### #API #GOOGLE 

```
AIzaSyBpskcVRxTopuDgsNXEzLdpXGPTjyFDlu0
```

---


```
{"web":{"client_id":"803690968562-g5gfjr31nf3b73iaahcvsvnejatavehg.apps.googleusercontent.com","project_id":"horizontal-data-408900","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["https://script.google.com"],"javascript_origins":["https://script.google.com"]}}
```

---
##### #OPENAI

```
export OPENAI_API_KEY=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
```

```
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
```

---
##### #ASAAS

#Token

```
$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjM4Y2MzMWRlLTM5YTEtNGM0Ni04NmNlLTc3N2U3M2Q2OTAzMDo6JGFhY2hfZjI3OWViODctZGIzOS00N2RiLTkxOTMtZDIwOGU2ODNkZGRl
```

#Nome
```
yello-v1
```
#Data de #expiração (opcional)
DD/MM/AAAA
#Hora de #expiração (opcional)
HH:MM
#Data de #criação
22/05/2025
#Criado por
fjunior_sant@hotmail.com

```
$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjM4Y2MzMWRlLTM5YTEtNGM0Ni04NmNlLTc3N2U3M2Q2OTAzMDo6JGFhY2hfZjI3OWViODctZGIzOS00N2RiLTkxOTMtZDIwOGU2ODNkZGRl

```

----
#### #CIELO

---
##### 🧾 #Identificação da #Aplicação

```plaintext
Nome: Yello-Solar-Hub
Descrição: A Yello Solar Hub tem como missão acelerar a transição para uma matriz energética sustentável, promovendo a energia solar como uma solução acessível.
```

---
##### 🔐 #Credenciais de #Autenticação

###### Client ID
```plaintext
8kDWkAE7nNk59ElIqyGi7r075eeHYYIH6tRY4RsCDAnel1YzDs

```
##### #Client #Secret

```
LETC9qwApfdOqUBGEIxwlEdgSuuk7xK0P3uejmCSwaZgH7rkGd
```

---
#### 🌐 #Endpoints da #API

##### API #Realm #URL: 
```plaintext
https://api.cielo.com.br

```
##### API #Sandbox #URL
```
https://api2.cielo.com.br
```

---
#### 🆔 #Identificadores e #Status

```plaintext
Merchant ID: a8cc1b3f-3407-4d0e-94b6-d18a7de36ac3
Access Token: 1f0615bd-55c1-4672-8dc4-5f13c883b7fe
Status: Aprovada
```

---
### 🧾 #Token de #Acesso e #Proprietário

```plaintext
Código de Acesso: Sfjx5tIkyCB9SUHqHlzKdU1Yrn2LtDS5uYGrcMeZa4jqvVOZfz
Proprietário: product@boldsbrain.ai
```

---

> [!NOTE]
> ### ⚠️ Recomendações de Segurança
> 
> - **Armazenamento Seguro**: Mantenha o `Client Secret` e o `Access Token` em locais seguros e nunca os exponha em repositórios públicos ou arquivos de configuração versionados.
>     
> - **Rotação de Credenciais**: Implemente um processo de rotação periódica das credenciais para minimizar riscos em caso de comprometimento.
>     
> - **Uso de Variáveis de Ambiente**: Utilize variáveis de ambiente para gerenciar as credenciais em ambientes de desenvolvimento, teste e produção.([Cielo Docs](https://docs.cielo.com.br/link-en/reference/get-credentials?utm_source=chatgpt.com "Get your credentials - Cielo E-commerce"))
>     
> - **Monitoramento de Acessos**: Implemente logs e monitoramento para detectar acessos não autorizados ou atividades suspeitas.
>     
> 
> ---
> 
> Se precisar de assistência adicional para integrar essas credenciais ao seu sistema ou configurar o fluxo de autenticação OAuth2 com a Cielo, estou à disposição para ajudar.

---
#### #MAPTILER_API_KEY

```
MLY|9665531083543688|9aa661cf26bfde2341efbb3f6fa1269d
```
#### #XAI_API_KEY

```
xai-wHMVs4KrKor6Tfa79XUgHOP9SzD6BWLjAob6V4pKc1T2Zbu5hg52notEGWyrbBMPUUebbVwRcgbW4gGS
```
#### #GROQ_API_KEY

```
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
```
#### #POSTGRES_PASSWORD

```
npg_DLrZhV7G5KOo
```
#### #POSTGRES_DATABASE

```
neondb
```
#### #PGPASSWORD

```
npg_DLrZhV7G5KOo
```
#### #PGDATABASE

```
neondb
```
#### #PGHOST_UNPOOLED

```
ep-dawn-star-a5fuox1k.us-east-2.aws.neon.tech
```
#### #PGUSER

```
neondb_owner
```
#### #POSTGRES_URL_NO_SSL

```
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech/neondb
```
#### #POSTGRES_HOST

```
ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech
```
#### #POSTGRES_URL

```
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
```
#### #POSTGRES_PRISMA_URL

```
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech/neondb?connect_timeout=15&sslmode=require
```
#### #DATABASE_URL_UNPOOLED

```
postgresql://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k.us-east-2.aws.neon.tech/neondb?sslmode=require
```
#### #POSTGRES_URL_NON_POOLING

```
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k.us-east-2.aws.neon.tech/neondb?sslmode=require
```
#### #PGHOST

```
ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech
```
#### #POSTGRES_USER

```
neondb_owner
```
#### #DATABASE_URL

```
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
```
#### #KV_URL

```
rediss://default:AURhAAIjcDEzODI3YmFjNjUwYWU0MDJmOTk3NDY5NTMxNDQ4NzVmNnAxMA@sincere-falcon-17505.upstash.io:6379
```
#### #KV_REST_API_READ_ONLY_TOKEN

```
AkRhAAIgcDHM3uzY1Jd270AyriY6ADYG0iT490qEXzFP3D5PzjURrw
```
#### #KV_REST_API_TOKEN

```
AURhAAIjcDEzODI3YmFjNjUwYWU0MDJmOTk3NDY5NTMxNDQ4NzVmNnAxMA
```
#### #KV_REST_API_URL

```
https://sincere-falcon-17505.upstash.io
```
#### #NEXT_PUBLIC_API_URL

```
https://yelloenergia
```
#### #SENTINEL_HUB_INSTANCE_ID

```
5b1edcad-abac-46ee-b92e-e9f6d451c891
```
#### #BLOB_READ_WRITE_TOKEN

```
vercel_blob_rw_GdQNXeQ3aHmoOrai_74fmOcZtiRwE2KDwHez3z8jCn6D7zE
```
#### #REPLICATE_API_TOKEN

```
r8_6X5JlQVS5hLuDkJfoj2TezlSfGGr0ha07Xsli
```

#### #NEXT_PUBLIC_MAPTILER_API_KEY
hc3VejoNv6LWcrNs6wNi
#### #VLLM_API_BASE
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
#### #VLLM_API_KEY
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
#### #SENTINEL_HUB_CLIENT_SECRET
ZSMkwcQuoMnUfBzv9qUCNnV4t5B6I0l8
#### #SENTINEL_HUB_CLIENT_ID
5b1edcad-abac-46ee-b92e-e9f6d451c891
#### #sentinelsecret
ZSMkwcQuoMnUfBzv9qUCNnV4t5B6l0l8
#### #sentinelid
5b1edcad-abac-46ee-b92e-e9f6d451c891

---

#### #XAI_API_KEY

```
xai-wHMVs4KrKor6Tfa79XUgHOP9SzD6BWLjAob6V4pKc1T2Zbu5hg52notEGWyrbBMPUUebbVwRcgbW4gGS
```

#### #KV_URL

```
rediss://default:AURhAAIjcDEzODI3YmFjNjUwYWU0MDJmOTk3NDY5NTMxNDQ4NzVmNnAxMA@sincere-falcon-17505.upstash.io:6379
```

#### #KV_REST_API_READ_ONLY_TOKEN

```
AkRhAAIgcDHM3uzY1Jd270AyriY6ADYG0iT490qEXzFP3D5PzjURrw
```
#### #KV_REST_API_TOKEN

```
AURhAAIjcDEzODI3YmFjNjUwYWU0MDJmOTk3NDY5NTMxNDQ4NzVmNnAxMA
```

#### #KV_REST_API_URL

```
https://sincere-falcon-17505.upstash.io
```

#### #POSTGRES_URL
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
#POSTGRES_PRISMA_URL
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech/neondb?connect_timeout=15&sslmode=require
#DATABASE_URL_UNPOOLED
postgresql://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k.us-east-2.aws.neon.tech/neondb?sslmode=require
#POSTGRES_URL_NON_POOLING
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k.us-east-2.aws.neon.tech/neondb?sslmode=require
#PGHOST
ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech
#POSTGRES_USER
neondb_owner
#DATABASE_URL
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
POSTGRES_PASSWORD
npg_DLrZhV7G5KOo
#POSTGRES_DATABASE
neondb
#PGPASSWORD
npg_DLrZhV7G5KOo
#PGDATABASE
neondb
#PGHOST_UNPOOLED
ep-dawn-star-a5fuox1k.us-east-2.aws.neon.tech
#PGUSER
#neondb_owner
POSTGRES_URL_NO_SSL
postgres://neondb_owner:npg_DLrZhV7G5KOo@ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech/neondb
#POSTGRES_HOST
ep-dawn-star-a5fuox1k-pooler.us-east-2.aws.neon.tech

-------

#BLOB_READ_WRITE_TOKEN
vercel_blob_rw_i7HJ422cmHKlsS58_dzXWCRcAeIXLWVEiXOke2MFaVK0Tty
#GROQ_API_KEY
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
#PGHOST_UNPOOLED
ep-cold-queen-ac27m8p4.sa-east-1.aws.neon.tech
PGUSER••••••••••••••••••
POSTGRES_URL_NO_SSL••••••••••••••••••
POSTGRES_HOST
ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech
POSTGRES_URL
postgres://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require


POSTGRES_PRISMA_URL
postgres://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech/neondb?connect_timeout=15&sslmode=require
DATABASE_URL_UNPOOLED
postgresql://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4.sa-east-1.aws.neon.tech/neondb?sslmode=require
POSTGRES_URL_NON_POOLING
postgres://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4.sa-east-1.aws.neon.tech/neondb?sslmode=require
PGHOST
ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech
POSTGRES_USER
neondb_owner
DATABASE_URL
postgres://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require
POSTGRES_PASSWORD
npg_I5rVeNcRtA3w
POSTGRES_DATABASE
neondb
PGPASSWORD
npg_I5rVeNcRtA3w
PGDATABASE
neondb

---





## Project Settings

[View Project](https://v0.dev/chat/projects/aGOzkLV6nHP)

Overview

Integrations

Environment Variables

Knowledge

Community

Add

BLOB_READ_WRITE_TOKEN`vercel_blob_rw_i7HJ422cmHKlsS58_dzXWCRcAeIXLWVEiXOke2MFaVK0Tty`

More options

XAI_API_KEY`xai-NIRUOgHY2fXuxldpPqRGxaLltwnB4ixWCJa3gtUC2DL5nKjCwgwklzM1s5HbnoUeswnGve7NquXTWiD2`

More options

KV_URL`rediss://default:AWGjAAIjcDE5ZDEwNzA1MDgxYTM0ZGVmOGUwMzU4MzBiMDE5ZGJjYXAxMA@feasible-louse-24995.upstash.io:6379`

More options

KV_REST_API_READ_ONLY_TOKEN`AmGjAAIgcDFKMSdqmXgvYHB3P6zbHUAN_IzOFk-VjgVtr49hT_VeAw`

More options

REDIS_URL`rediss://default:AWGjAAIjcDE5ZDEwNzA1MDgxYTM0ZGVmOGUwMzU4MzBiMDE5ZGJjYXAxMA@feasible-louse-24995.upstash.io:6379`

More options

KV_REST_API_TOKEN`AWGjAAIjcDE5ZDEwNzA1MDgxYTM0ZGVmOGUwMzU4MzBiMDE5ZGJjYXAxMA`

More options

KV_REST_API_URL`https://feasible-louse-24995.upstash.io`

More options

LAUNCHDARKLY_API_KEY`hc3VejoNv6LWcrNs6wNi`

More options

LAUNCHDARKLY_WEBHOOK_SECRET`https://yelloenergia`

More options

NEXT_PUBLIC_SOCKET_URL`https://yelloenergia`

More options

POSTGRES_URL`postgres://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require`

More options

POSTGRES_PRISMA_URL`postgres://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech/neondb?connect_timeout=15&sslmode=require`

More options

DATABASE_URL_UNPOOLED`postgresql://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4.sa-east-1.aws.neon.tech/neondb?sslmode=require`

More options

POSTGRES_URL_NON_POOLING`postgres://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4.sa-east-1.aws.neon.tech/neondb?sslmode=require`

More options

PGHOST`ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech`

More options

POSTGRES_USER`neondb_owner`

More options

DATABASE_URL`postgres://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require`

More options

POSTGRES_PASSWORD`npg_I5rVeNcRtA3w`

More options

POSTGRES_DATABASE`neondb`

More options

PGPASSWORD`npg_I5rVeNcRtA3w`

More options

PGDATABASE`neondb`

More options

PGHOST_UNPOOLED`ep-cold-queen-ac27m8p4.sa-east-1.aws.neon.tech`

More options

PGUSER`neondb_owner`

More options

POSTGRES_URL_NO_SSL`postgres://neondb_owner:npg_I5rVeNcRtA3w@ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech/neondb`

More options

POSTGRES_HOST`ep-cold-queen-ac27m8p4-pooler.sa-east-1.aws.neon.tech`

##### GROQ_API_KEY
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

---

#### 

Team Name

This is your team's visible name within Vercel. For example, the name of your company or department.

Please use 32 characters at maximum.

Save

#### 

Team URL

This is your team’s URL namespace on Vercel. Within it, your team can inspect their projects, check out any recent activity, or configure settings to their liking.

vercel.com/

Please use 48 characters at maximum.

Save

![Yello Solar Hub](https://vercel.com/api/www/avatar/fb799e5a9a133383169ed27e7ef3a40814de6b72?s=160 "Yello Solar Hub")

#### 

Team Avatar

This is your team's avatar.  
Click on the avatar to upload a custom one from your files.

An avatar is optional but strongly recommended.

#### 

Preview Deployment Suffix

By default, the URL of every new Preview Deployment ends with `.vercel.app`. This setting allows you to choose your own custom domain in place of this suffix.

my-deployment.

The provided domain name "yello-solar-hub" is invalid

Save

#### 

Team ID

This is your team's ID within Vercel.

team_JxqyDX1D60bwkxlgvCzxhQNS

Used when interacting with the Vercel API.

#### 

[Vercel Toolbar](https://vercel.com/yello-solarhub/~/settings#vercel-toolbar)

Enable the Vercel Toolbar on your Deployments.

Pre-Production Deployments

Default (on)OnOff

Production Deployments

Default (on)OnOff

To use the toolbar in production your team members need the [Chrome extension](https://chromewebstore.google.com/detail/vercel/lahhiofdgnbcgmemekkmjnpifojdaelb) or to enable the toolbar for that domain in the toolbar menu. Learn more about using the [toolbar in production](https://vercel.com/docs/vercel-toolbar/in-production-and-localhost/add-to-production).

Allow this setting to be overridden on the project level.

Enabled

Learn more about the [Vercel Toolbar](https://vercel.com/docs/workflow-collaboration/vercel-toolbar)

Save

#### 

Transfer

Transfer your projects to another team without downtime or workflow interruptions.

Learn more about [Transferring Projects](https://vercel.com/docs/projects/overview#transferring-a-project)