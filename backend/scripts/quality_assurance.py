"""
Módulo de Quality Assurance (QA) de Imagens

Este script verifica se uma imagem processada está em conformidade com as
regras do Meta Commerce e outras heurísticas de qualidade.
"""

import os
from PIL import Image

from config import IMAGE_PRIMARY_SIZE, IMAGE_OUTPUT_FORMAT


def qa_image(image_path: str) -> dict:
    """
    Executa uma série de verificações de qualidade em uma imagem.

    Args:
        image_path (str): O caminho para a imagem a ser verificada.

    Returns:
        dict: Um dicionário com os resultados do QA.
    """
    if not os.path.exists(image_path):
        return {"status": "REPROVADO", "reason": "Arquivo não encontrado"}

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)

            # 1. Verificação de Dimensões
            if width < 500 or height < 500:
                return {
                    "status": "REPROVADO",
                    "reason": f"Dimensões ({width}x{height}) menores que 500x500px",
                }

            # 2. Verificação de Tamanho do Arquivo
            if file_size_mb > 8:
                return {
                    "status": "REPROVADO",
                    "reason": f"Tamanho do arquivo ({file_size_mb:.2f} MB) excede 8 MB",
                }

            # 3. Verificação de Formato
            if img.format.upper() not in [IMAGE_OUTPUT_FORMAT, "PNG"]:
                return {
                    "status": "REPROVADO",
                    "reason": f"Formato inválido ({img.format}). Esperado JPEG ou PNG.",
                }

            # 4. Heurística de Fundo Branco/Neutro (simplificada)
            # Pega uma amostra das bordas para verificar se são predominantemente brancas
            border_pixels = (
                list(img.getdata())[0:width]  # Top
                + list(img.getdata())[width * (height - 1) :]  # Bottom
                + [img.getpixel((0, y)) for y in range(height)]  # Left
                + [img.getpixel((width - 1, y)) for y in range(height)]  # Right
            )

            white_pixels = sum(
                1 for p in border_pixels if p[0] > 240 and p[1] > 240 and p[2] > 240
            )
            bg_score = (white_pixels / len(border_pixels)) * 100

            if bg_score < 75:
                # Não reprova, mas marca como pendente para revisão manual
                return {
                    "status": "PENDENTE",
                    "reason": f"Fundo pode não ser neutro (Score: {bg_score:.1f}%)",
                }

            # 5. Detecção de Overlay (placeholder)
            # Uma implementação real usaria OCR ou detecção de contornos.
            overlay_score = 0  # 0 = sem overlay

            return {
                "status": "APROVADO",
                "width": width,
                "height": height,
                "size_mb": round(file_size_mb, 2),
                "format": img.format,
                "bg_score": round(bg_score, 1),
                "overlay_score": overlay_score,
            }

    except Exception as e:
        return {"status": "ERRO", "reason": str(e)}


if __name__ == "__main__":
    # Para testar, você precisaria de uma imagem de exemplo.
    # Suponha que 'example_primary.jpg' exista.
    # result = qa_image('example_primary.jpg')
    # print(f"Resultado do QA: {result}")
    print("Módulo de QA pronto. Execute o orquestrador para usar.")
