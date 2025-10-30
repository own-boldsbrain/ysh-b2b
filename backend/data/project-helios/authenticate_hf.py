"""
Script para autenticação no Hugging Face
Execute este script e cole seu token quando solicitado
"""

from huggingface_hub import login, HfApi
import sys

print("=" * 60)
print("AUTENTICAÇÃO HUGGING FACE")
print("=" * 60)
print("\nPara obter seu token:")
print("1. Acesse: https://huggingface.co/settings/tokens")
print("2. Clique em 'New token'")
print("3. Nome: 'helios-aneel-datasets'")
print("4. Tipo: 'Write'")
print("5. Copie o token gerado")
print("\n" + "=" * 60)

token = input("\nCole seu token aqui e pressione ENTER: ").strip()

if not token:
    print("❌ Token vazio. Abortando.")
    sys.exit(1)

try:
    # Login com o token
    login(token=token, add_to_git_credential=True)
    print("\n✅ Autenticação bem-sucedida!")

    # Testar API
    api = HfApi()
    user_info = api.whoami()
    print(f"\n👤 Usuário logado: {user_info['name']}")
    print(f"📧 Email: {user_info.get('email', 'N/A')}")

    print("\n" + "=" * 60)
    print("Token salvo com sucesso!")
    print("Você já pode executar: python upload_to_huggingface.py")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Erro na autenticação: {e}")
    print("\nVerifique se:")
    print("1. O token está correto")
    print("2. O token tem permissão 'Write'")
    print("3. Sua conexão com internet está ativa")
    sys.exit(1)
