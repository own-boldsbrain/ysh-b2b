"""
Módulo de Processamento e Normalização de Imagens

Este script contém funções para normalizar as imagens capturadas,
garantindo que elas atendam aos requisitos do Meta Commerce.
- Redimensionamento para 1024x1024 e 600x600.
- Adição de letterbox (fundo branco) para manter a proporção.
- Conversão para o formato de saída (JPEG).
- Remoção de metadados EXIF.
"""

from PIL import Image, ImageOps

from config import (
    IMAGE_PRIMARY_SIZE,
    IMAGE_SECONDARY_SIZE,
    IMAGE_QUALITY,
    IMAGE_OUTPUT_FORMAT,
    CANVAS_COLOR,
)


def process_image(
    input_path: str, output_path_primary: str, output_path_secondary: str
):
    """
    Processa uma imagem de entrada e salva as versões primária e secundária.

    Args:
        input_path (str): Caminho para a imagem original baixada.
        output_path_primary (str): Caminho para salvar a imagem primária (1024x1024).
        output_path_secondary (str): Caminho para salvar a imagem secundária (600x600).
    """
    try:
        with Image.open(input_path) as img:
            # Converte para RGB para garantir compatibilidade (remove canal alfa)
            img = img.convert("RGB")

            # Remove dados EXIF para privacidade e redução de tamanho
            img_data = list(img.getdata())
            img_without_exif = Image.new(img.mode, img.size)
            img_without_exif.putdata(img_data)

            # Gera e salva a imagem primária
            _resize_and_save(img_without_exif, output_path_primary, IMAGE_PRIMARY_SIZE)

            # Gera e salva a imagem secundária
            _resize_and_save(
                img_without_exif, output_path_secondary, IMAGE_SECONDARY_SIZE
            )

            print(
                f"✅ Imagem processada e salva em '{output_path_primary}' e '{output_path_secondary}'."
            )

    except Exception as e:
        print(f"❌ Erro ao processar a imagem {input_path}: {e}")


def _resize_and_save(image: Image, output_path: str, size: tuple):
    """
    Redimensiona a imagem usando letterboxing e a salva no caminho especificado.
    """
    # Cria um canvas com a cor de fundo e o tamanho desejados
    canvas = Image.new("RGB", size, CANVAS_COLOR)

    # Redimensiona a imagem original para caber no canvas, mantendo a proporção
    resized_img = image.copy()
    resized_img.thumbnail(size, Image.Resampling.LANCZOS)

    # Calcula a posição para centralizar a imagem no canvas
    paste_x = (size[0] - resized_img.width) // 2
    paste_y = (size[1] - resized_img.height) // 2

    # Cola a imagem redimensionada no centro do canvas
    canvas.paste(resized_img, (paste_x, paste_y))

    # Salva a imagem final
    canvas.save(
        output_path, format=IMAGE_OUTPUT_FORMAT, quality=IMAGE_QUALITY, optimize=True
    )


if __name__ == "__main__":
    # Para testar, você precisaria de uma imagem de exemplo.
    # Suponha que 'example.jpg' exista no mesmo diretório.
    # from PIL import Image
    # img = Image.new('RGB', (1200, 800), color = 'red')
    # img.save('example.jpg')

    # process_image(
    #     'example.jpg',
    #     'example_primary.jpg',
    #     'example_secondary.jpg'
    # )
    print("Módulo de processamento de imagem pronto. Execute o orquestrador para usar.")
