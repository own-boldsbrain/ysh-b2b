# 📚 VS Code Configuration Best Practices

**Baseado em:** [VS Code Official Documentation](https://code.visualstudio.com/docs)
**Data:** October 23, 2025

---

## 🎯 Regra de Ouro

### ✅ USE (VS Code Native Variables)
```json
{
  "terminal.integrated.cwd": "${workspaceFolder}",
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "editor.defaultFormatter": "${workspaceFolder}/scripts/formatter.py"
}
```

### ❌ DON'T (Environment Variables in Config)
```json
{
  "terminal.integrated.cwd": "${HOME}/projects/my-project",
  "python.defaultInterpreterPath": "$VIRTUAL_ENV/bin/python",
  "files.exclude": "${GLOB_PATTERN}/node_modules"
}
```

**Por quê?**
- VS Code **não expande** `$VAR`, `${VAR}`, `$(VAR)` em configurações
- Apenas variáveis **VS Code nativas** (com `${}`) são resolvidas
- Hardcode de environment variables causa erros em diferentes máquinas/sistemas

---

## 📋 Variáveis VS Code Mais Usadas

### Workspace & Files
| Variável | Valor | Uso |
|----------|-------|-----|
| `${workspaceFolder}` | `/home/user/project` | Raiz do projeto |
| `${workspaceRootFolderName}` | `project` | Nome da pasta raiz |
| `${file}` | `/home/user/project/file.py` | Arquivo aberto |
| `${fileDirname}` | `/home/user/project/src` | Pasta do arquivo aberto |
| `${fileBasename}` | `file.py` | Nome do arquivo aberto |
| `${fileBasenameNoExtension}` | `file` | Arquivo sem extensão |
| `${fileExtname}` | `.py` | Extensão do arquivo |
| `${relativeFile}` | `src/file.py` | Caminho relativo do arquivo |
| `${relativeFileDirname}` | `src` | Pasta relativa do arquivo |

### User & Machine
| Variável | Valor | Uso |
|----------|-------|-----|
| `${userHome}` | `/home/user` | Home directory do OS |
| `${homedir}` | `/home/user` | Alternativa a `${userHome}` |
| `${pathSeparator}` | `/` (Linux) ou `\` (Windows) | Separador de path |

### Environment (Leitura apenas)
| Variável | Valor | Uso |
|----------|-------|-----|
| `${env:VAR_NAME}` | `value` | **Para ler** env vars |

Referência completa: https://code.visualstudio.com/docs/editor/variables-reference

---

## ✅ Melhores Práticas por Contexto

### 1. Terminal Configuration

✅ **BOM:**
```json
{
  "terminal.integrated.cwd": "${workspaceFolder}",
  "terminal.integrated.profiles.linux": {
    "bash": {
      "path": "/bin/bash",
      "icon": "terminal"
    }
  }
}
```

❌ **RUIM:**
```json
{
  "terminal.integrated.cwd": "/home/${USER}/projects/helios",
  "terminal.integrated.defaultProfile": "${SHELL}"
}
```

**Por quê?**
- `${workspaceFolder}` sempre resolve corretamente
- `${USER}` não é expandido, vira string literal
- `${SHELL}` é environment var, não VS Code var

### 2. Python Path Configuration

✅ **BOM:**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest",
  "python.linting.pylintPath": "${workspaceFolder}/.venv/bin/pylint",
  "python.formatting.blackPath": "${workspaceFolder}/.venv/bin/black"
}
```

❌ **RUIM:**
```json
{
  "python.defaultInterpreterPath": "$VIRTUAL_ENV/bin/python",
  "python.linting.pylintPath": "$HOME/.venv/bin/pylint"
}
```

### 3. Debugger Configuration (launch.json)

✅ **BOM:**
```json
{
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app"],
      "cwd": "${workspaceFolder}/haas",
      "console": "integratedTerminal"
    }
  ]
}
```

❌ **RUIM:**
```json
{
  "configurations": [
    {
      "cwd": "${PROJECT_ROOT}/haas",
      "pythonPath": "${VIRTUAL_ENV}/bin/python"
    }
  ]
}
```

---

## 🔧 Configurando para Múltiplas Plataformas

### Remote WSL (Windows + Linux)

✅ **workspace.code-workspace:**
```json
{
  "remoteAuthority": "wsl+Ubuntu",
  "settings": {
    "terminal.integrated.cwd": "${workspaceFolder}",
    "terminal.integrated.profiles.windows": {
      "WSL": {
        "path": "wsl.exe",
        "args": ["-d", "Ubuntu"]
      }
    },
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
  }
}
```

**Key Points:**
- Use `${workspaceFolder}`, não paths hardcoded
- VS Code resolve corretamente em WSL context
- Paths em WSL são `/mnt/c/...`, não `/home/...` para mounted drives

### Remote SSH

✅ **Same pattern:**
```json
{
  "remoteAuthority": "ssh-remote+server",
  "settings": {
    "terminal.integrated.cwd": "${workspaceFolder}",
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
  }
}
```

---

## 🆘 Troubleshooting: "Starting directory does not exist"

### Root Cause
Usando environment variables em `terminal.integrated.cwd`:

```json
❌ "terminal.integrated.cwd": "/home/${USER}/project"
❌ "terminal.integrated.cwd": "$HOME/project"
❌ "terminal.integrated.cwd": "${HOME}/project"
```

### Fix
Use VS Code variable:

```json
✅ "terminal.integrated.cwd": "${workspaceFolder}"
```

### Debugging Steps
1. Check `remote.WSL.logLevel`: `debug`
2. Open **Output** panel → `Remote-WSL` tab
3. Look for "Starting directory" errors
4. Verify path exists: `ls -la "${workspaceFolder}"`

---

## 📖 Reference: All VS Code Variables

### Predefined Variables (Always Available)

```json
{
  "workspaceFolder": "/full/path/to/workspace",
  "workspaceRootFolderName": "workspace-name",
  "file": "/full/path/to/file.ext",
  "fileBasename": "file.ext",
  "fileBasenameNoExtension": "file",
  "fileDirname": "/full/path/to",
  "fileExtname": ".ext",
  "relativeFile": "path/to/file.ext",
  "relativeFileDirname": "path/to",
  "pathSeparator": "/",
  "userHome": "/home/user",
  "homedir": "/home/user"
}
```

### Environment Variables (Read-only)

```json
{
  "env:VAR_NAME": "value",
  "env:PATH": "/usr/bin:/usr/local/bin:...",
  "env:HOME": "/home/user",
  "env:USER": "username"
}
```

### Example Usage
```json
{
  "settings": {
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.linting.pylintPath": "${workspaceFolder}/.venv/bin/pylint"
  },
  "launch": {
    "configurations": [
      {
        "cwd": "${workspaceFolder}/haas",
        "program": "${file}",
        "args": ["${relativeFile}"]
      }
    ]
  }
}
```

---

## 🎯 Checklist para Workspace Setup

- [ ] `terminal.integrated.cwd` usa `${workspaceFolder}`
- [ ] `python.defaultInterpreterPath` usa `${workspaceFolder}/.venv`
- [ ] Sem hardcoded paths com `$HOME`, `${USER}`, `${SHELL}`
- [ ] Remote configs usam `${workspaceFolder}`
- [ ] Launch.json `cwd` usa `${workspaceFolder}/...`
- [ ] All paths relative to `${workspaceFolder}`

---

## 🔗 Official References

1. **[Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference)**
   - Complete list of all variables
   - Usage examples
   - Platform-specific notes

2. **[Terminal Troubleshooting](https://code.visualstudio.com/docs/supporting/troubleshoot-terminal-launch)**
   - Common issues
   - Debugging techniques
   - Platform-specific fixes

3. **[Launch Configuration](https://code.visualstudio.com/docs/editor/debugging#_launch-configurations)**
   - Debug config reference
   - Variable usage in debugger
   - Multi-target debugging

4. **[Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)**
   - WSL, SSH, Containers
   - Configuration for remote
   - Troubleshooting remote

5. **[Settings Reference](https://code.visualstudio.com/docs/getstarted/settings)**
   - Settings schema
   - Machine-specific settings
   - Profile settings

---

## 💡 Pro Tips

### Tip 1: Use Workspace Settings for Team
```json
// .vscode/settings.json (version controlled)
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

```json
// .vscode/settings.json (user, not version controlled)
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### Tip 2: Debug Variable Resolution
Add to settings:
```json
{
  "terminal.integrated.logLevel": "debug",
  "remote.WSL.logLevel": "debug"
}
```

Then check **Output** panel for expanded values.

### Tip 3: Test Configuration Locally
```bash
# Test if path exists
test -d "${workspaceFolder}/.venv/bin" && echo "OK" || echo "NOT FOUND"

# Test Python
"${workspaceFolder}/.venv/bin/python" --version
```

### Tip 4: Document Custom Setup
```json
{
  "settings": {
    // ✅ Use ${workspaceFolder} for cross-platform compatibility
    "terminal.integrated.cwd": "${workspaceFolder}",

    // ❌ Don't use: /home/${USER}, $HOME, ${SHELL}
    // These won't be expanded and will cause "directory not found" errors

    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
  }
}
```

---

## ✅ Summary

| Do | Don't |
|----|-------|
| Use `${workspaceFolder}` | Don't hardcode paths |
| Use `${file}`, `${fileExtname}` | Don't use `$FILE`, `$EXT` |
| Use `${env:VAR_NAME}` to read env | Don't use `$VAR` to set |
| Test with multiple machines | Don't assume local setup works everywhere |
| Document variables in comments | Don't leave magic strings |
| Use workspace settings for team | Don't put personal paths in shared files |

---

**Last Updated:** October 23, 2025
**Based On:** VS Code Official Documentation
**Status:** ✅ Best Practices Documented

Para mais detalhes sobre seu setup específico, veja:
- [`TERMINAL-CWD-FIX.md`](./TERMINAL-CWD-FIX.md) - Seu problema & solução
- [`TERMINAL-FIX-APPLIED.md`](./TERMINAL-FIX-APPLIED.md) - Como verificar o fix
