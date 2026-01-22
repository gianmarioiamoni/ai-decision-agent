#!/bin/bash
# Script to run the Gradio UI with the correct conda environment

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    # Load .env and handle quotes properly
    set -a
    source .env
    set +a
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY environment variable is not set!"
    echo "Please set it with: export OPENAI_API_KEY='your-api-key-here'"
    echo "Or add it to your .env file"
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ OPENAI_API_KEY loaded successfully"
fi

echo "🚀 Starting AI Decision Agent Gradio UI..."
echo "📡 Server will be available at: http://localhost:${GRADIO_SERVER_PORT:-7860}"
echo "🔗 A public sharing link will be generated (if share=True)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Activate conda environment and run the app
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate ai_decision_agent

# Run the app (logs will appear in real-time)
python -m app.ui.app_real

