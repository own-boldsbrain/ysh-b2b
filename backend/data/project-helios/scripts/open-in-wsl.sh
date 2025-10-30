#!/bin/bash
# Script para abrir o Project Helios no VS Code via WSL
# Uso: ./scripts/open-in-wsl.sh

set -e

# Configurações padrão
VSCODE_CMD="${1:-code-insiders}"
WSL_DISTRO="${2:-Ubuntu}"

echo "🚀 Abrindo Project Helios no WSL..."

# Verificar se estamos no WSL ou Linux nativo
if [[ -n "${WSL_DISTRO_NAME}" ]]; then
    echo "✅ Executando dentro do WSL: ${WSL_DISTRO_NAME}"
    IN_WSL=true
else
    echo "ℹ️  Executando em Linux nativo"
    IN_WSL=false
fi

# Obter o diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORKSPACE_FILE="${PROJECT_ROOT}/project-helios-wsl.code-workspace"

echo "📁 Diretório do projeto: $PROJECT_ROOT"

# Verificar se VS Code está instalado
VSCODE_FOUND=false
for cmd in code-insiders code; do
    if command -v "$cmd" &> /dev/null; then
        VSCODE_CMD="$cmd"
        VSCODE_FOUND=true
        echo "✅ VS Code encontrado: $cmd"
        break
    fi
done

if [[ "$VSCODE_FOUND" == false ]]; then
    echo "❌ VS Code não encontrado. Instalando..."
    
    # Tentar instalar VS Code automaticamente
    if command -v snap &> /dev/null; then
        echo "📦 Instalando via snap..."
        sudo snap install code --classic
        VSCODE_CMD="code"
    elif command -v apt &> /dev/null; then
        echo "📦 Instalando via apt..."
        wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
        sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
        sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
        sudo apt update
        sudo apt install -y code
        VSCODE_CMD="code"
    else
        echo "❌ Não foi possível instalar VS Code automaticamente."
        echo "Por favor, instale manualmente: https://code.visualstudio.com/docs/setup/linux"
        exit 1
    fi
fi

# Abrir o workspace
if [[ -f "$WORKSPACE_FILE" ]]; then
    echo "📁 Abrindo workspace: $WORKSPACE_FILE"
    
    if [[ "$IN_WSL" == true ]]; then
        # Já estamos no WSL, abrir normalmente
        "$VSCODE_CMD" "$WORKSPACE_FILE"
    else
        # Em Linux nativo, tentar abrir com remote WSL se disponível
        if command -v wsl.exe &> /dev/null; then
            echo "🔄 Abrindo no WSL: $WSL_DISTRO"
            "$VSCODE_CMD" "$WORKSPACE_FILE" --remote "wsl+$WSL_DISTRO"
        else
            echo "📂 Abrindo localmente (WSL não disponível)"
            "$VSCODE_CMD" "$WORKSPACE_FILE"
        fi
    fi
else
    echo "⚠️  Workspace file não encontrado, abrindo diretório atual"
    
    if [[ "$IN_WSL" == true ]]; then
        "$VSCODE_CMD" "$PROJECT_ROOT"
    else
        if command -v wsl.exe &> /dev/null; then
            "$VSCODE_CMD" "$PROJECT_ROOT" --remote "wsl+$WSL_DISTRO"
        else
            "$VSCODE_CMD" "$PROJECT_ROOT"
        fi
    fi
fi

echo ""
echo "✅ Project Helios aberto com sucesso!"
echo ""
echo "🔄 Próximos passos:"
echo "1. Aguarde o VS Code carregar"
echo "2. Abra o terminal integrado (Ctrl+\`)"
echo "3. Execute os comandos de setup:"
echo ""
echo "   # Criar ambiente virtual"
echo "   python3 -m venv ~/.venvs/project-helios"
echo "   source ~/.venvs/project-helios/bin/activate"
echo ""
echo "   # Instalar dependências"
echo "   pip install -r haas/requirements.txt"
echo ""
echo "4. Configure o interpretador Python:"
echo "   - Ctrl+Shift+P"
echo "   - Digite: Python: Select Interpreter"
echo "   - Selecione: ~/.venvs/project-helios/bin/python"
echo ""
echo "5. Teste a configuração:"
echo "   python --version"
echo "   cd haas && python -m pytest"