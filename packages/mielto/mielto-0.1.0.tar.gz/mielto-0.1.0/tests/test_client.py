"""Tests for Mielto client."""

from unittest.mock import patch

from mielto import Mielto
from mielto.types import Memory, MemoryCreate


class TestMieltoClient:
    """Test cases for Mielto client."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = Mielto(api_key="test-key")
        assert client._client.api_key == "test-key"
        assert client.memories is not None
        assert client.collections is not None
        assert client.compress is not None
        client.close()

    def test_client_context_manager(self):
        """Test client as context manager."""
        with Mielto(api_key="test-key") as client:
            assert client._client.api_key == "test-key"

    @patch("mielto.client.base.BaseClient.post")
    def test_create_memory(self, mock_post):
        """Test creating a memory."""
        # Mock API response
        mock_post.return_value = {
            "memory": {
                "memory_id": "mem_123",
                "user_id": "user_123",
                "memory": "Test memory",
                "topics": ["test"],
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }

        with Mielto(api_key="test-key") as client:
            memory = client.memories.create(MemoryCreate(user_id="user_123", memory="Test memory", topics=["test"]))

            assert isinstance(memory, Memory)
            assert memory.memory_id == "mem_123"
            assert memory.memory == "Test memory"
            assert memory.user_id == "user_123"

    @patch("mielto.client.base.BaseClient.get")
    def test_list_memories(self, mock_get):
        """Test listing memories."""
        # Mock API response
        mock_get.return_value = {
            "memories": [
                {
                    "memory_id": "mem_123",
                    "user_id": "user_123",
                    "memory": "Test memory 1",
                    "topics": ["test"],
                }
            ],
            "total_count": 1,
            "next_cursor": None,
            "has_more": False,
        }

        with Mielto(api_key="test-key") as client:
            result = client.memories.list(user_id="user_123")

            assert result.total_count == 1
            assert len(result.memories) == 1
            assert result.memories[0].memory_id == "mem_123"
            assert not result.has_more
