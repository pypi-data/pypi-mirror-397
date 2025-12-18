# BSO Python SDK

Python client library for the Docker Release Registry.

## Installation

```bash
pip install bso
```

## Quick Start

```python
from bso import Registry

# Initialize client
registry = Registry(
    base_url="http://localhost/api",
    api_key="your-api-key"
)

# Or use environment variables
# REGISTRY_URL=http://localhost/api
# REGISTRY_API_KEY=your-api-key
registry = Registry.from_env()

# Create a model
model = registry.create_model(
    name="myorg/pytorch-model",
    storage_path="s3://models/myorg/pytorch-model",
    description="My PyTorch model"
)

# Create a release
release = registry.create_release(
    model_name="myorg/pytorch-model",
    version="1.0.0",
    tag="v1.0.0",
    digest="sha256:abc123...",
    metadata={
        "pytorch_version": "2.1.0",
        "accuracy": 0.95,
        "git_commit": "abc123"
    }
)

# Record a deployment
deployment = registry.deploy(
    release_id=release.id,
    environment="production",
    metadata={"replicas": 3}
)

# Get latest release
latest = registry.get_latest_release(
    model_name="myorg/pytorch-model",
    environment="production"
)

print(f"Latest release: {latest.version}")
```

## API Reference

See the [documentation](https://docs.example.com) for complete API reference.

## License

MIT
