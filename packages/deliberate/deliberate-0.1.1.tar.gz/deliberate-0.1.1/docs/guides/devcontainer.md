# Dev Container Support

Deliberate can run validation commands (tests, linters) inside Dev Containers, providing isolation from the host system and consistent execution environments.

## Why Use Dev Containers?

Without isolation, agents can generate code that:
- Runs malicious scripts during test execution
- Modifies or deletes files outside the project
- Installs unwanted packages on your system

Dev Containers solve this by running commands in a Docker container with:
- Isolated filesystem (only the workspace is mounted)
- Controlled environment (reproducible dependencies)
- No access to host system outside the workspace

## Quick Start

1. Add a `.devcontainer/devcontainer.json` to your project:

```json
{
    "name": "My Project Dev",
    "image": "python:3.11",
    "postCreateCommand": "pip install -r requirements.txt"
}
```

2. Enable Dev Container validation in `.deliberate.yaml`:

```yaml
workflow:
  execution:
    validation:
      enabled: true
      command: "pytest"
      devcontainer:
        enabled: true
        auto_detect: true
```

3. Run deliberate as usual. Validation commands will execute inside the container.

## Configuration

### DevContainerConfig Options

```yaml
workflow:
  execution:
    validation:
      devcontainer:
        enabled: false        # Enable/disable Dev Container execution
        auto_detect: true     # Auto-detect .devcontainer/devcontainer.json
        use_devcontainer_cli: true  # Prefer devcontainer CLI over docker exec
        startup_timeout_seconds: 300  # Container startup timeout
        keep_running: true    # Keep container running between executions
```

### Supported Configurations

Deliberate detects devcontainer configurations in order of priority:

1. `.devcontainer/devcontainer.json` (standard location)
2. `.devcontainer.json` (root level)

Supported devcontainer types:
- **Image-based**: Uses a pre-built Docker image
- **Dockerfile-based**: Builds from a Dockerfile (requires devcontainer CLI)
- **Docker Compose**: Uses docker-compose (requires devcontainer CLI)

## Execution Modes

### With devcontainer CLI (Recommended)

If you have the [devcontainer CLI](https://github.com/devcontainers/cli) installed:

```bash
npm install -g @devcontainers/cli
```

Deliberate uses `devcontainer up` and `devcontainer exec` for full feature support including:
- Dockerfile builds
- Docker Compose setups
- Dev Container features
- Post-create commands

### Docker Fallback

When the devcontainer CLI is not available but Docker is, Deliberate uses a simpler fallback:

1. Pulls the image specified in `devcontainer.json`
2. Runs a container with the workspace mounted at `/workspace`
3. Executes commands via `docker exec`

Limitations:
- Only works with image-based devcontainers
- Does not run postCreateCommand or install features
- Container naming: `deliberate-{workspace-name}`

## Container Lifecycle

Containers are:
- Started on first validation command
- Reused for subsequent commands in the same session
- Named `deliberate-{workspace-name}` for easy identification

To manually clean up:

```bash
docker stop deliberate-myproject
docker rm deliberate-myproject
```

## Example: Python Project

```json
// .devcontainer/devcontainer.json
{
    "name": "Python Dev",
    "image": "python:3.11",
    "customizations": {
        "vscode": {
            "extensions": ["ms-python.python"]
        }
    },
    "postCreateCommand": "pip install -e .[dev]"
}
```

```yaml
# .deliberate.yaml
workflow:
  execution:
    validation:
      enabled: true
      command: "pytest tests/"
      devcontainer:
        enabled: true
```

## Example: Node.js Project

```json
// .devcontainer/devcontainer.json
{
    "name": "Node Dev",
    "image": "node:18",
    "postCreateCommand": "npm install"
}
```

```yaml
# .deliberate.yaml
workflow:
  execution:
    validation:
      enabled: true
      command: "npm test"
      devcontainer:
        enabled: true
```

## Troubleshooting

### "Failed to start Dev Container"

Check if Docker is running:
```bash
docker ps
```

For image-based containers, verify the image exists:
```bash
docker pull python:3.11
```

### Container Reuse

If you need a fresh container:
```bash
docker rm -f deliberate-myproject
```

### Logs

Enable verbose logging to see container operations:
```bash
deliberate run "@task.txt" -v
```

Look for lines like:
```
INFO:deliberate.validation.devcontainer:Started new container: deliberate-myproject
INFO:deliberate.validation.devcontainer:Using existing container: deliberate-myproject
```
