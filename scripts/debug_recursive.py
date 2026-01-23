#!/usr/bin/env python3
"""
Recursive debug script to find components with boolean values in wrong places.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("OPENAI_API_KEY", "dummy-key-for-debug")

import gradio as gr

def debug_blocks_recursive(blocks: gr.Blocks):
    print("=== DEBUG COMPONENTI GRADIO ===")

    def scan_component(comp, path="root"):
        comp_type = comp.__class__.__name__
        label = getattr(comp, "label", None)
        value = getattr(comp, "value", None)
        
        # Segnala valori sospetti
        suspicious = ""
        if value is not None and isinstance(value, bool) and comp_type not in ["Checkbox", "CheckboxGroup"]:
            suspicious = " <-- ⚠️  POSSIBILE ERRORE BOOLEANO NON VALIDO"
        
        print(f"{path}: {comp_type}, label={label}, value={repr(value)} (type={type(value).__name__}){suspicious}")

        # Se il componente ha children, scansione ricorsiva
        if hasattr(comp, "children") and comp.children:
            for i, child in enumerate(comp.children):
                scan_component(child, path=f"{path}.{comp_type}[{i}]")

    for i, child in enumerate(blocks.children):
        scan_component(child, path=f"root[{i}]")

    print("=== FINE DEBUG ===")


# Create the real demo
from app.ui.app_real import (
    create_header, create_input_section, create_output_plan,
    create_output_analysis, create_output_decision, create_output_messages,
    create_output_report, create_report_preview_section, 
    create_report_download_section
)

TITLE_COLOR = "#ffffff"
SUBTITLE_COLOR = "#a0aec0"

plan_output = create_output_plan()
analysis_output = create_output_analysis()
decision_output, confidence_output = create_output_decision()
messages_output = create_output_messages()
report_output, format_selector, report_download_output = create_output_report()

historical_output = gr.HTML(value="", label="Similar Historical Decisions")
rag_evidence_output = gr.HTML(value="", label="RAG Context & Evidence")

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

# Run debug
debug_blocks_recursive(demo)

