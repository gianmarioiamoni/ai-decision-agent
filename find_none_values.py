#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("OPENAI_API_KEY", "dummy-key-for-debug")

import gradio as gr

def find_none_values(blocks):
    """Find all components with value=None that should have explicit values."""
    
    issues = []
    
    def scan(comp, path="root"):
        comp_type = comp.__class__.__name__
        value = getattr(comp, "value", "NO_VALUE_ATTR")
        label = getattr(comp, "label", None)
        
        # Components that SHOULD have explicit non-None values
        problematic_types = ["Textbox", "HTML", "File", "JSON", "Dropdown", "Radio"]
        
        if comp_type in problematic_types and value is None:
            issues.append({
                "path": path,
                "type": comp_type,
                "label": label,
                "value": value
            })
            print(f"⚠️  {comp_type} with value=None at: {path}")
            print(f"   Label: {label}")
            print()
        
        # Recursive scan
        if hasattr(comp, "children") and comp.children:
            for i, child in enumerate(comp.children):
                scan(child, f"{path}.children[{i}]")
    
    for i, child in enumerate(blocks.children):
        scan(child, f"root.children[{i}]")
    
    return issues

# Create the real demo
from app.ui.app_real import launch_real_ui

print("Creating Gradio app...")
print("="*70)

# We need to intercept the demo creation
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
    
    # Render all tabs structure
    with gr.Tabs():
        with gr.Tab("📊 Planning & Analysis"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📋 Step-by-Step Plan")
                    plan_output.render()
                with gr.Column(scale=1):
                    gr.Markdown("### 🔍 Analysis")
                    analysis_output.render()

        with gr.Tab("✅ Decision"):
            gr.Markdown("### 🎯 Final Decision")
            with gr.Row():
                with gr.Column(scale=3):
                    decision_output.render()
                with gr.Column(scale=1):
                    confidence_output.render()

        with gr.Tab("💬 Messages"):
            gr.Markdown("### 💬 Conversation History")
            messages_output.render()

        with gr.Tab("📄 Report"):
            with gr.Row():
                create_report_preview_section(report_output)
                create_report_download_section(format_selector, report_download_output)

        with gr.Tab("📜 Historical Decisions"):
            historical_output.render()

        with gr.Tab("📚 RAG Context & Evidence"):
            rag_evidence_output.render()

print("\n" + "="*70)
print("SCANNING FOR COMPONENTS WITH value=None...")
print("="*70 + "\n")

issues = find_none_values(demo)

print("="*70)
print(f"SUMMARY: Found {len(issues)} components with value=None")
print("="*70)

if issues:
    print("\nComponents to fix:")
    for issue in issues:
        print(f"  - {issue['type']} at {issue['path']}")
        print(f"    Label: {issue['label']}")
else:
    print("\n✅ All components have explicit values!")

