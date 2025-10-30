# 🔧 Terminal CWD Error - FIX APPLIED

**Data:** October 23, 2025
**Status:** ✅ **CORRIGIDO E DOCUMENTADO**
**Baseado em:** [VS Code Official Troubleshooting](https://code.visualstudio.com/docs/supporting/troubleshoot-terminal-launch)

---

## 📍 O Que Mudou

Seu workspace foi atualizado para **corrigir o erro de terminal**:

```
Starting directory (cwd) "/home/${USER}/project-helios" does not exist.
```

### ✅ Solução Aplicada

**Arquivo:** `project-helios-wsl.code-workspace`

Problema: Usando variável não-VS-Code `${USER}` em configuração de terminal

```diff
- "terminal.integrated.cwd": "/home/${USER}/project-helios",
- "python.defaultInterpreterPath": "/home/${USER}/.venvs/helios/bin/python",

+ "terminal.integrated.cwd": "${workspaceFolder}",
+ "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
```

**Por que funciona agora:**
- ✅ `${workspaceFolder}` é variável **nativa do VS Code**, sempre resolvida
- ✅ Cross-platform: Windows, Linux, macOS, WSL
- ✅ Sem dependência de variáveis de ambiente do shell

---

## 🚀 Quick Verification (30 Segundos)

### 1️⃣ Feche e Reabra VS Code

```bash
code-insiders project-helios-wsl.code-workspace
```

### 2️⃣ Abra Terminal Novo

- Pressione `Ctrl+\`` (backtick/crase)
- OU: **Terminal > New Terminal**

### 3️⃣ Verifique Status Bar

No canto inferior esquerdo, deve aparecer:
```
WSL: Ubuntu
```

Se aparecer esse badge ✅, você está conectado ao WSL corretamente.

### 4️⃣ Terminal Abre Sem Erros?

Se o terminal abriu **SEM** mensagem de erro `Starting directory does not exist` ✅

**Pronto! Fix funcionou! 🎉**

---

## 📋 Verificação Detalhada (Opcional)

Se quiser confirmar tudo:

```bash
$ pwd
/mnt/c/Users/fjuni/ysh-b2b/backend/data/project-helios
✓ Deve mostrar este path

$ python --version
Python 3.12.x
✓ Python deve estar disponível

$ python -c "import sys; print(sys.executable)"
/mnt/c/Users/fjuni/ysh-b2b/backend/data/project-helios/.venv/bin/python
✓ Python deve estar na venv

$ cd haas && python -m pytest --version
pytest 7.x.x
✓ Pytest deve estar instalado
```

---

## � Se Ainda Houver Problemas

### Opção 1: Verifique Status Bar

Se **não aparecer** `WSL: Ubuntu` no status bar:
1. Clique nele
2. Selecione `Remote-WSL: Reopen in WSL`
3. Aguarde reconexão (~5 segundos)
4. Status bar deve mudar para `WSL: Ubuntu`

### Opção 2: Limpe Cache VS Code (Nuclear Option)

Se ainda não funcionar:

**Windows PowerShell:**
```powershell
# Remove all cached WSL connections
Remove-Item -Recurse -Force "$HOME\.vscode-server" -ErrorAction SilentlyContinue

# Reabra
code-insiders project-helios-wsl.code-workspace
```

⚠️ Isso vai **re-instalar extensões no WSL**, demora ~30 seg.

### Opção 3: Verificar Permissões Shell

```bash
# WSL Terminal - Check bash exists and is executable
ls -la /bin/bash
which bash
# Deve retornar /bin/bash e ter permissão -rwxr-xr-x
```

### Opção 4: Ativar Logs de Debug

Se nada funcionar, ativa logs:

Em `project-helios-wsl.code-workspace`, add:
```json
"terminal.integrated.logLevel": "debug",
"remote.WSL.logLevel": "debug"
```

Depois abre **Output** panel (bottom):
- Tab: `Terminal` ou `Remote-WSL`
- Procura por mensagens de erro

---

## 📚 Documentação Relacionada

| Documento | Descrição |
|-----------|-----------|
| [`TERMINAL-CWD-FIX.md`](./TERMINAL-CWD-FIX.md) | 📖 Explicação completa + troubleshooting avançado |
| [`VSCODE-WORKSPACE-SETUP.md`](./VSCODE-WORKSPACE-SETUP.md) | 📋 Setup completo do VS Code |
| [`VSCODE-QUICK-REFERENCE.md`](./VSCODE-QUICK-REFERENCE.md) | ⚡ Quick lookup de tudo |
| [VS Code Variables](https://code.visualstudio.com/docs/editor/variables-reference) | 🔗 Todas as variáveis VS Code |
| [Terminal Troubleshooting](https://code.visualstudio.com/docs/supporting/troubleshoot-terminal-launch) | 🔗 Official VS Code guide |

---

## ✅ Checklist Rápido

- [ ] `code-insiders project-helios-wsl.code-workspace` aberto
- [ ] Status bar mostra `WSL: Ubuntu` (canto inferior esquerdo)
- [ ] Terminal novo (`Ctrl+\``) abre **sem erros**
- [ ] `pwd` mostra `/mnt/c/Users/.../project-helios`
- [ ] `python --version` retorna versão
- [ ] Pode rodar `cd haas && python -m pytest`

✅ **Se todos os itens passarem, o fix funcionou!**

---

## ℹ️ Mais Informações

### Por que isso aconteceu?

A configuração original tinha:
```json
"terminal.integrated.cwd": "/home/${USER}/project-helios"
```

Problema: VS Code **não expande `${USER}`** em contextos de terminal. É apenas um string literal "/home/${USER}/..." que não existe.

### Por que a solução funciona?

```json
"terminal.integrated.cwd": "${workspaceFolder}"
```

**Porque:**
- `${workspaceFolder}` é **variável VS Code** reconhecida e expandida corretamente
- VS Code sempre resolve isso para o caminho absoluto do workspace
- Funciona em qualquer OS e plataforma

### Regra Geral

```
❌ NÃO FAÇA:
"terminal.integrated.cwd": "/home/${USER}/project"
"python.path": "$HOME/venv/bin/python"

✅ FAÇA:
"terminal.integrated.cwd": "${workspaceFolder}"
"python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
```

---

**Status:** ✅ **Pronto para uso**
**Impacto:** Terminal abre normalmente, sem erros
**Próximo:** Abra VS Code e comece com GitHub Copilot! 🤖

Para troubleshooting avançado, veja [`TERMINAL-CWD-FIX.md`](./TERMINAL-CWD-FIX.md).
