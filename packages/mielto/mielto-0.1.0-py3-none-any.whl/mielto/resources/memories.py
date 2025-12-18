"""Memory resource for interacting with the Mielto Memory API."""

from typing import List, Optional, Union

from mielto.client.base import AsyncBaseClient, BaseClient
from mielto.types.memory import (
    Memory,
    MemoryCreate,
    MemoryListResponse,
    MemoryReplace,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryUpdate,
)


class Memories:
    """Synchronous Memory resource."""

    def __init__(self, client: BaseClient):
        """Initialize the Memory resource.

        Args:
            client: Base HTTP client instance
        """
        self._client = client

    def create(self, memory_data: Union[MemoryCreate, dict]) -> Memory:
        """Create a new memory.

        Args:
            memory_data: Memory data to create

        Returns:
            Created memory

        Example:
            ```python
            memory = client.memories.create(
                MemoryCreate(
                    user_id="user_123",
                    memory="User prefers dark mode",
                    topics=["preferences", "ui"]
                )
            )
            ```
        """
        if isinstance(memory_data, MemoryCreate):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        response = self._client.post("/memories", json_data=payload)
        return Memory(**response["memory"])

    def get(self, memory_id: str, user_id: Optional[str] = None) -> Memory:
        """Get a specific memory by ID.

        Args:
            memory_id: Memory ID
            user_id: Optional user ID filter

        Returns:
            Memory object

        Example:
            ```python
            memory = client.memories.get("mem_123")
            ```
        """
        params = {}
        if user_id:
            params["user_id"] = user_id

        response = self._client.get(f"/memories/{memory_id}", params=params)
        return Memory(**response)

    def list(
        self,
        user_id: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: int = 50,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> MemoryListResponse:
        """List memories with pagination.

        Args:
            user_id: Optional user ID to filter memories
            cursor: Cursor for pagination
            limit: Number of memories to return (1-100)
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            MemoryListResponse with memories and pagination info

        Example:
            ```python
            result = client.memories.list(user_id="user_123", limit=20)
            for memory in result.memories:
                print(memory.memory)

            # Get next page
            if result.has_more:
                next_page = client.memories.list(
                    user_id="user_123",
                    cursor=result.next_cursor
                )
            ```
        """
        params = {
            "limit": limit,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if user_id:
            params["user_id"] = user_id
        if cursor:
            params["cursor"] = cursor

        response = self._client.get("/memories", params=params)
        return MemoryListResponse(**response)

    def search(self, search_request: Union[MemorySearchRequest, dict]) -> MemorySearchResponse:
        """Search memories.

        Args:
            search_request: Search parameters

        Returns:
            MemorySearchResponse with matching memories

        Example:
            ```python
            results = client.memories.search(
                MemorySearchRequest(
                    query="dark mode preferences",
                    user_id="user_123",
                    limit=10
                )
            )
            for memory in results.memories:
                print(f"{memory.memory} (score: {memory.score})")
            ```
        """
        if isinstance(search_request, MemorySearchRequest):
            payload = search_request.model_dump(exclude_none=True)
        else:
            payload = search_request

        response = self._client.post("/memories/search", json_data=payload)
        return MemorySearchResponse(**response)

    def update(self, memory_id: str, memory_data: Union[MemoryUpdate, dict]) -> Memory:
        """Update an existing memory.

        Args:
            memory_id: Memory ID
            memory_data: Updated memory data

        Returns:
            Updated memory

        Example:
            ```python
            updated = client.memories.update(
                "mem_123",
                MemoryUpdate(
                    memory="User prefers light mode now",
                    topics=["preferences", "ui", "updated"]
                )
            )
            ```
        """
        if isinstance(memory_data, MemoryUpdate):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        response = self._client.put(f"/memories/{memory_id}", json_data=payload)
        return Memory(**response["memory"])

    def replace(self, memory_id: str, memory_data: Union[MemoryReplace, dict]) -> dict:
        """Replace an existing memory completely.

        Args:
            memory_id: Memory ID
            memory_data: New memory data

        Returns:
            Dict with old and new memory

        Example:
            ```python
            result = client.memories.replace(
                "mem_123",
                MemoryReplace(
                    memory="Completely new memory content",
                    topics=["new"]
                )
            )
            ```
        """
        if isinstance(memory_data, MemoryReplace):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        return self._client.post(f"/memories/{memory_id}/replace", json_data=payload)

    def delete(self, memory_id: str, user_id: Optional[str] = None) -> dict:
        """Delete a memory.

        Args:
            memory_id: Memory ID
            user_id: Optional user ID

        Returns:
            Deletion confirmation

        Example:
            ```python
            result = client.memories.delete("mem_123")
            print(result["message"])
            ```
        """
        params = {}
        if user_id:
            params["user_id"] = user_id

        endpoint = f"/memories/{memory_id}"
        if params:
            from urllib.parse import urlencode

            endpoint += f"?{urlencode(params)}"

        return self._client.delete(endpoint)

    def from_messages(
        self,
        messages: List[dict],
        user_id: str,
        topics: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> List[Memory]:
        """Generate memories from a list of messages.

        This is a convenience method that processes messages and creates memories.

        Args:
            messages: List of message objects with 'role' and 'content' keys
            user_id: User ID to associate with the memories
            topics: Optional topics to tag the memories with
            metadata: Optional metadata to attach

        Returns:
            List of created memories

        Example:
            ```python
            messages = [
                {"role": "user", "content": "I prefer dark mode"},
                {"role": "assistant", "content": "I'll remember that"},
                {"role": "user", "content": "I work in tech"}
            ]
            memories = client.memories.from_messages(
                messages=messages,
                user_id="user_123",
                topics=["preferences", "background"]
            )
            ```
        """
        created_memories = []

        for msg in messages:
            # Extract relevant content based on message structure
            content = msg.get("content", "")
            role = msg.get("role", "user")

            # Skip empty messages or system messages
            if not content or role == "system":
                continue

            # Create memory from message
            memory_data = MemoryCreate(
                user_id=user_id,
                memory=content,
                topics=topics,
                metadata={
                    **(metadata or {}),
                    "source": "messages",
                    "role": role,
                },
            )

            try:
                memory = self.create(memory_data)
                created_memories.append(memory)
            except Exception as e:
                # Log error but continue processing
                print(f"Failed to create memory from message: {e}")
                continue

        return created_memories


class AsyncMemories:
    """Asynchronous Memory resource."""

    def __init__(self, client: AsyncBaseClient):
        """Initialize the async Memory resource.

        Args:
            client: Async base HTTP client instance
        """
        self._client = client

    async def create(self, memory_data: Union[MemoryCreate, dict]) -> Memory:
        """Create a new memory asynchronously."""
        if isinstance(memory_data, MemoryCreate):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        response = await self._client.post("/memories", json_data=payload)
        return Memory(**response["memory"])

    async def get(self, memory_id: str, user_id: Optional[str] = None) -> Memory:
        """Get a specific memory by ID asynchronously."""
        params = {}
        if user_id:
            params["user_id"] = user_id

        response = await self._client.get(f"/memories/{memory_id}", params=params)
        return Memory(**response)

    async def list(
        self,
        user_id: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: int = 50,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> MemoryListResponse:
        """List memories with pagination asynchronously."""
        params = {
            "limit": limit,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if user_id:
            params["user_id"] = user_id
        if cursor:
            params["cursor"] = cursor

        response = await self._client.get("/memories", params=params)
        return MemoryListResponse(**response)

    async def search(self, search_request: Union[MemorySearchRequest, dict]) -> MemorySearchResponse:
        """Search memories asynchronously."""
        if isinstance(search_request, MemorySearchRequest):
            payload = search_request.model_dump(exclude_none=True)
        else:
            payload = search_request

        response = await self._client.post("/memories/search", json_data=payload)
        return MemorySearchResponse(**response)

    async def update(self, memory_id: str, memory_data: Union[MemoryUpdate, dict]) -> Memory:
        """Update an existing memory asynchronously."""
        if isinstance(memory_data, MemoryUpdate):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        response = await self._client.put(f"/memories/{memory_id}", json_data=payload)
        return Memory(**response["memory"])

    async def replace(self, memory_id: str, memory_data: Union[MemoryReplace, dict]) -> dict:
        """Replace an existing memory completely asynchronously."""
        if isinstance(memory_data, MemoryReplace):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        return await self._client.post(f"/memories/{memory_id}/replace", json_data=payload)

    async def delete(self, memory_id: str, user_id: Optional[str] = None) -> dict:
        """Delete a memory asynchronously."""
        params = {}
        if user_id:
            params["user_id"] = user_id

        endpoint = f"/memories/{memory_id}"
        if params:
            from urllib.parse import urlencode

            endpoint += f"?{urlencode(params)}"

        return await self._client.delete(endpoint)

    async def from_messages(
        self,
        messages: List[dict],
        user_id: str,
        topics: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> List[Memory]:
        """Generate memories from a list of messages asynchronously."""
        created_memories = []

        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "user")

            if not content or role == "system":
                continue

            memory_data = MemoryCreate(
                user_id=user_id,
                memory=content,
                topics=topics,
                metadata={
                    **(metadata or {}),
                    "source": "messages",
                    "role": role,
                },
            )

            try:
                memory = await self.create(memory_data)
                created_memories.append(memory)
            except Exception as e:
                print(f"Failed to create memory from message: {e}")
                continue

        return created_memories
