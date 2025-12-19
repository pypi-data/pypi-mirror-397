"""Dataset operations for Kytchen SDK."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

from .types import Dataset

if TYPE_CHECKING:
    from .client import KytchenClient


class Datasets:
    """Dataset management operations."""

    def __init__(self, client: KytchenClient) -> None:
        self._client = client

    async def create(
        self,
        name: str,
        file: str | Path | BinaryIO,
        *,
        content_type: str | None = None,
    ) -> Dataset:
        """Upload a new dataset.

        Args:
            name: Name for the dataset
            file: File path or file-like object to upload
            content_type: Optional MIME type (auto-detected if not provided)

        Returns:
            The created dataset
        """
        if isinstance(file, (str, Path)):
            path = Path(file)
            with open(path, "rb") as f:
                content = f.read()
            filename = path.name
            if content_type is None:
                content_type = self._guess_content_type(filename)
        else:
            content = file.read()
            filename = getattr(file, "name", "upload")
            if content_type is None:
                content_type = "application/octet-stream"

        files = {"file": (filename, content, content_type)}
        data = await self._client._request(
            "POST",
            "/v1/datasets",
            params={"name": name},
            files=files,
        )
        return self._parse_dataset(data)

    async def list(self) -> list[Dataset]:
        """List all datasets in the workspace.

        Returns:
            List of datasets
        """
        data = await self._client._request("GET", "/v1/datasets")
        return [self._parse_dataset(d) for d in data.get("datasets", [])]

    async def get(self, dataset_id: str) -> Dataset:
        """Get a specific dataset by ID.

        Args:
            dataset_id: The dataset ID

        Returns:
            The dataset
        """
        data = await self._client._request("GET", f"/v1/datasets/{dataset_id}")
        return self._parse_dataset(data)

    async def delete(self, dataset_id: str) -> None:
        """Delete a dataset.

        Args:
            dataset_id: The dataset ID to delete
        """
        await self._client._request("DELETE", f"/v1/datasets/{dataset_id}")

    def _parse_dataset(self, data: dict) -> Dataset:
        """Parse API response into Dataset object."""
        return Dataset(
            id=data["id"],
            name=data["name"],
            size_bytes=data["size_bytes"],
            content_hash=data["content_hash"],
            status=data["status"],
            created_at=data["created_at"],
            format=data.get("format"),
            processing_error=data.get("processing_error"),
        )

    def _guess_content_type(self, filename: str) -> str:
        """Guess content type from filename."""
        ext = Path(filename).suffix.lower()
        content_types = {
            ".txt": "text/plain",
            ".json": "application/json",
            ".csv": "text/csv",
            ".md": "text/markdown",
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        return content_types.get(ext, "application/octet-stream")
