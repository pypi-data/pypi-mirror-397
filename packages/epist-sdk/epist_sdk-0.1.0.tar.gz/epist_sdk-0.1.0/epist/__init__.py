import os
from typing import Any

import httpx


class Epist:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://epist-api-prod-920152096400.us-central1.run.app/api/v1",
    ):
        self.api_key = api_key or os.getenv("EPIST_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is required. Pass it to the constructor or set EPIST_API_KEY env var.")
        self.base_url = base_url.rstrip("/")
        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
        self.client = httpx.Client(headers=self.headers, timeout=60.0)

    def upload_file(self, file_path: str) -> dict[str, Any]:
        """Upload a local audio file."""
        url = f"{self.base_url}/audio/upload"
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            # Remove Content-Type header for multipart upload so httpx sets boundary
            headers = self.headers.copy()
            headers.pop("Content-Type")
            response = self.client.post(url, files=files, headers=headers)
            response.raise_for_status()
            return response.json()

    def transcribe_url(self, url: str, rag_enabled: bool = True, language: str = "en") -> dict[str, Any]:
        """Transcribe audio from a URL."""
        endpoint = f"{self.base_url}/audio/transcribe_url"
        payload = {"audio_url": url, "rag_enabled": rag_enabled, "language": language}
        response = self.client.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()

    def get_status(self, audio_id: str) -> dict[str, Any]:
        """Get status of an audio task."""
        endpoint = f"{self.base_url}/audio/{audio_id}"
        response = self.client.get(endpoint)
        response.raise_for_status()
        return response.json()

    def get_transcript(self, audio_id: str) -> dict[str, Any]:
        """Get the full transcript."""
        endpoint = f"{self.base_url}/audio/{audio_id}/transcript"
        response = self.client.get(endpoint)
        response.raise_for_status()
        return response.json()

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search the knowledge base."""
        endpoint = f"{self.base_url}/search/"
        payload = {"query": query, "limit": limit}
        response = self.client.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
