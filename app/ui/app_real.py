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
_RAG_BOOTSTRAPPED = False  # One-time bootstrap guard


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

    historical_output = gr.HTML(value="", label="Similar Historical Decisions")
    rag_evidence_output = gr.HTML(value="", label="RAG Context & Evidence")

    theme = gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="purple",
        neutral_hue="slate",
        font=["Helvetica", "Arial", "sans-serif"]
    )

    # -------------------------------------------------
    # 🔑 RAG BOOTSTRAP (FINAL, CORRECT)
    # -------------------------------------------------
    def bootstrap_rag():
        #
        # One-time RAG bootstrap.
        #
        # Responsibilities:
        # - Load FileManager registry
        # - Initialize Vectorstore
        # - If vectorstore is empty:
        #   - Ensure files exist locally (download if missing)
        #   - Rebuild embeddings
        #
        # No uploads, no HF sync, no side effects.
        #

        global _RAG_BOOTSTRAPPED
        if _RAG_BOOTSTRAPPED:
            print("[RAG BOOTSTRAP] ⚠️ Already bootstrapped")
            return

        print("[RAG BOOTSTRAP] 🚀 RAG BOOTSTRAP START")

        file_manager = get_file_manager()
        vectorstore_manager = get_vectorstore_manager()
        hf_persistence = getattr(file_manager, "hf_persistence", None)

        # Load registry
        files = file_manager.refresh_state()
        print(f"[RAG BOOTSTRAP] 📄 Registry loaded: {len(files)} file(s)")

        # Initialize vectorstore (persistent Chroma)
        vectorstore_manager.get_vectorstore()
        print("[RAG BOOTSTRAP] 📦 Vectorstore initialized")

        # Rebuild embeddings only if needed
        if files and not vectorstore_manager.has_documents():
            print("[RAG BOOTSTRAP] 🔄 Vectorstore empty, rebuilding embeddings")

            for f in files:
                name = f.get("name")
                path = f.get("path")

                if not name:
                    continue

                # Ensure local file exists
                if not path or not os.path.exists(path):
                    if hf_persistence:
                        print(f"[RAG BOOTSTRAP] 📥 Downloading missing file: {name}")
                        success = hf_persistence.download_document(
                            filename=name,
                            local_path=os.path.join(
                                file_manager.storage_dir, name
                            )
                        )
                        if not success:
                            print(f"[RAG BOOTSTRAP] ❌ Failed to download {name}")
                            continue
                        path = os.path.join(file_manager.storage_dir, name)
                    else:
                        print(f"[RAG BOOTSTRAP] ⚠️ No HF persistence, cannot download {name}")
                        continue

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()

                    if not content.strip():
                        print(f"[RAG BOOTSTRAP] ⚠️ Empty file skipped: {name}")
                        continue

                    vectorstore_manager.add_documents(
                        documents=[content],
                        metadatas=[{"filename": name}],
                        sync_to_hub=False,
                    )

                    print(f"[RAG BOOTSTRAP] ✅ Embedded {name}")

                except Exception as e:
                    print(f"[RAG BOOTSTRAP] ❌ Failed embedding {name}: {e}")

        else:
            print("[RAG BOOTSTRAP] ℹ️ Vectorstore already populated")

        _RAG_BOOTSTRAPPED = True
        print("[RAG BOOTSTRAP] ✅ RAG bootstrap completed")

    # 🔑 RUN BOOTSTRAP EXACTLY ONCE
    bootstrap_rag()

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
                    with gr.Column():
                        plan_output.render()
                    with gr.Column():
                        analysis_output.render()

            with gr.Tab("✅ Decision"):
                decision_output.render()
                confidence_output.render()

            with gr.Tab("💬 Messages"):
                messages_output.render()

            with gr.Tab("📄 Report"):
                with gr.Row():
                    create_report_preview_section(report_output)
                    create_report_download_section(format_selector, report_download_output)

            with gr.Tab("📜 Historical Decisions"):
                historical_output.render()

            with gr.Tab("📚 RAG Context & Evidence"):
                rag_evidence_output.render()

        # -----------------------------
        # EVENT HANDLERS
        # -----------------------------
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
