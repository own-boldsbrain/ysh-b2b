# 🔑 Configuração de API Keys

## Como obter suas API keys:

### OpenAI (Codex/GPT-4o-mini)
1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a key (formato: `sk-...`)

**Custo**: ~$0.15 por 1.000 SKUs  
**Free tier**: $5 de crédito grátis (suficiente para ~33.000 SKUs)

### Google Gemini (1.5 Flash)
1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com conta Google
3. Clique em "Create API Key"
4. Copie a key (formato: `AIza...`)

**Custo**: ~$0.10 por 1.000 SKUs  
**Free tier**: 1.500 requests/dia grátis

---

## Como configurar:

### Opção 1: Variáveis de ambiente (Recomendado)

```powershell
# PowerShell
$env:OPENAI_API_KEY = "sk-SUA_KEY_AQUI"
$env:GEMINI_API_KEY = "AIza_SUA_KEY_AQUI"

# Verificar
echo $env:OPENAI_API_KEY
echo $env:GEMINI_API_KEY
```

### Opção 2: Passar diretamente no comando

```powershell
python enrich_specs_with_llm.py --api openai --key "sk-SUA_KEY_AQUI"
python enrich_specs_with_llm.py --api gemini --key "AIza_SUA_KEY_AQUI"
```

---

## Teste inicial (recomendado):

```powershell
# Testar com 5 SKUs primeiro
python enrich_specs_with_llm.py --api openai --key "sk-..." --limit 5

# Se funcionou, processar todos os SKUs sem specs
python enrich_specs_with_llm.py --api openai --key "sk-..." --skip-existing
```

---

## ⚠️ Segurança

**NUNCA**:
- ❌ Commitar API keys no Git
- ❌ Compartilhar keys em chat público
- ❌ Salvar keys em arquivos sem .gitignore

**SEMPRE**:
- ✅ Usar variáveis de ambiente
- ✅ Adicionar `.env` ao `.gitignore`
- ✅ Revogar keys comprometidas imediatamente

---

**Status**: Aguardando suas API keys para testar o enriquecimento LLM 🚀
