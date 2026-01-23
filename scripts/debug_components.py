#!/usr/bin/env python3
"""
Debug script to inspect all Gradio components and find problematic values.
Run with: python debug_components.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set dummy environment variable to avoid errors
os.environ.setdefault("OPENAI_API_KEY", "dummy-key-for-debug")

import gradio as gr
from app.ui.app_real import launch_real_ui

def debug_component(comp, depth=0):
    """Recursively debug a component and its properties."""
    indent = "  " * depth
    print(f"{indent}Component: {comp.__class__.__name__}")
    
    # Check value
    if hasattr(comp, "value"):
        val = comp.value
        print(f"{indent}  value: {repr(val)} (type: {type(val).__name__})")
        # Flag if value is boolean
        if isinstance(val, bool):
            print(f"{indent}  ⚠️  WARNING: Boolean value found!")
    
    # Check label
    if hasattr(comp, "label"):
        lab = comp.label
        print(f"{indent}  label: {repr(lab)} (type: {type(lab).__name__})")
        if isinstance(lab, bool):
            print(f"{indent}  ⚠️  WARNING: Boolean label found!")
    
    # Check choices (for Radio, Dropdown, etc.)
    if hasattr(comp, "choices"):
        choices = comp.choices
        print(f"{indent}  choices: {repr(choices)} (type: {type(choices).__name__})")
        if isinstance(choices, bool):
            print(f"{indent}  ⚠️  WARNING: Boolean choices found!")
    
    # Check other attributes
    for attr in ["default", "placeholder", "info"]:
        if hasattr(comp, attr):
            val = getattr(comp, attr)
            if val is not None and isinstance(val, bool):
                print(f"{indent}  {attr}: {repr(val)} (type: {type(val).__name__})")
                print(f"{indent}  ⚠️  WARNING: Boolean {attr} found!")


def debug_blocks(blocks):
    """Debug all components in a Blocks."""
    print("\n" + "="*70)
    print("GRADIO COMPONENTS DEBUG")
    print("="*70 + "\n")
    
    # Get all blocks
    all_blocks = []
    
    def collect_blocks(block):
        all_blocks.append(block)
        if hasattr(block, "children"):
            for child in block.children:
                collect_blocks(child)
    
    collect_blocks(blocks)
    
    print(f"Total components found: {len(all_blocks)}\n")
    
    for i, comp in enumerate(all_blocks):
        print(f"\n[{i}] ", end="")
        debug_component(comp)
    
    print("\n" + "="*70)
    print("END DEBUG")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("Creating Gradio app...")
    
    # Import the demo creation
    from app.ui.app_real import (
        create_header, create_input_section, create_output_plan,
        create_output_analysis, create_output_decision, create_output_messages,
        create_output_report, create_report_preview_section, 
        create_report_download_section
    )
    
    # Colors (hardcoded from app_real.py)
    TITLE_COLOR = "#ffffff"
    SUBTITLE_COLOR = "#a0aec0"
    
    # Recreate the demo structure (simplified)
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
    
    # Debug all components
    debug_blocks(demo)
    
    print("\n✅ Debug complete! Check output above for ⚠️  WARNING messages.")
    print("If you see any boolean values where they shouldn't be, that's the problem!")

