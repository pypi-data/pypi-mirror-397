"""Data models for SDK."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class Model(BaseModel):
    """Model metadata."""
    id: str
    name: str
    storage_path: str
    repository: Optional[str] = None
    company: Optional[str] = None
    base_model: Optional[str] = None
    parameter_count: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class Release(BaseModel):
    """Release model."""
    id: str
    model_id: str
    version: str
    tag: str
    digest: str
    size_bytes: Optional[int] = None
    platform: str = "linux/amd64"
    architecture: str = "amd64"
    os: str = "linux"
    quantization: Optional[str] = None
    release_notes: Optional[str] = None
    metadata: Dict[str, Any] = {}
    ceph_path: Optional[str] = None
    status: str = "active"
    created_at: datetime


class Deployment(BaseModel):
    """Deployment model."""
    id: str
    release_id: str
    environment: str
    deployed_by: Optional[str] = None
    deployed_at: datetime
    status: str = "success"
    metadata: Dict[str, Any] = {}


class ApiKey(BaseModel):
    """API Key model."""
    id: str
    name: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    key: Optional[str] = None  # Only present when creating
