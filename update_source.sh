#!/bin/bash

# Script to fetch a single file from an external GitHub repository
# and place it in the external/ directory (ignored by Git)

# Configuration: Set these variables to your specific repository and file
REMOTE_NAME="source_upstream"
UPSTREAM_REPO="https://github.com/dtinth/thaiexamjs.git"
FILE_PATH="snapshot.jsonl.br"
OUTPUT_FILE="external/snapshot.jsonl.br"

# Change to the repository root (where the script is located)
cd "$(dirname "$0")" || { echo "Error: Cannot change to repository directory"; exit 1; }

# Check if the remote exists; add it if it doesn't
if ! git remote | grep -q "$REMOTE_NAME"; then
    echo "Adding remote $REMOTE_NAME: $UPSTREAM_REPO"
    git remote add "$REMOTE_NAME" "$UPSTREAM_REPO" || {
        echo "Error: Failed to add remote $REMOTE_NAME"; exit 1;
    }
else
    echo "Remote $REMOTE_NAME already exists"
fi

# Fetch the latest data
echo "Fetching from $REMOTE_NAME..."
git fetch "$REMOTE_NAME" || { echo "Error: Failed to fetch from $REMOTE_NAME"; exit 1; }

# Set up sparse checkout for the specific file
echo "Configuring sparse checkout for $FILE_PATH..."
git sparse-checkout init --cone || { echo "Error: Failed to initialize sparse checkout"; exit 1; }
git sparse-checkout set --skip-checks "$FILE_PATH" || { echo "Error: Failed to set sparse checkout"; exit 1; }

# Checkout the file and move it to external/
echo "Checking out file: $FILE_PATH..."
git checkout "$REMOTE_NAME"/main -- "$FILE_PATH" || { echo "Error: Failed to checkout file"; exit 1; }
mkdir -p "$(dirname "$OUTPUT_FILE")" || { echo "Error: Failed to create output directory"; exit 1; }
mv "$FILE_PATH" "$OUTPUT_FILE" || { echo "Error: Failed to move file to $OUTPUT_FILE"; exit 1; }

echo "File updated successfully: $OUTPUT_FILE"
