#!/bin/bash
# File: aitube.sh
# Description: Unified entry point for AITube

# Stop on error
set -e

function show_help {
    echo "Usage: ./aitube.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev       Start in development mode (hot-reload, mounted volumes)"
    echo "  --prod      Start in production mode (immutable images)"
    echo "  --down      Stop all containers"
    echo "  --test      Run tests inside the container"
    echo "  --help      Show this help message"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running."
    exit 1
fi

MODE="prod"
COMPOSE_FILES="-f docker-compose.yml"

# Parse arguments
if [[ $# -eq 0 ]]; then
    show_help
    exit 0
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dev)
            MODE="dev"
            COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
            ;;
        --prod)
            MODE="prod"
            COMPOSE_FILES="-f docker-compose.yml"
            ;;
        --down)
            docker compose down
            exit 0
            ;;
        --test)
            # Run pytest inside a one-off container
            docker compose -f docker-compose.yml run --rm web uv run pytest
            exit 0
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown parameter passed: $1"
            show_help
            exit 1
            ;;
    esac
    shift
done

echo "🚀 Starting AITube in $MODE mode..."
echo "📂 Using compose files: $COMPOSE_FILES"

# Build and Up
docker compose $COMPOSE_FILES up --build -d

echo ""
echo "✅ System is up!"
if [ "$MODE" == "dev" ]; then
    echo "   Web App: http://localhost"
    echo "   API Docs: http://localhost/api/v1/docs"
    echo "   Logs: docker compose logs -f web worker"
fi