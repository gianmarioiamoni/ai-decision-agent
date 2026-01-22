# app.py
# Entry point for Hugging Face Spaces deployment
# This file is specifically for HF Spaces - local development uses app/ui/app_real.py

import os
from app.ui.app_real import launch_real_ui

if __name__ == "__main__":
    # Launch the Gradio UI
    # HF Spaces will automatically detect and run this
    launch_real_ui()

