"""
StateStore - Armazenamento persistente de estado
Inspirado no SST state management
"""

from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
from enum import Enum
import json
import os
from pathlib import Path


class CloudStorageProvider(Enum):
    """Provedores de cloud storage suportados"""

    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"
    LOCAL = "local"  # Para desenvolvimento


class StateStore:
    """
    Store de estado persistente para agentes.

    Inspirado em SST state management:
    - State diffing
    - Versioning
    - Rollback capability
    - Cloud backup (S3, GCS, Azure)
    - Backup automático
    """

    def __init__(
        self,
        storage_backend: str = "memory",
        cloud_provider: Optional[str] = None,
        cloud_bucket: Optional[str] = None,
        cloud_prefix: str = "agent-states/",
        auto_backup: bool = False,
        backup_interval_hours: int = 24,
    ):
        self.storage_backend = storage_backend
        self.states: Dict[str, List[Dict[str, Any]]] = {}

        # Cloud backup configuration
        self.cloud_provider = cloud_provider
        self.cloud_bucket = cloud_bucket
        self.cloud_prefix = cloud_prefix
        self.auto_backup = auto_backup
        self.backup_interval_hours = backup_interval_hours
        self.last_backup: Optional[datetime] = None

        # Local backup path para desenvolvimento
        self.local_backup_path = Path("./backups/states")
        self.local_backup_path.mkdir(parents=True, exist_ok=True)

    def save_state(
        self,
        entity_id: str,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Salva estado de uma entidade"""
        version = len(self.states.get(entity_id, [])) + 1

        state_entry = {
            "version": version,
            "state": state,
            "metadata": metadata or {},
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

        if entity_id not in self.states:
            self.states[entity_id] = []

        self.states[entity_id].append(state_entry)

        return f"{entity_id}_v{version}"

    def load_state(
        self,
        entity_id: str,
        version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Carrega estado de uma entidade"""
        if entity_id not in self.states:
            return None

        states = self.states[entity_id]

        if version is None:
            # Retorna última versão
            return states[-1]["state"] if states else None
        else:
            # Retorna versão específica
            for entry in states:
                if entry["version"] == version:
                    return entry["state"]

        return None

    def diff_states(
        self,
        entity_id: str,
        version1: int,
        version2: int
    ) -> Dict[str, Any]:
        """Compara duas versões de estado"""
        state1 = self.load_state(entity_id, version1)
        state2 = self.load_state(entity_id, version2)

        if not state1 or not state2:
            return {"error": "Version not found"}

        # Diff simples (TODO: implementar diff profundo)
        return {
            "added": {k: v for k, v in state2.items() if k not in state1},
            "removed": {k: v for k, v in state1.items() if k not in state2},
            "modified": {
                k: {"old": state1[k], "new": state2[k]}
                for k in state1
                if k in state2 and state1[k] != state2[k]
            },
        }

    async def backup_to_cloud(self, entity_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Faz backup dos estados para cloud storage.

        Args:
            entity_id: ID específico da entidade (None = todas)

        Returns:
            Resultado do backup
        """
        result = {
            "success": False,
            "backed_up_entities": 0,
            "total_versions": 0,
            "errors": [],
        }

        try:
            entities_to_backup = [entity_id] if entity_id else list(self.states.keys())

            for entity in entities_to_backup:
                if entity in self.states:
                    versions = self.states[entity]
                    result["total_versions"] += len(versions)

                    # Backup para cloud
                    await self._upload_to_cloud(entity, versions)
                    result["backed_up_entities"] += 1

            result["success"] = True
            self.last_backup = datetime.now(timezone.utc)

        except Exception as e:
            result["errors"].append(str(e))

        return result

    async def restore_from_cloud(self, entity_id: str) -> Dict[str, Any]:
        """
        Restaura estado do cloud storage.

        Args:
            entity_id: ID da entidade para restaurar

        Returns:
            Resultado da restauração
        """
        result = {"success": False, "versions_restored": 0, "errors": []}

        try:
            # Download do cloud
            versions = await self._download_from_cloud(entity_id)

            if versions:
                self.states[entity_id] = versions
                result["versions_restored"] = len(versions)
                result["success"] = True

        except Exception as e:
            result["errors"].append(str(e))

        return result

    async def _upload_to_cloud(
        self, entity_id: str, versions: List[Dict[str, Any]]
    ) -> None:
        """Upload para cloud storage"""
        if not self.cloud_provider:
            # Fallback para local storage
            await self._upload_to_local(entity_id, versions)
            return

        if self.cloud_provider == CloudStorageProvider.S3.value:
            await self._upload_to_s3(entity_id, versions)
        elif self.cloud_provider == CloudStorageProvider.GCS.value:
            await self._upload_to_gcs(entity_id, versions)
        elif self.cloud_provider == CloudStorageProvider.AZURE.value:
            await self._upload_to_azure(entity_id, versions)
        else:
            await self._upload_to_local(entity_id, versions)

    async def _download_from_cloud(self, entity_id: str) -> List[Dict[str, Any]]:
        """Download do cloud storage"""
        if not self.cloud_provider:
            return await self._download_from_local(entity_id)

        if self.cloud_provider == CloudStorageProvider.S3.value:
            return await self._download_from_s3(entity_id)
        elif self.cloud_provider == CloudStorageProvider.GCS.value:
            return await self._download_from_gcs(entity_id)
        elif self.cloud_provider == CloudStorageProvider.AZURE.value:
            return await self._download_from_azure(entity_id)
        else:
            return await self._download_from_local(entity_id)

    async def _upload_to_local(
        self, entity_id: str, versions: List[Dict[str, Any]]
    ) -> None:
        """Upload para armazenamento local (desenvolvimento)"""
        backup_file = self.local_backup_path / f"{entity_id}.json"

        data = {
            "entity_id": entity_id,
            "versions": versions,
            "backed_up_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(backup_file, "w") as f:
            json.dump(data, f, indent=2)

    async def _download_from_local(self, entity_id: str) -> List[Dict[str, Any]]:
        """Download do armazenamento local"""
        backup_file = self.local_backup_path / f"{entity_id}.json"

        if backup_file.exists():
            with open(backup_file, "r") as f:
                data = json.load(f)
                return data.get("versions", [])

        return []

    async def _upload_to_s3(
        self, entity_id: str, versions: List[Dict[str, Any]]
    ) -> None:
        """Upload para AWS S3"""
        # TODO: Implementar integração real com boto3
        # Por enquanto, simula upload
        pass

    async def _download_from_s3(self, entity_id: str) -> List[Dict[str, Any]]:
        """Download do AWS S3"""
        # TODO: Implementar integração real com boto3
        return []

    async def _upload_to_gcs(
        self, entity_id: str, versions: List[Dict[str, Any]]
    ) -> None:
        """Upload para Google Cloud Storage"""
        # TODO: Implementar integração real com google-cloud-storage
        pass

    async def _download_from_gcs(self, entity_id: str) -> List[Dict[str, Any]]:
        """Download do Google Cloud Storage"""
        # TODO: Implementar integração real com google-cloud-storage
        return []

    async def _upload_to_azure(
        self, entity_id: str, versions: List[Dict[str, Any]]
    ) -> None:
        """Upload para Azure Blob Storage"""
        # TODO: Implementar integração real com azure-storage-blob
        pass

    async def _download_from_azure(self, entity_id: str) -> List[Dict[str, Any]]:
        """Download do Azure Blob Storage"""
        # TODO: Implementar integração real com azure-storage-blob
        return []

    def should_backup(self) -> bool:
        """Verifica se deve fazer backup automático"""
        if not self.auto_backup:
            return False

        if not self.last_backup:
            return True

        time_since_backup = datetime.now(timezone.utc) - self.last_backup
        return time_since_backup.total_seconds() > (self.backup_interval_hours * 3600)

    async def auto_backup_if_needed(self) -> Optional[Dict[str, Any]]:
        """Executa backup automático se necessário"""
        if self.should_backup():
            return await self.backup_to_cloud()
        return None

    def get_backup_status(self) -> Dict[str, Any]:
        """Retorna status do backup"""
        return {
            "cloud_provider": self.cloud_provider,
            "cloud_bucket": self.cloud_bucket,
            "auto_backup_enabled": self.auto_backup,
            "backup_interval_hours": self.backup_interval_hours,
            "last_backup": self.last_backup.isoformat() if self.last_backup else None,
            "should_backup": self.should_backup(),
            "entities_count": len(self.states),
            "total_versions": sum(len(versions) for versions in self.states.values()),
        }
