#!/bin/bash
# Run AI Decision Agent Tests
# This script activates the conda environment, loads env vars, and runs pytest

# Activate conda environment
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate ai_decision_agent

# Load environment variables (required for OpenAI API)
set -a
source .env
set +a

# Run all tests
echo "🧪 Running AI Decision Agent Test Suite..."
echo "==========================================="
python -m pytest tests/ -v --tb=short "$@"

