# VS Code Workspace Setup - Project Helios (HaaS)

> **Configuração Automática do VS Code com GitHub Copilot, Pylance, e 50+ Extensões Recomendadas**

## 📋 Visão Geral

Este guia documenta a configuração profissional do VS Code para desenvolvimento máximo-performance no Project Helios com:

- ✅ GitHub Copilot integrado (AI-assisted development)
- ✅ Pylance para type checking e análise estática
- ✅ GitLens para git workflows avançados
- ✅ Docker, Pytest, Celery, Alembic integrado
- ✅ 50+ extensões curadas para produtividade máxima
- ✅ Configurações otimizadas para performance (150+ ajustes)
- ✅ Debug configs para FastAPI, Celery, pytest
- ✅ Remote WSL suport para Windows users

## 🚀 Quick Start (3 Minutos)

### 1. Abrir o Workspace

**Windows (PowerShell):**
```powershell
cd c:\Users\fjuni\ysh-b2b\backend\data\project-helios
code-insiders project-helios-wsl.code-workspace
```

**Linux/macOS/WSL (Bash):**
```bash
cd ~/ysh-b2b/backend/data/project-helios
code-insiders project-helios-wsl.code-workspace
```

### 2. VS Code vai reconhecer as extensões recomendadas

Na janela de notificação que aparecer, clique em:
- **"Install All"** para instalar tudo de uma vez, OU
- **"Show Recommendations"** para instalar seletivamente

### 3. Usar o script de auto-install (Alternativa)

**Windows (PowerShell):**
```powershell
.\scripts\install-vscode-extensions.ps1
```

**Linux/macOS/WSL (Bash):**
```bash
bash scripts/install-vscode-extensions.sh
```

## 📁 Arquivos de Configuração

### `.vscode/settings.json`
- **Lines:** 150+
- **Purpose:** Otimizações de performance, formatação, linting, temas
- **Key Sections:**
  - Python type checking (Pylance + Pylint)
  - GitHub Copilot activation
  - Editor formatters (Black)
  - File watching exclusions (performance)
  - Terminal defaults (WSL)
  - Docker integration
  - Theme (One Dark Pro Darker)

**View:** `c:\Users\fjuni\ysh-b2b\backend\data\project-helios\.vscode\settings.json`

### `.vscode/extensions.json`
- **Extensions:** 50+
- **Categories:** Copilot, Python, Remote, Docker, Testing, Git, etc.
- **Auto-Install:** VS Code detecta e oferece instalar automaticamente

**Top Priority Extensions:**
1. `GitHub.copilot` - AI-powered code suggestions
2. `GitHub.copilot-chat` - Chat interface com Copilot
3. `ms-python.vscode-pylance` - Type checking + LSP
4. `eamodio.gitlens` - Advanced git integration
5. `ms-azuretools.vscode-docker` - Docker support

**View:** `c:\Users\fjuni\ysh-b2b\backend\data\project-helios\.vscode\extensions.json`

### `.vscode/launch.json`
- **Configurations:** 13 debug configs + 2 compounds
- **Categories:**
  - **API:** FastAPI (uvicorn), com e sem debugger
  - **Testing:** pytest (all, current file, single test)
  - **Background:** Celery worker, Flower monitor
  - **Utilities:** Python shell, Alembic migrations
  - **Compounds:** Full stack (API + Worker + Monitor)

**View:** `c:\Users\fjuni\ysh-b2b\backend\data\project-helios\.vscode\launch.json`

## 🎮 Usando Debug Configurations

### FastAPI Development Server

Pressione `F5` (ou **Run > Start Debugging**) e selecione:
```
FastAPI: uvicorn (Development)
```

O servidor inicia em `http://localhost:8000` com hot-reload habilitado.

**Navegar em Debug:**
- `F5` - Continue
- `F10` - Step over
- `F11` - Step into
- `Shift+F11` - Step out
- `Ctrl+Shift+D` - Show debug console

### Executar Testes com Pytest

Selecione a configuração:
```
pytest: All Tests       # Todos os testes
pytest: Current File    # Arquivo aberto
pytest: Single Test     # Teste específico (select function)
```

### Full Stack (API + Celery + Flower)

Para desenvolvimento com background tasks:
```
Full Stack (API + Worker + Monitor)
```

Esto inicia:
- FastAPI em `http://localhost:8000`
- Celery worker (4 concurrency)
- Flower monitor em `http://localhost:5555`

## 💬 GitHub Copilot

### Inicializar

1. Abra o workspace com `code-insiders project-helios-wsl.code-workspace`
2. Extensão `GitHub.copilot` ativará automaticamente
3. Clique no ícone do Copilot na sidebar (left panel)
4. Faça login com sua conta GitHub

### Usar

- **Inline Suggestions:** Comece a digitar, Copilot sugerirá código em cinza
  - `Tab` para aceitar
  - `Escape` para rejeitar

- **Copilot Chat:** `Ctrl+Shift+I` (ou clique no ícone)
  - `/explain` - Explicar código selecionado
  - `/doc` - Gerar docstrings
  - `/fix` - Corrigir erro
  - `/tests` - Gerar testes

- **Inline Chat:** `Ctrl+I` para editar inline

### Configurações

**Já ativadas em `.vscode/settings.json`:**
```json
"github.copilot.enable": { "*": true },
"github.copilot.chat.researchEnabled": false,
"github.copilot.advanced.debug": false
```

## 🔧 Configurações Principais

### Python Linting & Type Checking

```json
"python.defaultInterpreterPath": "${workspaceFolder}/haas/.venv/bin/python",
"python.linting.enabled": true,
"python.linting.pylintEnabled": true,
"[python]": {
  "editor.defaultFormatter": "ms-python.black-formatter",
  "editor.formatOnSave": true
}
```

**Result:** Ao salvar um arquivo `.py`, Black formata automaticamente e Pylint marca erros.

### File Watching (Performance)

```json
"files.watcherExclude": {
  "**/.pytest_cache": true,
  "**/__pycache__": true,
  "**/node_modules": true,
  "**/htmlcov": true
}
```

**Result:** VS Code ignora pastas grandes, reduzindo CPU usage.

### Terminal Default

```json
"terminal.integrated.defaultProfile.windows": "PowerShell",
"terminal.integrated.profiles.windows": {
  "WSL": {
    "path": "wsl.exe",
    "args": ["bash", "-i", "-l"]
  }
}
```

**Result:** Terminal integrado usa WSL bash automaticamente no Windows.

## 🌐 Remote WSL Development

### Setup (One-time)

1. Instale "Remote - WSL" no seu **Windows** VS Code host
2. Abra `project-helios-wsl.code-workspace`
3. VS Code detecta `"remoteAuthority": "wsl+Ubuntu"` e conecta automaticamente

### Verify Connection

- Na **status bar** (canto inferior esquerdo), deve aparecer: `WSL: Ubuntu`
- Terminal integrado deve rodar comandos bash (não cmd/PowerShell)
- Python interpreter deve estar em `/home/user/.venvs/helios/bin/python`

### Troubleshoot

Se não conectar:
1. `WSL: Reopen in WSL` (Command Palette: `Ctrl+Shift+P`)
2. Se ainda falhar, executar em PowerShell:
   ```powershell
   bash scripts/wsl-setup-venv.sh
   ```

## 📊 Extensões por Categoria

### GitHub & Copilot (2)
- `GitHub.copilot` - AI code suggestions
- `GitHub.copilot-chat` - Chat interface

### Python Development (5)
- `ms-python.python` - Core Python extension
- `ms-python.vscode-pylance` - Type checking
- `ms-python.debugpy` - Python debugger
- `ms-python.black-formatter` - Code formatter
- `ms-python.pytest` - Test runner

### Remote Development (4)
- `ms-vscode-remote.remote-wsl` - WSL support
- `ms-vscode-remote.remote-containers` - Docker support
- `ms-vscode-remote.remote-ssh` - SSH support

### Code Quality (4)
- `charliermarsh.ruff` - Ultra-fast linter (Rust-based)
- `ms-python.pylint` - Python linter
- `sonarsource.sonarlint-vscode` - SonarLint integration

### Git & Version Control (4)
- `eamodio.gitlens` - Git supercharged
- `GitHub.vscode-pull-request-github` - GitHub PR integration
- `mhutchie.git-graph` - Git graph visualization
- `donjayamanne.githistory` - Git history viewer

### Testing (3)
- `ms-python.pytest` - Pytest integration
- `arjun.run-on-save` - Auto-run tests on save
- `hbenl.vscode-test-explorer` - Test explorer UI

### Docker & DevOps (2)
- `ms-azuretools.vscode-docker` - Docker support
- `ms-azuretools.vscode-kubernetes-tools` - Kubernetes

### API & Database (4)
- `humao.rest-client` - REST client
- `rangav.vscode-thunder-client` - Thunder Client (Postman alternative)
- `cweijan.vscode-postgresql-client2` - PostgreSQL client
- `ms-mssql.mssql` - SQL Server support

### Productivity (5)
- `gruntfuggly.todo-tree` - TODO/FIXME highlighting
- `wayou.vscode-todo-highlight` - Alternative TODO highlighting
- `usernamehw.errorlens` - Inline error/warning lens
- `ms-vscode.makefile-tools` - Makefile support

### Jupyter & ML (5)
- `ms-toolsai.jupyter` - Jupyter notebook support
- `ms-toolsai.vscode-jupyter-cell-tags` - Jupyter cell tags
- `ms-toolsai.vscode-jupyter-slideshow` - Jupyter slideshow

### Themes & Icons (3)
- `zhuangtongfa.Material-theme` - Material theme (One Dark Pro Darker)
- `vscode-icons-team.vscode-icons` - Icon theme
- `PKief.material-icon-theme` - Material icon theme

### Advanced/Utility (3+)
- `ms-vscode.hex` - Hex editor
- `ms-vscode.vscode-js-profile-table` - JS Profiler
- Vários snippets e utils

## 🎯 Performance Tuning

### Diagnostics Mode (Only Open Files)

```json
"python.analysis.diagnosticMode": "openFilesOnly"
```

**Why:** Reduz análise apenas para arquivos abertos. Em `workspace` mode, Pylance analisa todo o projeto, causando lag.

### File Watcher Exclusions

```json
"files.watcherExclude": {
  "**/__pycache__": true,
  "**/.pytest_cache": true,
  "**/htmlcov": true,
  "**/.egg-info": true,
  "**/.git/objects": true
}
```

**Why:** FSEvents (macOS) ou inotify (Linux) monitora mudanças em arquivo. Excluir diretórios grandes (cache, build) reduz I/O.

### Search Exclusions

```json
"search.exclude": {
  "**/__pycache__": true,
  "**/.venv": true,
  "**/node_modules": true,
  "**/dist": true
}
```

**Why:** Buscar em 1M+ arquivos de cache é lento. Excluir venvs, node_modules, builds.

## 📝 Keyboard Shortcuts (Quick Reference)

| Shortcut | Action |
|----------|--------|
| `F5` | Start Debugging |
| `Ctrl+Shift+D` | Debug sidebar |
| `Ctrl+K Ctrl+T` | Choose theme |
| `Ctrl+Shift+I` | Copilot Chat |
| `Ctrl+I` | Inline Chat (Copilot) |
| `Ctrl+Shift+P` | Command palette |
| `Ctrl+~` | Toggle integrated terminal |
| `Ctrl+Shift+\`` | Open new terminal |
| `Ctrl+J` | Toggle bottom panel |
| `Ctrl+B` | Toggle sidebar |
| `F10` | Step over (debug) |
| `F11` | Step into (debug) |

## 🔗 Related Documentation

- **Environment Setup:** See `WSL-SETUP-COMPLETE.md` for WSL/environment troubleshooting
- **Debug Configs:** See `.vscode/launch.json` for all debug configurations
- **Recommended Extensions:** See `.vscode/extensions.json`
- **Editor Settings:** See `.vscode/settings.json` (150+ lines)

## 🆘 Troubleshooting

### Terminal CWD Error: Starting directory does not exist

**Error:** `Process failed to start: Starting directory (cwd) "/home/${USER}/project-helios" does not exist.`

**Solution:**
1. File `.vscode/project-helios-wsl.code-workspace` was updated to use `${workspaceFolder}` instead of hardcoded path
2. Close and reopen VS Code: `code-insiders project-helios-wsl.code-workspace`
3. Open new terminal: `Ctrl+\`` (backtick)
4. Verify with: `pwd` (should show `/mnt/c/Users/...`)

**See:** [`TERMINAL-CWD-FIX.md`](./TERMINAL-CWD-FIX.md) for detailed explanation

### Copilot not showing suggestions

1. Verify `GitHub.copilot` extension is installed
2. Check status bar (lower right): Should show Copilot icon
3. If not authenticated: Click Copilot icon → Login with GitHub
4. Check `.vscode/settings.json` has `"github.copilot.enable": { "*": true }`

### Python path not found

1. Verify WSL venv exists: `wsl ls ~/.venvs/helios/bin/python`
2. Re-create: `bash scripts/wsl-setup-venv.sh`
3. Update `.vscode/settings.json`: `"python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"`

### Tests not running

1. Verify pytest installed: `python -m pytest --version`
2. Check `haas/pytest.ini` exists
3. Run manually: `cd haas && python -m pytest -v`
4. If import errors: `export PYTHONPATH=$PWD/haas:$PYTHONPATH`

### Terminal defaults to cmd instead of bash

1. Check `.vscode/settings.json`: `"terminal.integrated.defaultProfile.windows": "PowerShell"`
2. Add WSL profile:
   ```json
   "terminal.integrated.profiles.windows": {
     "WSL": { "path": "wsl.exe", "args": ["bash", "-i", "-l"] }
   }
   ```

## ✅ Setup Checklist

- [ ] Abrir `project-helios-wsl.code-workspace` em VS Code Insiders
- [ ] Ver notificação de extensões recomendadas
- [ ] Instalar todas as extensões (automático ou manual)
- [ ] Verificar status bar mostra `WSL: Ubuntu`
- [ ] Abrir arquivo `.py` e confirmar Copilot sugestões (tipo-hint)
- [ ] Pressionar `F5` e selecionar `FastAPI: uvicorn (Development)`
- [ ] Servidor deve iniciar em `http://localhost:8000`
- [ ] Abrir `haas/tests/test_distributors.py` e rodar debug `pytest: Current File`
- [ ] Todos os 13 testes passam
- [ ] Conferir Command Palette: `GitHub Copilot: Open`

## 📞 Support

Para dúvidas sobre setup:
1. Checar `WSL-SETUP-COMPLETE.md` (ambiente)
2. Checar `README.md` (projeto)
3. Ver `.vscode/settings.json` comments (explicações inline)
4. Rodar: `code-insiders --version` e `code-insiders --extensions`

---

**Last Updated:** October 2025
**Project:** Helios (HaaS) - Homologação como Serviço
**Author:** GitHub Copilot (Assistant)
