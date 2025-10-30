
#!/bin/bash
# Script de setup rápido para Project Helios
# Este script configura o ambiente Python e instala dependências

set -e

echo "🔧 Configurando ambiente Python para Project Helios..."

# Verificar se Python 3 está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instalando..."
    
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    else
        echo "❌ Gerenciador de pacotes não suportado. Instale Python 3 manualmente."
        exit 1
    fi
fi

echo "✅ Python encontrado: $(python3 --version)"

# Configurar ambiente virtual
VENV_PATH="$HOME/.venvs/project-helios"

if [[ -d "$VENV_PATH" ]]; then
    echo "♻️  Ambiente virtual já existe. Removendo..."
    rm -rf "$VENV_PATH"
fi

echo "📦 Criando ambiente virtual..."
python3 -m venv "$VENV_PATH"

echo "🔌 Ativando ambiente virtual..."
source "$VENV_PATH/bin/activate"

echo "✅ Ambiente virtual ativo: $VIRTUAL_ENV"

# Atualizar pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Obter diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REQUIREMENTS_FILE="$PROJECT_ROOT/haas/requirements.txt"

# Instalar dependências se o arquivo existir
if [[ -f "$REQUIREMENTS_FILE" ]]; then
    echo "📚 Instalando dependências do haas/requirements.txt..."
    pip install -r "$REQUIREMENTS_FILE"
    echo "✅ Dependências instaladas!"
else
    echo "⚠️  Arquivo requirements.txt não encontrado em haas/"
    echo "📦 Instalando dependências básicas..."
    pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary pydantic pytest
fi

echo ""
echo "🎉 Setup concluído com sucesso!"
echo ""
echo "📍 Para usar o ambiente:"
echo "   source ~/.venvs/project-helios/bin/activate"
echo ""
echo "🧪 Para testar:"
echo "   cd haas && python -m pytest"
echo ""
echo "🚀 Para executar a aplicação:"
echo "   cd haas && python run.py"