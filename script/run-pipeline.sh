#!/bin/bash
#
# AUTHOR:
# @chizo4 (Filip J. Cierkosz)
#
# INFO:
# The script runs the full-experiment pipeline for a specified task
# (e.g., DUO student finance).
#
# NOTE:
# (1) The currently implemented code only supports the duo-student-finance
# task, as the project is a proof-of-concept. Nonetheless, providing
# new [task] specific data makes it easy to run it on other (law-related) tasks.
# (2) The list of models in [model] is limited to models that were utilized
# in experiments. However, the experiments can be extended to any other models
# supported by OLLAMA (https://github.com/ollama/ollama/tree/main); provided
# they have appropriate token size and input format).
#
# USAGE:
# bash script/run-pipeline.sh [task] [model] [decision_tree] [temperature]
#
# OPTIONS:
# [task]          -> "duo-student-finance" (default: "duo-student-finance")
# [decision_tree] -> "yes"/"no" (default: "yes")
# [model]         -> "llama3.2", "qwen2.5:1.5b", "deepseek-r1:8b" (default: "llama3.2")
# [temperature]   -> values 0-1.0 (default: 0.5)

########################### CONFIGURATION & SETUP ###########################

# STEP 0: Fetch CLI args.
TASK=${1:-"duo-student-finance"}
DECISION_TREE=${2:-"yes"}
MODEL=${3:-"llama3.2"}
TEMPERATURE=${4:-0.5}

# STEP 1: Setup for input/output resources.
RESULTS_DIR="results/$TASK"
if [ ! -d "$RESULTS_DIR" ]; then
    mkdir -p "$RESULTS_DIR"
    echo "INFO: Created results directory: $RESULTS_DIR"; echo
fi
if [ ! -f "data/$TASK/cases.json" ]; then
    echo "ERROR: Input file '$INPUT_FILE' not found. EXIT!"; echo
    exit 1
fi
if [ "$DECISION_TREE" == "yes" ] && [ ! -f "data/$TASK/decision-tree.json" ]; then
    echo "ERROR: Decision tree file '$TREE_FILE' not found. EXIT!"; echo
    exit 1
fi

########################### RUN PIPELINE ###########################

# STEP 2: Run the pipeline with the target LLM.
echo "*PROCESSING CASES for '$TASK'...*"; echo
python3 jus-tree-ai/pipeline.py \
    --task "$TASK" \
    --decision_tree "$DECISION_TREE" \
    --model "$MODEL" \
    --temperature "$TEMPERATURE"
