"""
Módulo para Extração de Imagens de Arquivos PDF.

Este script usa a biblioteca PyMuPDF (fitz) para rasterizar a primeira
página de um documento PDF, que geralmente contém o packshot do produto,
e a salva como uma imagem de alta qualidade.
"""

import os
import fitz  # PyMuPDF


def extract_first_page_as_image(pdf_path: str, output_image_path: str, dpi: int = 300):
    """
    Extrai a primeira página de um PDF e a salva como uma imagem.

    Args:
        pdf_path (str): O caminho para o arquivo PDF de entrada.
        output_image_path (str): O caminho para salvar a imagem de saída.
        dpi (int): A resolução (dots per inch) para a renderização da imagem.
    """
    if not os.path.exists(pdf_path):
        print(f"❌ Erro: Arquivo PDF não encontrado em '{pdf_path}'")
        return False

    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # Carrega a primeira página (índice 0)

        # Renderiza a página para um pixmap (imagem) com o DPI especificado
        pix = page.get_pixmap(dpi=dpi)

        # Salva o pixmap como um arquivo de imagem (PNG para manter a qualidade)
        pix.save(output_image_path)

        print(f"✅ Imagem extraída com sucesso do PDF para '{output_image_path}'")
        doc.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao extrair imagem do PDF {pdf_path}: {e}")
        if "doc" in locals() and doc:
            doc.close()
        return False


if __name__ == "__main__":
    # Para testar, você precisaria de um arquivo PDF de exemplo.
    # Suponha que 'example.pdf' exista.
    # extract_first_page_as_image('example.pdf', 'example_from_pdf.png')
    print("Módulo de extração de PDF pronto. Execute o orquestrador para usar.")
