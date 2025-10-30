"""Structured RAG service - incremental indexing for Helios datasets."""

from __future__ import annotations

import csv
import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import Any, Dict, List, Optional

from openai import OpenAI
import numpy as np

from helios_agents.infrastructure.state_store import StateStore

logger = logging.getLogger(__name__)


@dataclass
class StructuredRAGIndex:
    """Represents a dataset node indexed for Structured RAG."""

    dataset_id: str
    path: str
    checksum: str
    columns: List[str]
    sample_rows: List[List[str]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    embeddings: List[List[float]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "path": self.path,
            "checksum": self.checksum,
            "columns": self.columns,
            "sample_rows": self.sample_rows,
            "metadata": self.metadata,
            "embeddings": self.embeddings,
        }


class StructuredRAGService:
    """Creates and persists structured knowledge graphs powering TypeAgent memory."""

    def __init__(
        self,
        state_store: StateStore,
        dataset_root: str,
        namespace: str = "aneel",
        sample_size: int = 5,
        enable_embeddings: bool = False,
        embedding_service: Optional[str] = None,
        embedding_model: str = "text-embedding-ada-002",
    ) -> None:
        self._state_store = state_store
        self._dataset_root = Path(dataset_root).resolve()
        self._namespace = namespace
        self._sample_size = sample_size
        self._enable_embeddings = enable_embeddings
        self._embedding_model = embedding_model
        self._openai_client = OpenAI(api_key=embedding_service) if embedding_service else None
        self._index: Dict[str, StructuredRAGIndex] = {}

        if not self._dataset_root.exists():
            logger.warning("Dataset root não encontrado: %s", self._dataset_root)
        else:
            self._load_cached_index()

    @property
    def namespace(self) -> str:
        return self._namespace

    def indexed_datasets(self) -> List[str]:
        return list(self._index.keys())

    def _load_cached_index(self) -> None:
        cached = self._state_store.load_state(f"{self._namespace}:structured_rag_index")
        if not cached:
            return
        for item in cached.get("datasets", []):
            try:
                index_entry = StructuredRAGIndex(
                    dataset_id=item["dataset_id"],
                    path=item["path"],
                    checksum=item["checksum"],
                    columns=item.get("columns", []),
                    sample_rows=item.get("sample_rows", []),
                    metadata=item.get("metadata", {}),
                    embeddings=item.get("embeddings", []),
                )
                self._index[index_entry.dataset_id] = index_entry
            except KeyError:
                continue

    def _checksum(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _extract_sample(self, path: Path) -> StructuredRAGIndex:
        relative_id = path.relative_to(self._dataset_root).as_posix()
        checksum = self._checksum(path)
        columns: List[str] = []
        sample_rows: List[List[str]] = []

        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                columns = next(reader, [])
                for idx, row in enumerate(reader):
                    sample_rows.append(row)
                    if idx + 1 >= self._sample_size:
                        break
        except UnicodeDecodeError:
            with path.open("r", encoding="latin-1", newline="") as handle:
                reader = csv.reader(handle)
                columns = next(reader, [])
                for idx, row in enumerate(reader):
                    sample_rows.append(row)
                    if idx + 1 >= self._sample_size:
                        break

        metadata = {
            "indexed_at": time(),
            "size_bytes": path.stat().st_size,
            "columns_count": len(columns),
            "sample_size": len(sample_rows),
        }

        return StructuredRAGIndex(
            dataset_id=relative_id,
            path=str(path),
            checksum=checksum,
            columns=columns,
            sample_rows=sample_rows,
            metadata=metadata,
        )

    def _embed_text(self, text: str) -> List[float]:
        if not self._openai_client:
            raise ValueError("OpenAI client not configured")
        response = self._openai_client.embeddings.create(input=text, model=self._embedding_model)
        return response.data[0].embedding

    def generate_embeddings(self, path: Path) -> List[List[float]]:
        """Generate embeddings for the full dataset by chunking."""
        if not self._openai_client:
            return []
        
        columns = []
        rows = []
        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                columns = next(reader, [])
                rows = list(reader)
        except UnicodeDecodeError:
            with path.open("r", encoding="latin-1", newline="") as handle:
                reader = csv.reader(handle)
                columns = next(reader, [])
                rows = list(reader)
        
        chunk_size = 100
        embeddings = []
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            text = f"Columns: {','.join(columns)}\n" + "\n".join("\t".join(row) for row in chunk)
            emb = self._embed_text(text)
            embeddings.append(emb)
        return embeddings

    def index(self, refresh: bool = False) -> None:
        """Index entire dataset directory."""
        if not self._dataset_root.exists():
            logger.warning("Pasta de datasets não encontrada: %s", self._dataset_root)
            return

        csv_files = sorted(self._dataset_root.glob("**/*.csv"))
        if not csv_files:
            logger.info("Nenhum CSV encontrado para Structured RAG em %s", self._dataset_root)
            return

        for csv_path in csv_files:
            dataset_id = csv_path.relative_to(self._dataset_root).as_posix()
            if not refresh and dataset_id in self._index:
                continue
            index_entry = self._extract_sample(csv_path)
            if self._enable_embeddings:
                embeddings = self.generate_embeddings(csv_path)
                index_entry.embeddings = embeddings
            self._index[dataset_id] = index_entry
            entity_id = f"{self._namespace}:{dataset_id}"
            self._state_store.save_state(entity_id, index_entry.to_dict(), metadata={"namespace": self._namespace})

        aggregated = {
            "namespace": self._namespace,
            "datasets": [entry.to_dict() for entry in self._index.values()],
            "generated_at": time(),
        }
        self._state_store.save_state(f"{self._namespace}:structured_rag_index", aggregated, metadata={"namespace": self._namespace})
        logger.info("Structured RAG index atualizado (%s datasets)", len(self._index))

    def get_dataset(self, dataset_id: str) -> Optional[StructuredRAGIndex]:
        if dataset_id in self._index:
            return self._index[dataset_id]
        stored = self._state_store.load_state(f"{self._namespace}:{dataset_id}")
        if stored:
            return StructuredRAGIndex(
                dataset_id=stored["dataset_id"],
                path=stored["path"],
                checksum=stored["checksum"],
                columns=stored.get("columns", []),
                sample_rows=stored.get("sample_rows", []),
                metadata=stored.get("metadata", {}),
                embeddings=stored.get("embeddings", []),
            )
        return None

    def query(self, text: str, limit: int = 5) -> List[StructuredRAGIndex]:
        """Perform simple keyword search on dataset metadata."""
        text_lower = text.lower()
        matches: List[StructuredRAGIndex] = []
        for entry in self._index.values():
            if text_lower in entry.dataset_id.lower() or any(
                text_lower in column.lower() for column in entry.columns
            ):
                matches.append(entry)
        matches.sort(key=lambda item: item.dataset_id)
        return matches[:limit]

    def semantic_query(self, text: str, limit: int = 5) -> List[StructuredRAGIndex]:
        """Perform semantic search using cosine similarity on embeddings."""
        if not self._enable_embeddings or not self._openai_client:
            return []
        
        query_emb = self._embed_text(text)
        similarities = []
        for entry in self._index.values():
            for emb in entry.embeddings:
                sim = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
                similarities.append((sim, entry))
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in similarities[:limit]]

    def export_index(self) -> Dict[str, Any]:
        """Return the Structured RAG index as plain dictionary."""
        return {
            dataset_id: entry.to_dict()
            for dataset_id, entry in self._index.items()
        }
