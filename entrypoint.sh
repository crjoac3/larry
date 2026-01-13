#!/bin/bash
set -e

echo "🐳 Starting Entrypoint Script..."

# 1. Update Code from GitHub (if .git exists)
if [ -d ".git" ]; then
    echo "🔄 Checking for updates from GitHub..."
    git fetch origin
    git reset --hard origin/main || echo "⚠️ Git update failed."
else
    echo "⚠️ No .git directory found. Skipping auto-update."
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
