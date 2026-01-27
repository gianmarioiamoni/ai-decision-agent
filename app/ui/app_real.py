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
import os
import gradio as gr
from pathlib import Path

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

from app.rag.file_manager import get_file_manager
from app.rag.vectorstore_manager import get_vectorstore_manager
from app.rag.hf_persistence import get_hf_persistence

# Import handlers
from .handlers.graph_handler_parallel import run_graph_parallel_streaming
from .handlers.report_format_handler import handle_format_change
from .handlers.rag_handlers import (
    init_ui_on_load,
    handle_file_upload,
    handle_refresh,
    handle_clear_files
)

# ========================================
# GLOBAL VARIABLES
# ========================================
_RAG_BOOTSTRAPPED = False  # Flag to check if RAG has been bootstrapped

# -----------------------------
# Main UI Assembly
# -----------------------------
def launch_real_ui():
    # Launch the Gradio UI for the AI Decision Support Agent.

    TITLE_COLOR = "#ffffff"
    SUBTITLE_COLOR = "#a0aec0"

    # Outputs
    plan_output = create_output_plan()
    analysis_output = create_output_analysis()
    decision_output, confidence_output = create_output_decision()
    messages_output = create_output_messages()
    report_output, format_selector, report_download_output = create_output_report()

    # Additional outputs
    historical_output = gr.HTML(value="", label="Similar Historical Decisions")
    rag_evidence_output = gr.HTML(value="", label="RAG Context & Evidence")

    theme = gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="purple",
        neutral_hue="slate",
        font=["Helvetica", "Arial", "sans-serif"]
    )

    # --------------------------------------------------
    # RAG BOOTSTRAP (HF-SAFE, FILESYSTEM-AWARE)
    # --------------------------------------------------
    def bootstrap_rag():
        global _RAG_BOOTSTRAPPED

        if _RAG_BOOTSTRAPPED:
            print("[RAG BOOTSTRAP] ⚠️ Already completed")
            return

        print("[RAG BOOTSTRAP] 🚀 RAG BOOTSTRAP START")

        file_manager = get_file_manager()
        vectorstore_manager = get_vectorstore_manager()
        hf_persistence = get_hf_persistence()

        files = file_manager.refresh_state()

        if not files:
            print("[RAG BOOTSTRAP] ℹ️ No files in registry")
            _RAG_BOOTSTRAPPED = True
            return

        base_dir = Path(file_manager.storage_dir)

        total_chunks = 0

        for file in files:
            filename = file["name"]
            local_path = base_dir / filename

            # --------------------------------------------------
            # Ensure file exists locally (HF Spaces are stateless)
            # --------------------------------------------------
            if not local_path.exists():
                if hf_persistence:
                    print(f"[RAG BOOTSTRAP] 📥 Downloading {filename} from HF Hub...")
                    success = hf_persistence.download_document(
                        filename=filename,
                        local_path=str(local_path)
                    )
                    if not success:
                        print(f"[RAG BOOTSTRAP] ❌ Failed to download {filename}")
                        continue
                else:
                    print(f"[RAG BOOTSTRAP] ❌ Missing file and no HF persistence: {filename}")
                    continue

            # --------------------------------------------------
            # Read + embed
            # --------------------------------------------------
            try:
                with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if not content.strip():
                    print(f"[RAG BOOTSTRAP] ⚠️ Empty file: {filename}")
                    continue

                chunks = vectorstore_manager.add_documents(
                    documents=[content],
                    metadatas=[{
                        "filename": filename,
                        "source": "hf_registry",
                    }],
                    sync_to_hub=False
                )

                total_chunks += chunks
                print(f"[RAG BOOTSTRAP] ➕ Indexed {chunks} chunks from {filename}")

            except Exception as e:
                print(f"[RAG BOOTSTRAP] ❌ Failed indexing {filename}: {e}")

        print(f"[RAG BOOTSTRAP] 🎉 Indexing complete: {total_chunks} chunks added")
        _RAG_BOOTSTRAPPED = True

    # 🔑 ONE-TIME RAG BOOTSTRAP (process-level)
    bootstrap_rag()

    # ------------------------
    # BUILD UI
    # ------------------------
    with gr.Blocks() as demo:
        demo.api_mode = False

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

        gr.Markdown("---")

        with gr.Tabs():
            with gr.Tab("📊 Planning & Analysis"):
                with gr.Row():
                    plan_output.render()
                    analysis_output.render()

            with gr.Tab("✅ Decision"):
                decision_output.render()
                confidence_output.render()

            with gr.Tab("💬 Messages"):
                messages_output.render()

            with gr.Tab("📄 Report"):
                create_report_preview_section(report_output)
                create_report_download_section(format_selector, report_download_output)

            with gr.Tab("📜 Historical Decisions"):
                historical_output.render()

            with gr.Tab("📚 RAG Context & Evidence"):
                rag_evidence_output.render()

        gr.Markdown("---")

        # ------------------------
        # EVENTS
        # ------------------------
        demo.load(
            fn=init_ui_on_load,
            inputs=None,
            outputs=[storage_summary, files_list_display]
        )

        rag_input.upload(
            fn=handle_file_upload,
            inputs=[rag_input],
            outputs=[upload_status_output, storage_summary, files_list_display]
        )

        refresh_files_btn.click(
            fn=handle_refresh,
            inputs=[],
            outputs=[storage_summary, files_list_display]
        )

        clear_files_btn.click(
            fn=handle_clear_files,
            inputs=[],
            outputs=[clear_status_display, storage_summary, files_list_display]
        )

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

        format_selector.change(
            fn=handle_format_change,
            inputs=[format_selector],
            outputs=[report_download_output]
        )

    demo.queue(default_concurrency_limit=1, max_size=32)

    demo.launch(
        theme=theme,
        server_name="0.0.0.0",
        server_port=7860,
        ssr_mode=False
    )


if __name__ == "__main__":
    launch_real_ui()
