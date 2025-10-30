# 🚀 Setup Completo: Project Helios no WSL

**Data:** 23 de outubro de 2025  
**Problema:** VS Code Insiders abriu no Windows e tentou usar venv Linux corrompida  
**Solução:** Recriar venv **dentro do WSL** e forçar sempre abrir no WSL

---

## ⚡ TL;DR (Rápido)

### Windows (PowerShell):
```powershell
# Remova venv corrompida
Remove-Item -Recurse -Force .venv

# Abra WSL
wsl
```

### No WSL:
```bash
cd /mnt/c/Users/fjuni/ysh-b2b/backend/data/project-helios
bash scripts/wsl-setup-venv.sh
```

### De volta ao Windows/VS Code:
```
code-insiders project-helios-wsl.code-workspace
```

Pronto! VS Code abrirá no WSL com tudo configurado.

---

## 📋 Passos Completos

### **Passo 1: Windows — Remover venv Corrompida**

Abra PowerShell no diretório do projeto:

```powershell
cd C:\Users\fjuni\ysh-b2b\backend\data\project-helios

# Remover venv Windows (corrompida/incompatível)
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue

# Confirmar que foi removida
Test-Path .venv  # Deve retornar False
```

---

### **Passo 2: WSL — Criar venv Correta**

Abra um terminal WSL (a partir do PowerShell ou de outro terminal WSL):

```bash
# Entrar no WSL
wsl

# Navegar para o projeto
cd /mnt/c/Users/fjuni/ysh-b2b/backend/data/project-helios

# Executar script de setup
bash scripts/wsl-setup-venv.sh
```

**O que esse script faz:**
- ✅ Verifica se estamos no WSL
- ✅ Cria nova venv em `~/.venvs/helios`
- ✅ Instala todas as dependências (`haas/requirements.txt`)
- ✅ Verifica se tudo está OK
- ✅ Retorna instruções para os próximos passos

**Tempo estimado:** ~3-5 minutos (depende de internet para download)

---

### **Passo 3: VS Code Insiders — Abrir Projeto no WSL**

Opção A (Recomendada): Abrir o workspace diretamente

```bash
# Ainda no WSL, ou em um novo terminal Windows:
code-insiders project-helios-wsl.code-workspace
```

Opção B: Via WSL remoto

```bash
# Em qualquer terminal:
code-insiders --remote wsl+Ubuntu project-helios-wsl.code-workspace
```

**O que esperado:**
- VS Code abrirá uma janela verde no canto inferior esquerdo: `WSL: Ubuntu`
- Terminal integrado usará automaticamente WSL bash
- Python será do `~/.venvs/helios`

---

### **Passo 4: VS Code — Selecionar Interpretador Python (Se Necessário)**

Se o Python não for detectado automaticamente:

1. **Abra a Paleta de Comandos:** `Ctrl+Shift+P`
2. **Digite:** `Python: Select Interpreter`
3. **Escolha:** `~/.venvs/helios/bin/python` (ou similar com "helios")

Se não aparecer na lista:
- Clique em "Enter interpreter path..."
- Digite: `/home/${USER}/.venvs/helios/bin/python`

---

### **Passo 5: Validar Setup**

Abra um terminal integrado no VS Code (`Ctrl+\`` ou Terminal → New Terminal) e rode:

```bash
# Verificar Python
python --version
# Saída esperada: Python 3.x.x

# Listar pacotes instalados
pip list | head -20
# Saída esperada: fastapi, sqlalchemy, pytest, etc.

# Rodar testes rápidos
cd haas && python -m pytest tests/ -v --tb=short -x
```

Se tudo funcionar, ✅ **Setup concluído com sucesso!**

---

## 🛠️ Troubleshooting

### "Terminal: Starting directory does not exist"

**Causa:** Workspace usa um `terminal.integrated.cwd` inválido.

**Solução:**
- Feche VS Code
- Abra novamente com: `code-insiders project-helios-wsl.code-workspace`
- Verifique que a janela mostra `WSL: Ubuntu` em baixo

---

### "ModuleNotFoundError: No module named 'helios_agents'"

**Causa:** Dependências não instaladas completamente.

**Solução:**
```bash
# No WSL, com venv ativa:
pip install -e /mnt/c/Users/fjuni/ysh-b2b/backend/data/project-helios/helios_agents

# Ou reinstale tudo:
pip install -r haas/requirements.txt
```

---

### "Redis connection failed"

**Causa:** Redis não está rodando (esperado em dev local).

**Solução:**
```bash
# Opção 1: Inicie Redis localmente (se tiver instalado)
redis-server

# Opção 2: Use docker-compose para toda a stack
cd haas && docker-compose up -d

# Opção 3: Rode testes sem Redis (mock)
cd haas && python -m pytest tests/ -v --disable-warnings
```

---

### "Python command not found" no terminal integrado

**Causa:** Venv não foi ativada ou está em outro shell.

**Solução:**
```bash
# Manualmente no terminal integrado:
source ~/.venvs/helios/bin/activate

# Ou no VS Code settings, já está configurado:
# "python.terminal.activateEnvironment": true
```

---

## 📚 Estrutura de Venv

Após o setup, sua venv estará em:

```
~/.venvs/helios/
├── bin/
│   ├── python         ← interpretador ativo
│   ├── pip            ← gerenciador de pacotes
│   ├── pytest         ← framework de testes
│   └── ... (outros executáveis)
├── lib/
│   └── python3.x/site-packages/  ← pacotes instalados
└── pyvenv.cfg
```

**Importante:** Esta venv está **NO WSL**, não no Windows.

---

## 🎯 Checklist Final

- [ ] Venv Windows `.venv` removida
- [ ] Venv WSL criada em `~/.venvs/helios`
- [ ] Dependências instaladas (`pip list` mostra pacotes)
- [ ] VS Code Insiders abriu com `WSL: Ubuntu` ativo
- [ ] Python interpreter selecionado (Ctrl+Shift+P → Python: Select Interpreter)
- [ ] Terminal integrado usa bash/WSL (não PowerShell)
- [ ] `python --version` funciona no terminal
- [ ] Testes rodam: `pytest tests/ -v`

---

## 💡 Dicas & Atalhos

### Abrir sempre no WSL com um atalho

**Windows:**
```batch
# Crie um arquivo .bat em um atalho da área de trabalho:
@echo off
cd C:\Users\fjuni\ysh-b2b\backend\data\project-helios
code-insiders project-helios-wsl.code-workspace
```

**WSL:**
```bash
# Adicione um alias no ~/.bashrc:
echo 'alias helios="code-insiders project-helios-wsl.code-workspace"' >> ~/.bashrc
source ~/.bashrc

# Depois, qualquer terminal WSL pode usar:
helios
```

### Performance no WSL

Se o VS Code ficar lento:

```json
// project-helios-wsl.code-workspace
{
  "settings": {
    "remote.WSL.fileWatcher.polling": true,
    "search.followSymlinks": false,
    "files.watcherExclude": {
      "**/.git": true,
      "**/node_modules": true,
      "**/__pycache__": true
    }
  }
}
```

---

## 📞 Referências

- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)
- [Developing in WSL](https://code.visualstudio.com/docs/remote/wsl)
- [Python Environments](https://code.visualstudio.com/docs/python/environments)
- [Terminal Basics](https://code.visualstudio.com/docs/terminal/basics)

---

**Status:** ✅ Ready to go!  
**Próximo passo:** Siga os passos acima e divirta-se desenvolvendo no WSL sem conflitos.
