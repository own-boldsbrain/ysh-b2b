"""
Testes unitários para FileSystemManager
"""

import pytest
from pathlib import Path
from helios_agents.execution.file_system_manager import FileSystemManager


class TestFileSystemManager:
    """Testes para FileSystemManager"""

    def test_initialization(self):
        """Testa inicialização do FileSystemManager"""
        manager = FileSystemManager("/tmp/test")

        assert manager.base_path == Path("/tmp/test")
        assert manager.file_registry == {}

    def test_save_file(self):
        """Testa salvamento de arquivo"""
        manager = FileSystemManager("/tmp/test")

        content = b"test content"
        filename = "test.txt"
        project_id = "proj_123"

        file_id = manager.save_file(content, filename, project_id)

        assert file_id.startswith("proj_123_test.txt_")
        assert file_id in manager.file_registry

        file_info = manager.file_registry[file_id]
        assert file_info["size"] == len(content)
        assert "created_at" in file_info
        assert file_info["metadata"] == {}

    def test_save_file_with_metadata(self):
        """Testa salvamento com metadados"""
        manager = FileSystemManager("/tmp/test")

        content = b"test content"
        filename = "test.txt"
        project_id = "proj_123"
        metadata = {"type": "document", "version": "1.0"}

        file_id = manager.save_file(content, filename, project_id, metadata)

        file_info = manager.file_registry[file_id]
        assert file_info["metadata"] == metadata

    def test_get_file(self):
        """Testa recuperação de arquivo"""
        manager = FileSystemManager("/tmp/test")

        # Salva arquivo
        file_id = manager.save_file(b"content", "test.txt", "proj_123")

        # Recupera
        file_info = manager.get_file(file_id)

        assert file_info is not None
        assert file_info["size"] == 7

    def test_get_nonexistent_file(self):
        """Testa recuperação de arquivo inexistente"""
        manager = FileSystemManager("/tmp/test")

        file_info = manager.get_file("nonexistent")

        assert file_info is None

    def test_list_files(self):
        """Testa listagem de arquivos por projeto"""
        manager = FileSystemManager("/tmp/test")

        # Salva múltiplos arquivos
        manager.save_file(b"content1", "file1.txt", "proj_123")
        manager.save_file(b"content2", "file2.txt", "proj_123")
        manager.save_file(b"content3", "file3.txt", "proj_456")

        files_proj_123 = manager.list_files("proj_123")
        files_proj_456 = manager.list_files("proj_456")

        assert len(files_proj_123) == 2
        assert len(files_proj_456) == 1

        # Verifica que todos os arquivos são do projeto correto
        for file_info in files_proj_123:
            assert "proj_123" in file_info["path"]
