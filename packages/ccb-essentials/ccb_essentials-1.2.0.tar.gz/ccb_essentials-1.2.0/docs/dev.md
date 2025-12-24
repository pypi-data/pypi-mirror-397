# Package Maintenance

## Development Environment

First, [install uv](https://docs.astral.sh/uv/getting-started/installation/).

### Set up
    uv sync
    uv tree

## Maintenance

### Test code
    uv run pytest

#### Test with each Python version
    ./bin/test-all.sh

### Lint code
    uv run bin/lint.sh

### Build artifacts
    uv build

### Publish
    uv version --bump [major|minor|patch]
    V=v$(uv version --short) && git add pyproject.toml && git commit -m $V && git tag -a -m $V $V
    uv publish
