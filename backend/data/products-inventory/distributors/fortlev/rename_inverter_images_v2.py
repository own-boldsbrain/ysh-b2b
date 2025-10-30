#!/usr/bin/env python3
"""
Script melhorado para renomear imagens de inversores Fortlev.
Versão 2.0 - Com suporte a variações de nomes de arquivo.
"""
import json
import os
import shutil
import re
from pathlib import Path

# Caminhos
INVERTERS_JSON = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\products-inventory-backup-20251017-134630\distributors\fortlev\fortlev-inverters.json"
IMAGES_DIR = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\distributors\fortlev\organized_images\inverters"
RENAMED_DIR = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\distributors\fortlev\organized_images\inverters_renamed_v2"


def sanitize_filename(name):
    """Remove caracteres inválidos do nome do arquivo."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "")
    return name.strip()


def extract_image_codes(image_url):
    """
    Extrai todos os códigos IIN possíveis da URL.
    Retorna uma lista de códigos encontrados.
    """
    if not image_url:
        return []

    # Procurar por padrão IIN seguido de 5 dígitos
    codes = re.findall(r"IIN\d{5}", image_url)
    return list(set(codes))  # Remover duplicatas


def main():
    # Criar diretório de destino
    os.makedirs(RENAMED_DIR, exist_ok=True)

    # Carregar dados dos inversores
    print(f"Carregando dados de: {INVERTERS_JSON}")
    with open(INVERTERS_JSON, "r", encoding="utf-8") as f:
        inverters = json.load(f)

    print(f"Total de inversores encontrados: {len(inverters)}")

    # Criar mapeamento de código de imagem para nome do produto
    # Agora suporta múltiplos códigos por produto
    image_mapping = {}

    for inverter in inverters:
        image_codes = extract_image_codes(inverter.get("image", ""))

        if image_codes:
            # Criar nome de arquivo baseado no fabricante e modelo
            manufacturer = inverter.get("manufacturer", "Unknown").upper()
            name = inverter.get("name", "")

            # Simplificar o nome
            name_clean = (
                name.replace("ON-GRID", "")
                .replace("GRID-TIE", "")
                .replace("OFF-GRID", "")
                .strip()
            )

            # Criar nome de arquivo
            new_name = f"{manufacturer}_{name_clean}"
            new_name = sanitize_filename(new_name)
            new_name = new_name.replace(" ", "_")

            # Limitar tamanho do nome
            if len(new_name) > 100:
                new_name = new_name[:100]

            # Mapear todos os códigos encontrados para este produto
            for code in image_codes:
                image_mapping[code] = {
                    "new_name": new_name,
                    "original_name": inverter["name"],
                    "manufacturer": manufacturer,
                    "price": inverter.get("price", "N/A"),
                    "id": inverter.get("id", ""),
                }

    print(f"\nMapeamento criado para {len(image_mapping)} códigos de imagem")

    # Listar arquivos de imagem
    image_files = list(Path(IMAGES_DIR).glob("*.png"))
    print(f"Arquivos de imagem encontrados: {len(image_files)}")

    # Renomear arquivos
    renamed_count = 0
    not_found = []

    for image_file in image_files:
        image_code = image_file.stem  # Nome sem extensão

        if image_code in image_mapping:
            mapping = image_mapping[image_code]
            new_filename = f"{mapping['new_name']}.png"
            new_path = Path(RENAMED_DIR) / new_filename

            # Se arquivo já existe, adicionar sufixo
            counter = 1
            while new_path.exists():
                new_filename = f"{mapping['new_name']}_{counter}.png"
                new_path = Path(RENAMED_DIR) / new_filename
                counter += 1

            # Copiar arquivo com novo nome
            shutil.copy2(image_file, new_path)
            renamed_count += 1

            print(f"✓ {image_code}.png -> {new_filename}")
            print(f"  ID: {mapping['id']}")
            print(f"  Produto: {mapping['original_name']}")
            print(f"  Preço: {mapping['price']}")
            print()
        else:
            not_found.append(image_code)

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DA RENOMEAÇÃO (V2)")
    print("=" * 80)
    print(f"Total de imagens processadas: {len(image_files)}")
    print(f"Imagens renomeadas com sucesso: {renamed_count}")
    print(f"Imagens sem mapeamento: {len(not_found)}")
    print(f"Taxa de sucesso: {(renamed_count/len(image_files)*100):.1f}%")

    if not_found:
        print("\nImagens sem mapeamento encontrado:")
        for code in not_found:
            print(f"  - {code}.png")

    print(f"\nImagens renomeadas salvas em: {RENAMED_DIR}")


if __name__ == "__main__":
    main()
