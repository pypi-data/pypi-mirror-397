"""Main Registry client."""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx

from .models import Model, Release, Deployment, ApiKey


class RegistryError(Exception):
    """Base exception for registry errors."""
    pass


class Registry:
    """Docker Release Registry client."""

    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize Registry client.

        Args:
            base_url: Base URL of the registry API
            api_key: API key for authentication
        """
        self.base_url = base_url or os.getenv("REGISTRY_URL", "http://localhost/api")
        self.api_key = api_key or os.getenv("REGISTRY_API_KEY")

        if not self.api_key:
            raise RegistryError("API key is required. Set REGISTRY_API_KEY environment variable or pass api_key parameter.")

        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": self.api_key},
            timeout=30.0,
        )

    @classmethod
    def from_env(cls) -> "Registry":
        """Create Registry client from environment variables."""
        return cls()

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise errors if needed."""
        if response.status_code >= 400:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except:
                error_detail = response.text

            raise RegistryError(f"API error ({response.status_code}): {error_detail}")

        return response.json()

    # ============================================================================
    # Models
    # ============================================================================

    def create_model(
        self,
        name: str,
        storage_path: str,
        repository: str = None,
        description: str = None,
        company: str = None,
        base_model: str = None,
        parameter_count: str = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> Model:
        """
        Create a new model.

        Args:
            name: Model name
            storage_path: Storage path (e.g. s3://bucket/path)
            repository: Optional repository URL
            description: Optional description
            company: Optional company name
            base_model: Optional base model name
            parameter_count: Optional parameter count
            tags: Optional list of tags
            metadata: Optional metadata dict

        Returns:
            Created Model object
        """
        payload = {
            "name": name,
            "storage_path": storage_path,
            "description": description,
        }
        if repository:
            payload["repository"] = repository
        if company:
            payload["company"] = company
        if base_model:
            payload["base_model"] = base_model
        if parameter_count:
            payload["parameter_count"] = parameter_count
        if tags:
            payload["tags"] = tags
        if metadata:
            payload["metadata"] = metadata

        response = self.client.post(
            "/v1/models",
            json=payload,
        )
        data = self._handle_response(response)
        return Model(**data)

    def list_models(self, search: str = None, limit: int = 100, offset: int = 0) -> List[Model]:
        """
        List models.

        Args:
            search: Search term for model name
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of Model objects
        """
        params = {"limit": limit, "offset": offset}
        if search:
            params["search"] = search

        response = self.client.get("/v1/models", params=params)
        data = self._handle_response(response)
        return [Model(**item) for item in data]

    def get_model(self, model_id: str) -> Model:
        """Get model by ID."""
        response = self.client.get(f"/v1/models/{model_id}")
        data = self._handle_response(response)
        return Model(**data)

    def delete_model(self, model_id: str) -> None:
        """Delete model by ID."""
        response = self.client.delete(f"/v1/models/{model_id}")
        self._handle_response(response)

    # ============================================================================
    # Releases
    # ============================================================================

    def create_release(
        self,
        model_name: str,
        version: str,
        tag: str,
        digest: str,
        size_bytes: int = None,
        platform: str = "linux/amd64",
        quantization: str = None,
        release_notes: str = None,
        metadata: Dict[str, Any] = None,
        ceph_path: str = None,
    ) -> Release:
        """
        Create a new release.

        Args:
            model_name: Name of the model
            version: Version string
            tag: Docker tag
            digest: Image digest (sha256:...)
            size_bytes: Size in bytes
            platform: Platform (default: linux/amd64)
            quantization: Quantization level (e.g. fp16, int8)
            release_notes: Release notes
            metadata: Additional metadata
            ceph_path: Path on Ceph filesystem

        Returns:
            Created Release object
        """
        # Get or create model
        models = self.list_models(search=model_name)
        model = next((m for m in models if m.name == model_name), None)

        if not model:
            raise RegistryError(f"Model '{model_name}' not found. Create it first with create_model().")

        # Create release
        payload = {
            "model_id": model.id,
            "version": version,
            "tag": tag,
            "digest": digest,
            "size_bytes": size_bytes,
            "platform": platform,
            "metadata": metadata or {},
            "ceph_path": ceph_path,
        }
        if quantization:
            payload["quantization"] = quantization
        if release_notes:
            payload["release_notes"] = release_notes

        response = self.client.post(
            "/v1/releases",
            json=payload,
        )
        data = self._handle_response(response)
        return Release(**data)

    def list_releases(
        self,
        image_name: str = None,
        version: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Release]:
        """
        List releases.

        Args:
            image_name: Filter by image name
            version: Filter by version
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of Release objects
        """
        params = {"limit": limit, "offset": offset}
        if image_name:
            params["image_name"] = image_name
        if version:
            params["version"] = version

        response = self.client.get("/v1/releases", params=params)
        data = self._handle_response(response)
        return [Release(**item) for item in data]

    def get_release(self, release_id: str) -> Release:
        """Get release by ID."""
        response = self.client.get(f"/v1/releases/{release_id}")
        data = self._handle_response(response)
        return Release(**data)

    def get_latest_release(
        self,
        image_name: str,
        environment: str = None,
    ) -> Optional[Release]:
        """
        Get latest release for an image.

        Args:
            image_name: Image name
            environment: Optional environment filter

        Returns:
            Latest Release object or None
        """
        params = {"model_name": image_name}
        if environment:
            params["environment"] = environment

        response = self.client.get("/v1/releases/latest", params=params)
        data = self._handle_response(response)
        return Release(**data) if data else None

    def delete_release(self, release_id: str) -> None:
        """Delete release by ID."""
        response = self.client.delete(f"/v1/releases/{release_id}")
        self._handle_response(response)

    # ============================================================================
    # Deployments
    # ============================================================================

    def deploy(
        self,
        release_id: str,
        environment: str,
        metadata: Dict[str, Any] = None,
        status: str = "success",
    ) -> Deployment:
        """
        Record a deployment.

        Args:
            release_id: ID of the release being deployed
            environment: Environment name (e.g., 'production', 'staging')
            metadata: Additional deployment metadata
            status: Deployment status (default: 'success')

        Returns:
            Created Deployment object
        """
        response = self.client.post(
            "/v1/deployments",
            json={
                "release_id": release_id,
                "environment": environment,
                "metadata": metadata or {},
                "status": status,
            },
        )
        data = self._handle_response(response)
        return Deployment(**data)

    def list_deployments(
        self,
        environment: str = None,
        release_id: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Deployment]:
        """
        List deployments.

        Args:
            environment: Filter by environment
            release_id: Filter by release ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of Deployment objects
        """
        params = {"limit": limit, "offset": offset}
        if environment:
            params["environment"] = environment
        if release_id:
            params["release_id"] = release_id

        response = self.client.get("/v1/deployments", params=params)
        data = self._handle_response(response)
        return [Deployment(**item) for item in data]

    def get_deployment(self, deployment_id: str) -> Deployment:
        """Get deployment by ID."""
        response = self.client.get(f"/v1/deployments/{deployment_id}")
        data = self._handle_response(response)
        return Deployment(**data)

    # ============================================================================
    # API Keys
    # ============================================================================

    def create_api_key(self, name: str, expires_at: datetime = None) -> ApiKey:
        """
        Create a new API key.

        Args:
            name: Name for the API key
            expires_at: Optional expiration date

        Returns:
            Created ApiKey object (includes plaintext key)
        """
        payload = {"name": name}
        if expires_at:
            payload["expires_at"] = expires_at.isoformat()

        response = self.client.post("/v1/api-keys", json=payload)
        data = self._handle_response(response)
        return ApiKey(**data)

    def list_api_keys(self) -> List[ApiKey]:
        """List all API keys."""
        response = self.client.get("/v1/api-keys")
        data = self._handle_response(response)
        return [ApiKey(**item) for item in data]

    def revoke_api_key(self, key_id: str) -> None:
        """Revoke an API key."""
        response = self.client.delete(f"/v1/api-keys/{key_id}")
        self._handle_response(response)

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
