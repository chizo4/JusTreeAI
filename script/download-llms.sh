#!/bin/bash
#
# AUTHOR:
# @chizo4 (Filip J. Cierkosz)
#
# INFO:
# This script downloads the project's LLMs via Ollama
#
# USAGE:
# bash script/download-llms.sh

# STEP 0: Ensure Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama is not installed - please download it first!"
    exit 1
fi

# STEP 1: Target models.
MODELS=(
    "llama3.2"
    "qwen2.5:1.5b"
    "deepseek-r1:8b"
    "openthinker:7b"
)

# STEP 2: Pull the models at checkpoints.
echo "Starting LLM downloads via Ollama..."; echo
for model in "${MODELS[@]}"; do
    echo "Pulling model: $model"
    ollama pull "$model"
done

echo; echo "SUCCESS: All models downloaded!"; echo