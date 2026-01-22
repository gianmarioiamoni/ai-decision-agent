# app/ui/app_real.py

# Professional Gradio UI for AI Decision Support Agent.
#
# SIMPLE EVENT-DRIVEN PATTERN:
# - No gr.State needed
# - Functions return values → Gradio updates components automatically
# - FileManager maintains backend state
# - Clean, predictable, enterprise-grade
#
# Architecture:
# - Components: UI widgets
# - Handlers: Return new values for components
# - FileManager: Backend state singleton
#
import gradio as gr

# Import UI components
from .components.header import create_header
from .components.input_section import create_input_section
from .components.output_plan import create_output_plan
from .components.output_analysis import create_output_analysis
from .components.output_decision import create_output_decision
from .components.output_messages import create_output_messages
from .components.output_report import create_output_report
from .components.report_preview_section import create_report_preview_section
from .components.report_download_section import create_report_download_section

# Import handlers
from .handlers.graph_handler_parallel import run_graph_parallel_streaming
from .handlers.report_format_handler import handle_format_change
from .handlers.rag_handlers import (
    init_ui_on_load,
    handle_file_upload,
    handle_refresh,
    handle_clear_files
)


# -----------------------------
# Main UI Assembly
# -----------------------------
def launch_real_ui():
    # Launch the Gradio UI for the AI Decision Support Agent.
    
    # SIMPLE PATTERN:
    # - Event handlers return values
    # - Gradio automatically updates output components
    # - No explicit state management needed
    
    # ------------------------
    # Create UI Components
    # ------------------------
    
    # Color scheme
    TITLE_COLOR = "#ffffff"
    SUBTITLE_COLOR = "#a0aec0"
    
    # Outputs
    plan_output = create_output_plan()
    analysis_output = create_output_analysis()
    decision_output, confidence_output = create_output_decision()
    messages_output = create_output_messages()
    report_output, format_selector, report_download_output = create_output_report()
    
    # Additional outputs
    historical_output = gr.HTML(label="Similar Historical Decisions")
    rag_evidence_output = gr.HTML(label="RAG Context & Evidence")
    
    # ------------------------
    # Assemble UI Layout
    # ------------------------
    # Theme configuration
    theme = gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="purple",
        neutral_hue="slate",
        font=["Helvetica", "Arial", "sans-serif"]
    )
    
    with gr.Blocks(theme=theme) as demo:
        # Header
        create_header(TITLE_COLOR, SUBTITLE_COLOR)
        
        # Input Section (includes RAG file management)
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
        
        gr.Markdown("---")

        # Output Tabs
        with gr.Tabs() as tabs:
            # Planning & Analysis
            with gr.Tab("📊 Planning & Analysis"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📋 Step-by-Step Plan")
                        plan_output.render()
                    with gr.Column(scale=1):
                        gr.Markdown("### 🔍 Analysis")
                        analysis_output.render()

            # Decision & Confidence
            with gr.Tab("✅ Decision"):
                gr.Markdown("### 🎯 Final Decision")
                with gr.Row():
                    with gr.Column(scale=3):
                        decision_output.render()
                    with gr.Column(scale=1):
                        confidence_output.render()

            # Conversation Log
            with gr.Tab("💬 Messages"):
                gr.Markdown("### 💬 Conversation History")
                gr.Markdown(
                    f"<p style='color:{SUBTITLE_COLOR}; margin-bottom:15px;'>"
                    "View the complete conversation history and reasoning steps."
                    "</p>"
                )
                messages_output.render()

            # Session Report
            with gr.Tab("📄 Report"):
                with gr.Row():
                    # Preview section (scrollable, 2/3 width)
                    create_report_preview_section(report_output)
                    
                    # Download section (fixed, 1/3 width)
                    create_report_download_section(format_selector, report_download_output)

            # Historical Decisions
            with gr.Tab("📜 Historical Decisions"):
                gr.Markdown(
                    f"<p style='color:{SUBTITLE_COLOR}; margin-bottom:15px;'>"
                    "Similar decisions from past sessions that may inform your current analysis."
                    "</p>"
                )
                historical_output.render()

            # RAG Context & Evidence
            with gr.Tab("📚 RAG Context & Evidence"):
                gr.Markdown(
                    f"<p style='color:{SUBTITLE_COLOR}; margin-bottom:15px;'>"
                    "Context documents and retrieved evidence used to ground the analysis."
                    "</p>"
                )
                rag_evidence_output.render()

        # Footer
        gr.Markdown("---")
        gr.Markdown(
            f"<p style='text-align:center; color:{SUBTITLE_COLOR}; font-size:0.9em;'>"
            "🤖 Powered by LangGraph, OpenAI GPT-4, and ChromaDB"
            "</p>"
        )
        
        # ========================================
        # SIMPLE EVENT-DRIVEN PATTERN
        # ========================================
        
        # 1️⃣ Initialize UI on page load/reload
        demo.load(
            fn=init_ui_on_load,
            inputs=None,
            outputs=[storage_summary, files_list_display]
        )
        
        # 2️⃣ File upload → returns updated values
        rag_input.upload(
            fn=handle_file_upload,
            inputs=[rag_input],
            outputs=[upload_status_output, storage_summary, files_list_display]
        )
        
        # 3️⃣ Refresh button → returns updated values
        refresh_files_btn.click(
            fn=handle_refresh,
            inputs=[],
            outputs=[storage_summary, files_list_display]
        )
        
        # 4️⃣ Clear button → returns updated values
        clear_files_btn.click(
            fn=handle_clear_files,
            inputs=[],
            outputs=[clear_status_display, storage_summary, files_list_display]
        )
        
        # ========================================
        # DECISION GRAPH EXECUTION
        # ========================================
        
        # Submit button - run decision graph with parallel execution
        submit_button.click(
            fn=run_graph_parallel_streaming,
            inputs=[question_input, rag_input],
            outputs=[
                plan_output,
                analysis_output,
                decision_output,
                confidence_output,
                messages_output,
                report_output,
                report_download_output,
                historical_output,
                rag_evidence_output
            ]
        )
        
        # Enter key submit - run decision graph with parallel execution
        question_input.submit(
            fn=run_graph_parallel_streaming,
            inputs=[question_input, rag_input],
            outputs=[
                plan_output,
                analysis_output,
                decision_output,
                confidence_output,
                messages_output,
                report_output,
                report_download_output,
                historical_output,
                rag_evidence_output
            ]
        )
        
        # Format selector - regenerate report download in selected format
        format_selector.change(
            fn=handle_format_change,
            inputs=[format_selector],
            outputs=[report_download_output]
        )

    # Enable queue for streaming functionality
    # This is CRITICAL for generators to work properly
    demo.queue()
    
    # Launch the Gradio interface
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)


if __name__ == "__main__":
    launch_real_ui()
