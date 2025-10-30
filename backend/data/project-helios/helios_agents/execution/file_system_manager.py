"""
FileSystemManager - Gerenciamento de arquivos e documentos
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime, timezone


class FileSystemManager:
    """
    Gerenciador de sistema de arquivos para documentos de homologação.
    
    Funcionalidades:
    - Upload/download de documentos
    - Versionamento
    - Validação de integridade
    - Organização por projeto
    """

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.file_registry: Dict[str, Dict[str, Any]] = {}

    def save_file(
        self,
        file_content: bytes,
        filename: str,
        project_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Salva arquivo no sistema"""
        file_id = f"{project_id}_{filename}_{datetime.now(timezone.utc).timestamp()}"

        file_path = self.base_path / project_id / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_bytes(file_content)

        self.file_registry[file_id] = {
            "path": str(file_path),
            "size": len(file_content),
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        return file_id

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Recupera informações do arquivo"""
        return self.file_registry.get(file_id)

    def list_files(self, project_id: str) -> List[Dict[str, Any]]:
        """Lista arquivos de um projeto"""
        return [
            info for file_id, info in self.file_registry.items()
            if file_id.startswith(project_id)
        ]
