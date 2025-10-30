# Project Helios - WSL Configuration

Este workspace está configurado para abrir **automaticamente no WSL Ubuntu**.

## Como usar

### Opção 1: Abrir via workspace (Recomendado)
1. No VS Code Insiders, vá em `File > Open Workspace from File...`
2. Selecione `project-helios-wsl.code-workspace`
3. O VS Code vai reconectar automaticamente no WSL

### Opção 2: Atalho direto
Crie um atalho com o comando:
```cmd
"C:\Users\fjuni\AppData\Local\Programs\Microsoft VS Code Insiders\Code - Insiders.exe" "c:\Users\fjuni\ysh-b2b\backend\data\project-helios\project-helios-wsl.code-workspace"
```

### Opção 3: Linha de comando
```powershell
code-insiders project-helios-wsl.code-workspace
```

## O que está configurado

✅ **remoteAuthority: wsl+Ubuntu** - Força abertura no WSL  
✅ **Terminal padrão WSL** - Todos os terminais abrem no Ubuntu  
✅ **Python do WSL** - Usa `/mnt/c/.../project-helios/.venv/bin/python`  
✅ **Git do WSL** - Comandos git executam no ambiente Linux  
✅ **File watchers otimizados** - Melhor performance no WSL  

## Recriar venv no WSL (se necessário)

Se a venv ainda estiver apontando para Windows:

```bash
# No terminal WSL
cd /mnt/c/Users/fjuni/ysh-b2b/backend/data/project-helios
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r haas/requirements.txt
pip install -r haas/requirements-dev.txt
```

## Verificar configuração

Após abrir o workspace:
1. Abra o terminal (Ctrl+`) - deve mostrar prompt WSL (rookie@...)
2. Execute: `python --version` - deve usar o Python do WSL
3. Execute: `which python` - deve retornar `/mnt/c/.../project-helios/.venv/bin/python`

## Troubleshooting

**Problema**: VS Code não conecta no WSL  
**Solução**: Instale a extensão "Remote - WSL" (ms-vscode-remote.remote-wsl)

**Problema**: Terminal ainda abre no PowerShell  
**Solução**: Recarregue o workspace (Ctrl+Shift+P > "Developer: Reload Window")

**Problema**: Python não encontrado  
**Solução**: Recrie a venv no WSL conforme instruções acima
