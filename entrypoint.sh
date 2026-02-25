#!/bin/bash
set -e

echo "🐳 Starting Entrypoint Script..."

# 1. Update Code from GitHub (Auto-init if missing)
# Fix for "dubious ownership" error in Docker (Exit 128)
git config --global --add safe.directory /app

if [ "$GIT_UPDATE" = "true" ]; then
    echo "🔄 Updating code from GitHub..."
    if [ -d ".git" ]; then
        git fetch origin
        git reset --hard origin/main || echo "⚠️ Git update failed."
    else
        echo "⚠️ No .git directory found. Auto-initializing..."
        git init
        git remote add origin https://github.com/crjoac3/larry.git
        git fetch origin
        git reset --hard origin/main || echo "⚠️ Initial git sync failed."
    fi
else
    echo "⏭️ GIT_UPDATE is not 'true'. Skipping GitHub sync."
fi

# 2. Data Migration / Initialization
# Define persistent data directory from Env Var or default to /data
DATA_DIR="${DATA_VOLUME:-/data}"

mkdir -p "$DATA_DIR"
echo "📂 Data Directory: $DATA_DIR"

# List of critical files to persist (initial copy if missing)
FILES=("users.csv" "companies.csv" "master_inventory.csv" "settings.json" "logo.jpg")

for file in "${FILES[@]}"; do
    if [ ! -f "$DATA_DIR/$file" ]; then
        if [ -f "/app/$file" ]; then
            echo "🆕 Initializing $file in persistent volume..."
            cp "/app/$file" "$DATA_DIR/$file"
        else
            echo "⚠️ Source $file not found in image, skipping initialization."
        fi
    else
        echo "✅ $file exists in persistent volume."
    fi
done

# 3. Start Streamlit
echo "🚀 Starting Streamlit..."
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0
