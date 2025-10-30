#!/bin/bash
# Script para recriar venv CORRETAMENTE no WSL
# Deve ser executado DENTRO do WSL, não no Windows
# Uso: bash scripts/wsl-setup-venv.sh

set -e

echo "🚀 Iniciando setup da venv NO WSL..."
echo ""

# Detectar se estamos no WSL
if [[ -z "${WSL_DISTRO_NAME}" ]] && [[ ! -f /etc/wsl.conf ]]; then
    echo "❌ ERRO: Este script DEVE ser executado DENTRO do WSL!"
    echo ""
    echo "Para executar no WSL, use:"
    echo "  wsl bash scripts/wsl-setup-venv.sh"
    echo ""
    echo "Ou abra o VS Code no WSL com:"
    echo "  code-insiders --remote wsl+Ubuntu project-helios-wsl.code-workspace"
    exit 1
fi

echo "✅ Executando no WSL: ${WSL_DISTRO_NAME:-Ubuntu}"
echo ""

# 1. Limpar venv antiga se existir
VENV_DIR="$HOME/.venvs/helios"

if [[ -d "$VENV_DIR" ]]; then
    echo "♻️  Removendo venv antiga em $VENV_DIR..."
    rm -rf "$VENV_DIR"
fi

# 2. Criar nova venv
echo "📦 Criando novo ambiente virtual..."
python3 -m venv "$VENV_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "❌ ERRO: Falha ao criar venv"
    exit 1
fi

echo "✅ Venv criada em: $VENV_DIR"
echo ""

# 3. Ativar venv
echo "🔌 Ativando venv..."
source "$VENV_DIR/bin/activate"

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ ERRO: Falha ao ativar venv"
    exit 1
fi

echo "✅ Venv ativa: $VIRTUAL_ENV"
echo ""

# 4. Atualizar pip
echo "⬆️  Atualizando pip..."
python -m pip install --upgrade pip setuptools wheel
echo ""

# 5. Instalar dependências
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REQUIREMENTS="$PROJECT_ROOT/haas/requirements.txt"

if [[ ! -f "$REQUIREMENTS" ]]; then
    echo "❌ ERRO: $REQUIREMENTS não encontrado"
    exit 1
fi

echo "📚 Instalando dependências de $REQUIREMENTS..."
pip install -r "$REQUIREMENTS"

echo ""
echo "✅ Dependências instaladas com sucesso!"
echo ""

# 6. Verificar Python
echo "🔍 Verificando Python..."
python --version
echo "Python path: $(which python)"
echo ""

# 7. Dicas finais
echo "✅ ✅ ✅ SETUP CONCLUÍDO COM SUCESSO! ✅ ✅ ✅"
echo ""
echo "📍 Próximos passos:"
echo ""
echo "1. No VS Code Insiders, selecione o interpretador Python:"
echo "   - Ctrl+Shift+P → 'Python: Select Interpreter'"
echo "   - Escolha: ~/.venvs/helios/bin/python"
echo ""
echo "2. Ou execute no WSL:"
echo "   - Abra um terminal WSL"
echo "   - source ~/.venvs/helios/bin/activate"
echo ""
echo "3. Teste a instalação:"
echo "   - python --version"
echo "   - pip list"
echo ""
echo "4. Execute os testes:"
echo "   - cd $PROJECT_ROOT/haas"
echo "   - python -m pytest tests/ -v"
echo ""
echo "💡 Dica: Para abrir SEMPRE no WSL, use:"
echo "   code-insiders project-helios-wsl.code-workspace"
echo ""
