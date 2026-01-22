#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set dummy environment variable
os.environ.setdefault("OPENAI_API_KEY", "dummy-key-for-debug")

import gradio as gr

def debug_blocks(blocks: gr.Blocks):
    print("=== COMPONENTI DI GRADIO ===")
    for i, comp in enumerate(blocks.children):
        print(f"{i}: {comp.__class__.__name__}")
        # Prova a stampare value o proprietà rilevanti
        if hasattr(comp, "value"):
            print(f"   value: {comp.value} (type: {type(comp.value)})")
        if hasattr(comp, "label"):
            print(f"   label: {comp.label} (type: {type(comp.label)})")
        if hasattr(comp, "choices"):
            print(f"   choices: {comp.choices} (type: {type(comp.choices)})")
    print("=== FINE COMPONENTI ===")

# Import and create the real demo
from app.ui.app_real import (
    create_header, create_input_section, create_output_plan,
    create_output_analysis, create_output_decision, create_output_messages,
    create_output_report, create_report_preview_section, 
    create_report_download_section
)

# Colors
TITLE_COLOR = "#ffffff"
SUBTITLE_COLOR = "#a0aec0"

# Recreate components
plan_output = create_output_plan()
analysis_output = create_output_analysis()
decision_output, confidence_output = create_output_decision()
messages_output = create_output_messages()
report_output, format_selector, report_download_output = create_output_report()

historical_output = gr.HTML(label="Similar Historical Decisions")
rag_evidence_output = gr.HTML(label="RAG Context & Evidence")

theme = gr.themes.Soft(
    primary_hue="violet",
    secondary_hue="purple",
    neutral_hue="slate",
    font=["Helvetica", "Arial", "sans-serif"]
)

with gr.Blocks(theme=theme) as demo:
    create_header(TITLE_COLOR, SUBTITLE_COLOR)
    
    (
        question_input,
        submit_button,
        rag_input,
        upload_status_output,
        storage_summary,
        files_list_display,
        refresh_files_btn,
        clear_files_btn,
        clear_status_display
    ) = create_input_section(SUBTITLE_COLOR)
    
    # Render all outputs
    plan_output.render()
    analysis_output.render()
    decision_output.render()
    confidence_output.render()
    messages_output.render()
    report_output.render()
    format_selector.render()
    report_download_output.render()
    historical_output.render()
    rag_evidence_output.render()

# Debug
debug_blocks(demo)

