# app/ui/components/input_context_docs.py

import gradio as gr


def create_input_context_docs():
    # Optional upload of context documents for Hybrid RAG.
    # If no documents are uploaded, the system behaves as a standard LLM.

    context_docs = gr.Files(
        label="📚 Context Documents (optional)",
        file_types=[".txt", ".md", ".pdf"],
        file_count="multiple",
        interactive=True,
        visible=True,
        elem_id="context-docs-upload"
    )

    context_help = gr.Markdown(
        """
        <p style="color:#6b7280; font-size:0.9em; margin-top:5px;">
        <strong>Optional.</strong> Upload documents containing contextual information
        (e.g. team structure, technologies, internal constraints, business goals).
        <br/>
        If no documents are provided, the AI will respond using general knowledge only.
        </p>
        """
    )

    return context_docs, context_help
