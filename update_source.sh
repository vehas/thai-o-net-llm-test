#!/bin/bash

# Script to fetch a single file from an external GitHub repository
# and place it in the external/ directory (ignored by Git)

# Configuration: Set these variables to your specific repository and file
REMOTE_NAME="source_upstream"
UPSTREAM_REPO="https://github.com/ORIGINAL-OWNER/ORIGINAL-REPO.git"
SNAPSHOT_FILE_PATH="snapshot.jsonl.br"
SNAPSHOT_OUTPUT_FILE="external/snapshot.jsonl.br"
THAI_EXAM_PATH="thai_exam"
THAI_EXAM_OUTPUT_DIR="external/thai_exam"
OPEN_THAI_GPT_EVAL_PATH="openthaigpt_eval"
OPEN_THAI_GPT_EVAL_OUTPUT_DIR="external/openthaigpt_eval"

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

# Set up sparse checkout for the file and folder
echo "Configuring sparse checkout for $SNAPSHOT_FILE_PATH and $THAI_EXAM_PATH..."
git sparse-checkout init --cone || { echo "Error: Failed to initialize sparse checkout"; exit 1; }
git sparse-checkout set --skip-checks "$SNAPSHOT_FILE_PATH" "$THAI_EXAM_PATH" "$OPEN_THAI_GPT_EVAL_PATH" || { echo "Error: Failed to set sparse checkout"; exit 1; }

# Checkout the file and folder
echo "Checking out file: $SNAPSHOT_FILE_PATH and folder: $THAI_EXAM_PATH..."
git checkout "$REMOTE_NAME"/main -- "$SNAPSHOT_FILE_PATH" "$THAI_EXAM_PATH" "$OPEN_THAI_GPT_EVAL_PATH" || { echo "Error: Failed to checkout file or folder"; exit 1; }


# Move the file and folder to external/
echo "Moving file to $SNAPSHOT_OUTPUT_FILE..."
mkdir -p "$(dirname "$SNAPSHOT_OUTPUT_FILE")" || { echo "Error: Failed to create snapshot output directory"; exit 1; }
mv "$SNAPSHOT_FILE_PATH" "$SNAPSHOT_OUTPUT_FILE" || { echo "Error: Failed to move file to $SNAPSHOT_OUTPUT_FILE"; exit 1; }

echo "Moving folder to $THAI_EXAM_OUTPUT_DIR..."
mkdir -p "$(dirname "$THAI_EXAM_OUTPUT_DIR")" || { echo "Error: Failed to create thai_exam output directory"; exit 1; }
mv "$THAI_EXAM_PATH" "$THAI_EXAM_OUTPUT_DIR" || { echo "Error: Failed to move folder to $THAI_EXAM_OUTPUT_DIR"; exit 1; }

echo "Moving folder to $OPEN_THAI_GPT_EVAL_OUTPUT_DIR..."
mkdir -p "$(dirname "$OPEN_THAI_GPT_EVAL_OUTPUT_DIR")" || { echo "Error: Failed to create openthaigpt_eval output directory"; exit 1; }
mv "$OPEN_THAI_GPT_EVAL_PATH" "$OPEN_THAI_GPT_EVAL_OUTPUT_DIR" || { echo "Error: Failed to move folder to $OPEN_THAI_GPT_EVAL_OUTPUT_DIR"; exit 1; }



echo "Files updated successfully: $SNAPSHOT_OUTPUT_FILE and $THAI_EXAM_OUTPUT_DIR and $OPEN_THAI_GPT_EVAL_OUTPUT_DIR"
