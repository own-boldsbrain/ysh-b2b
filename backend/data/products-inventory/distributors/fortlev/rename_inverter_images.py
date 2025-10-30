#!/usr/bin/env python3
"""
Script para renomear imagens de inversores Fortlev com base nos dados do JSON.
"""
import json
import os
import shutil
from pathlib import Path

# Caminhos
INVERTERS_JSON = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\products-inventory-backup-20251017-134630\distributors\fortlev\fortlev-inverters.json"
IMAGES_DIR = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\distributors\fortlev\organized_images\inverters"
RENAMED_DIR = r"c:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend\data\products-inventory\distributors\fortlev\organized_images\inverters_renamed"


def sanitize_filename(name):
    """Remove caracteres inválidos do nome do arquivo."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "")
    return name.strip()


def extract_image_code(image_url):
    """Extrai o código da imagem (ex: IIN00384) da URL."""
    if not image_url:
        return None
    parts = image_url.split("/")
    for part in parts:
        if part.startswith("IIN") and ".png" in part:
            return part.replace(".png", "")
    return None


def main():
    # Criar diretório de destino
    os.makedirs(RENAMED_DIR, exist_ok=True)

    # Carregar dados dos inversores
    print(f"Carregando dados de: {INVERTERS_JSON}")
    with open(INVERTERS_JSON, "r", encoding="utf-8") as f:
        inverters = json.load(f)

    print(f"Total de inversores encontrados: {len(inverters)}")

    # Criar mapeamento de código de imagem para nome do produto
    image_mapping = {}
    for inverter in inverters:
        image_code = extract_image_code(inverter.get("image", ""))
        if image_code:
            # Criar nome de arquivo baseado no fabricante e modelo
            manufacturer = inverter.get("manufacturer", "Unknown").upper()
            name = inverter.get("name", "")

            # Simplificar o nome
            # Remover partes repetitivas
            name_clean = name.replace("ON-GRID", "").replace("GRID-TIE", "").strip()

            # Criar nome de arquivo
            new_name = f"{manufacturer}_{name_clean}"
            new_name = sanitize_filename(new_name)
            new_name = new_name.replace(" ", "_")

            # Limitar tamanho do nome
            if len(new_name) > 100:
                new_name = new_name[:100]

            image_mapping[image_code] = {
                "new_name": new_name,
                "original_name": inverter["name"],
                "manufacturer": manufacturer,
                "price": inverter.get("price", "N/A"),
            }

    print(f"\nMapeamento criado para {len(image_mapping)} imagens")

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

            # Copiar arquivo com novo nome
            shutil.copy2(image_file, new_path)
            renamed_count += 1

            print(f"✓ {image_code}.png -> {new_filename}")
            print(f"  Produto: {mapping['original_name']}")
            print(f"  Preço: {mapping['price']}")
            print()
        else:
            not_found.append(image_code)

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DA RENOMEAÇÃO")
    print("=" * 80)
    print(f"Total de imagens processadas: {len(image_files)}")
    print(f"Imagens renomeadas com sucesso: {renamed_count}")
    print(f"Imagens sem mapeamento: {len(not_found)}")

    if not_found:
        print("\nImagens sem mapeamento encontrado:")
        for code in not_found:
            print(f"  - {code}.png")

    print(f"\nImagens renomeadas salvas em: {RENAMED_DIR}")


if __name__ == "__main__":
    main()
