# Run with: bash .init/.linter.sh

# Use system-installed flake8
# Set the absolute path
WORKSPACE_DIR="/home/kavia/workspace/code-generation/employee-knowledge-hub-73744"
cd "$WORKSPACE_DIR/scribbly_backend" && flake8 src/
