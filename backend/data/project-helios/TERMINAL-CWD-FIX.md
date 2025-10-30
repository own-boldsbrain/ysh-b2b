# ✅ Terminal CWD Error - FIXED

## O Problema

```
Process failed to start: Starting directory (cwd) "/home/${USER}/project-helios" does not exist.
```

## Causa Root

A configuração do workspace tinha paths hardcoded com variáveis não-interpoladas:

```json
"terminal.integrated.cwd": "/home/${USER}/project-helios"
```

**Por que isso falha:**
- ❌ `${USER}` não é variável de ambiente - é apenas um string literal
- ❌ O caminho `/home/${USER}/...` não existe (estar em `/mnt/c/Users/...` no WSL)
- ❌ VS Code não expande `${USER}` neste contexto de configuração

**Referência:** [VS Code Terminal Launch Troubleshooting](https://code.visualstudio.com/docs/supporting/troubleshoot-terminal-launch)

## A Solução

✅ **Corrigido para usar variáveis VS Code nativas:**
```json
"terminal.integrated.cwd": "${workspaceFolder}"
```

**Por quê funciona:**
- ✅ `${workspaceFolder}` é variável **nativa do VS Code**, sempre resolvida
- ✅ Cross-platform: Windows, Linux, macOS, WSL
- ✅ Sem dependência de variáveis de ambiente
- ✅ Aponta sempre para raiz do workspace

## Variáveis VS Code Disponíveis

Para terminal, use sempre variáveis nativas (não ambiente):

| Variável | Valor | Exemplo |
|----------|-------|---------|
| `${workspaceFolder}` | Raiz do workspace | `/mnt/c/Users/.../project-helios` |
| `${workspaceRootFolderName}` | Nome da pasta | `project-helios` |
| `${file}` | Arquivo aberto | `/mnt/c/.../file.py` |
| `${fileDirname}` | Pasta do arquivo | `/mnt/c/.../haas` |
| `${homedir}` | Home directory | `/home/usuario` |

**❌ NÃO use:** `${USER}`, `${HOME}`, `${PATH}` (variáveis de ambiente)

Referência: [VS Code Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference)

## Mudanças Aplicadas

### Arquivo: `project-helios-wsl.code-workspace`

**Antes (❌ Não funciona):**
```jsonc
"terminal.integrated.cwd": "/home/${USER}/project-helios",
"python.defaultInterpreterPath": "/home/${USER}/.venvs/helios/bin/python",
```

**Depois (✅ Funciona):**
```jsonc
"terminal.integrated.cwd": "${workspaceFolder}",
"python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
```

## Verificação Rápida (30 segundos)

### Passo 1: Feche e reabra VS Code
```bash
code-insiders project-helios-wsl.code-workspace
```

### Passo 2: Abra novo terminal
- `Ctrl+\`` (backtick) ou
- **Terminal > New Terminal**

Se abrir **sem erros** de CWD ✅, a fix funcionou!

### Passo 3: Confirme paths (opcional)
```bash
pwd  # Deve ser /mnt/c/Users/fjuni/ysh-b2b/backend/data/project-helios

python --version
python -c "import sys; print(sys.executable)"
```

Saída esperada:
```bash
$ pwd
/mnt/c/Users/fjuni/ysh-b2b/backend/data/project-helios

$ python --version
Python 3.12.x

$ python -c "import sys; print(sys.executable)"
/mnt/c/Users/fjuni/ysh-b2b/backend/data/project-helios/.venv/bin/python
```

## Troubleshooting Avançado

Se ainda tiver problema **após reabrir VS Code**:

### 1. Verifique se realmente reabriu WSL
No **status bar** (canto inferior esquerdo), deve aparecer:
```
WSL: Ubuntu
```

Se não aparecer, clique e reconecte.

### 2. Limpe configurações do WSL
```powershell
# Windows PowerShell - Remove cached WSL connection
Remove-Item -Recurse -Force "$HOME\.vscode-server" -ErrorAction SilentlyContinue

# Depois reabra:
code-insiders project-helios-wsl.code-workspace
```

### 3. Verifique permissões de terminal
```bash
# WSL - Check shell availability
which bash
ls -la /bin/bash
# Deve retornar algo como: /bin/bash
```

### 4. Recrie venv (se Python não funciona)
```bash
cd "${workspaceFolder}"  # Vai para raiz do projeto
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r haas/requirements.txt
```

### 5. Ativar logs de debug
Para diagnosticar mais, abra as configurações do terminal:
```json
"terminal.integrated.logLevel": "debug",
"remote.WSL.logLevel": "debug"
```

Depois verifique **Output** panel (Bottom panel) → **Terminal** ou **Remote-WSL** tabs.

## Comandos Úteis para Diagnóstico

```bash
# Ver todas as variáveis de workspace
code-insiders --status

# Ver versão do WSL
wsl --list --verbose  # (Windows PowerShell)

# Testar conexão WSL
wsl echo "WSL working"

# Verificar venv
ls -la .venv/bin/python
python -m venv --help
```

## 📚 Referência Oficial

Baseado na documentação oficial do VS Code:

1. **[Troubleshoot Terminal Launch](https://code.visualstudio.com/docs/supporting/troubleshoot-terminal-launch)**
   - Problemas comuns e soluções
   - Logging e debugging
   - Platform-specific issues

2. **[Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference)**
   - Todas as variáveis VS Code disponíveis
   - Quando usar cada uma

3. **[Remote WSL Documentation](https://code.visualstudio.com/docs/remote/wsl)**
   - Setup WSL no VS Code
   - Terminal configuration
   - Troubleshooting WSL específico

4. **[Remote Containers Advanced](https://code.visualstudio.com/remote/advancedcontainers/configuration)**
   - Configurações avançadas
   - Multi-container setups

## ✅ Checklist de Verificação

- [ ] Status bar mostra `WSL: Ubuntu`
- [ ] Terminal novo abre sem erros
- [ ] `pwd` retorna `/mnt/c/Users/.../project-helios`
- [ ] `python --version` funciona
- [ ] `python -c "import sys; print(sys.executable)"` mostra `.venv/bin/python`
- [ ] `cd haas && python -m pytest --version` funciona

---

**Status:** ✅ Corrigido & Documentado
**Data:** Outubro 23, 2025
**Baseado em:** [VS Code Official Troubleshooting](https://code.visualstudio.com/docs/supporting/troubleshoot-terminal-launch)
**Arquivo Afetado:** `project-helios-wsl.code-workspace`
