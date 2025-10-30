"""
RAG Finder - Busca Semântica de Produtos

Este módulo usa Retrieval-Augmented Generation (RAG) e fuzzy matching
para encontrar URLs de produtos em bases de conhecimento de fabricantes.
"""

import os
import json
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class RAGFinder:
    def __init__(self, kb_dir: str):
        """
        Inicializa o finder com um diretório de knowledge bases.

        Args:
            kb_dir: Diretório contendo arquivos JSON das KBs
        """
        self.kb_dir = kb_dir
        self.kb_cache = {}  # Cache de KBs carregadas

    def _load_kb(self, manufacturer: str) -> Optional[Dict]:
        """Carrega a KB de um fabricante"""
        if manufacturer in self.kb_cache:
            return self.kb_cache[manufacturer]

        kb_file = os.path.join(self.kb_dir, f"{manufacturer.lower()}_kb.json")
        if not os.path.exists(kb_file):
            return None

        with open(kb_file, "r", encoding="utf-8") as f:
            kb = json.load(f)
            self.kb_cache[manufacturer] = kb
            return kb

    def _prepare_finder(self, knowledge_base: Dict):
        """Prepara o finder com uma KB específica"""
        self.urls = list(knowledge_base.keys())
        self.documents = [
            f"{data['title']} {data['content']}" for data in knowledge_base.values()
        ]

        # Cria o vetorizador TF-IDF
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 2)
        )

        # Vetoriza os documentos
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def find_product_url(
        self, manufacturer: str, query: str, top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Encontra as URLs mais relevantes para uma query de produto.

        Args:
            manufacturer: Nome do fabricante
            query: String de busca (ex: "Deye SUN-8K-SG04LP3-EU")
            top_k: Número de resultados a retornar

        Returns:
            Lista de tuplas (url, score) ordenadas por relevância
        """
        # Carrega KB do fabricante
        kb = self._load_kb(manufacturer)
        if not kb:
            print(f"❌ KB não encontrada para {manufacturer}")
            return []

        # Prepara o finder
        self._prepare_finder(kb)

        # Vetoriza a query
        query_vec = self.vectorizer.transform([query])

        # Calcula similaridade de cosseno
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        # Pega os top_k resultados
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = [(self.urls[idx], float(similarities[idx])) for idx in top_indices]

        return results

    def multi_query_search(
        self, manufacturer: str, queries: List[str], top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Executa múltiplas queries e consolida os resultados.
        URLs que aparecem em múltiplas buscas têm seus scores somados.

        Args:
            manufacturer: Nome do fabricante
            queries: Lista de queries de busca
            top_k: Número de resultados finais a retornar

        Returns:
            Lista de tuplas (url, score_consolidado) ordenadas por relevância
        """
        url_scores = {}  # {url: score_total}

        print(f"\n🔍 Multi-Query RAG ({len(queries)} queries):")

        for i, query in enumerate(queries, 1):
            print(f"   Query {i}: {query}")
            results = self.find_product_url(manufacturer, query, top_k=5)

            for url, score in results:
                if url in url_scores:
                    url_scores[url] += score  # Soma scores de múltiplas queries
                else:
                    url_scores[url] = score

        # Ordena por score consolidado
        sorted_results = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)[
            :top_k
        ]

        print(f"\n   ✅ Score consolidado (top 5):")
        for url, score in sorted_results[:5]:
            print(f"      {score:.3f}: {url}")

        # Retorna dict com best_url, score e queries_matched
        if sorted_results:
            best_url, best_score = sorted_results[0]
            queries_matched = sum(
                1
                for q in queries
                if any(
                    best_url in str(r)
                    for r in self.find_product_url(manufacturer, q, top_k=5)
                )
            )
            return {
                "best_url": best_url,
                "score": best_score,
                "queries_matched": queries_matched,
                "all_results": sorted_results,
            }
        else:
            return {
                "best_url": None,
                "score": 0.0,
                "queries_matched": 0,
                "all_results": [],
            }

    def find_best_match(
        self, manufacturer: str, query: str, threshold: float = 0.1
    ) -> Optional[str]:
        """
        Encontra a melhor correspondência para uma query.

        Args:
            manufacturer: Nome do fabricante
            query: String de busca
            threshold: Score mínimo para considerar uma correspondência válida

        Returns:
            URL da melhor correspondência ou None
        """
        results = self.find_product_url(manufacturer, query, top_k=1)

        if results and results[0][1] >= threshold:
            return results[0][0]  # Retorna apenas a URL

        return None

    def search_with_context(
        self,
        model_name: str,
        series: str = "",
        power: str = "",
        manufacturer: str = "",
        top_k: int = 5,
    ) -> List[Tuple[str, float, Dict]]:
        """
        Busca usando informações contextuais estruturadas.

        Args:
            model_name: Nome/código do modelo
            series: Série do produto (opcional)
            power: Potência (opcional)
            manufacturer: Fabricante (opcional)
            top_k: Número de resultados

        Returns:
            Lista de tuplas (url, score, metadata)
        """
        # Constrói query contextual
        query_parts = [model_name]
        if series:
            query_parts.append(series)
        if power:
            query_parts.append(f"{power}W")
        if manufacturer:
            query_parts.append(manufacturer)

        query = " ".join(query_parts)

        # Busca
        results = self.find_product_url(query, top_k)

        # Adiciona metadados
        enriched_results = []
        for url, score in results:
            metadata = self.knowledge_base[url]
            enriched_results.append((url, score, metadata))

        return enriched_results


if __name__ == "__main__":
    # Exemplo de uso com base de conhecimento mockada
    mock_kb = {
        "https://example.com/deye-sun-8k": {
            "title": "Deye SUN-8K-SG04LP3-EU Hybrid Inverter",
            "content": "The SUN-8K-SG04LP3-EU is a powerful 8kW hybrid inverter...",
        },
        "https://example.com/deye-sun-12k": {
            "title": "Deye SUN-12K Three Phase Inverter",
            "content": "High efficiency 12kW three phase solar inverter...",
        },
        "https://example.com/growatt-min-5000": {
            "title": "Growatt MIN 5000TL-XH Inverter",
            "content": "Compact and efficient 5kW single phase inverter...",
        },
    }

    finder = RAGFinder(mock_kb)

    # Teste 1: Busca simples
    print("🔍 Teste 1: Busca por 'Deye SUN-8K'")
    results = finder.find_product_url("Deye SUN-8K", top_k=3)
    for url, score in results:
        print(f"  - {url} (score: {score:.3f})")

    # Teste 2: Melhor correspondência
    print("\n🎯 Teste 2: Melhor correspondência para 'Growatt MIN 5000'")
    best_url, best_score = finder.find_best_match("Growatt MIN 5000")
    if best_url:
        print(f"  ✅ Encontrado: {best_url} (score: {best_score:.3f})")
    else:
        print(f"  ❌ Nenhuma correspondência encontrada")

    # Teste 3: Busca contextual
    print("\n🧠 Teste 3: Busca contextual")
    results = finder.search_with_context(
        model_name="SUN-8K-SG04LP3-EU", manufacturer="Deye", power="8000", top_k=2
    )
    for url, score, metadata in results:
        print(f"  - {url}")
        print(f"    Score: {score:.3f}")
        print(f"    Título: {metadata['title']}")
