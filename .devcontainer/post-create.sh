#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Setting up Arkiv Python Starter environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "🐳 Starting Docker daemon..."
sudo nohup dockerd > /tmp/dockerd.log 2>&1 &
# Wait for Docker to be ready
for i in {1..10}; do
    if docker info > /dev/null 2>&1; then
        echo "   Docker daemon is ready!"
        break
    fi
    echo "   Waiting for Docker daemon to start..."
    sleep 1
done

echo ""
echo "🐍 Installing Python and dependencies with uv..."
# Remove any existing .venv with wrong permissions
if [ -d ".venv" ]; then
    echo "   Cleaning up old virtual environment..."
    sudo rm -rf .venv
fi
uv sync

echo ""
echo "✅ Verifying installation..."
echo "   Python: $(python --version)"
echo "   UV: $(uv --version)"
echo "   Docker: $(docker --version)"
echo "   Arkiv SDK: $(uv run python -c 'import arkiv; print(arkiv.__version__)')"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Dev container is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Quick start commands:"
echo "  • python examples/01_basic_crud.py       # Run first example"
echo "  • python examples/02_queries.py          # Query entities"
echo "  • python examples/03_events.py           # Event listening"
echo "  • python examples/04_web3_integration.py # Web3 integration"
echo "  • uv run ipython                         # Interactive Python"
echo ""
