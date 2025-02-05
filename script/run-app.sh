#!/bin/bash
#
# AUTHOR:
# @chizo4 (Filip J. Cierkosz)
#
# INFO:
# The script runs the demo app pipeline for the task of "duo-student-finance".
#
# NOTE:
# The script includes the optimal pipeline configuration with the following setup:
# [task]          -> "duo-student-finance"
# [decision_tree] -> "yes"
# [model]         -> "deepseek-r1:8b"
# [temperature]   -> 0.8
#
# USAGE:
# bash script/run-app.sh
#
# EXAMPLE:
# bash script/run-app.sh

########################### CONFIGURATION & SETUP ###########################

# STEP 0: Specify args. Unlike "run-pipeline.sh", CLI args are not allowed.
TASK="duo-student-finance"
DECISION_TREE="yes"
MODEL="deepseek-r1:8b"
TEMPERATURE=0.8

########################### RUN PIPELINE ###########################

# STEP 3: Run the pipeline with the target LLM.
echo "***PROCESSING CASES FOR TASK: '$TASK'***"
echo "***SETUP: (A) LLM: '$MODEL'. (B) TEMPERATURE: '$TEMPERATURE'.***"; echo
python3 jus-tree-ai/app.py \
    --task "$TASK" \
    --decision_tree "$DECISION_TREE" \
    --model "$MODEL" \
    --temperature "$TEMPERATURE" \
