# app/ui/utils/rag_formatter.py
#
# RAG context formatting utilities for UI display.
#
# This module provides functions to format retrieved RAG context
# and uploaded documents into HTML for display in the Gradio interface.
#
# SAFE VERSION:
# - Always normalizes rag_context to string
# - Always normalizes context_docs to list[str]
# - Prevents: "expected string or bytes-like object, got 'list'"
#

import re


# ==========================================================
# Safety helpers
# ==========================================================


def _ensure_string(value) -> str:
    # Ensures input is always a string.
    # Prevents regex failures when receiving list / None.
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n\n".join(str(v) for v in value)
    return str(value)


def _ensure_list(value):
    # Ensures uploaded docs are always a list.
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


# ==========================================================
# Public API
# ==========================================================


def format_rag_context_for_ui(
    context_docs,
    rag_context,
) -> str:
    #
    # Format RAG context and uploaded documents into styled HTML.
    #

    safe_docs = _ensure_list(context_docs)
    safe_rag_context = _ensure_string(rag_context)

    rag_evidence_html = "<div style='font-family: monospace;'>"

    # --------------------------------------------------
    # Section 1: Uploaded Context Documents
    # --------------------------------------------------

    if safe_docs:
        rag_evidence_html += _format_uploaded_documents(safe_docs)
        rag_evidence_html += "<hr style='margin: 20px 0; border: 1px solid #e2e8f0;'>"

    # --------------------------------------------------
    # Section 2: Retrieved Evidence Chunks
    # --------------------------------------------------

    if safe_rag_context:
        rag_evidence_html += _format_retrieved_chunks(safe_rag_context)
    else:
        if not safe_docs:
            rag_evidence_html += (
                "<p style='color: #9ca3af; font-style: italic;'>"
                "No context documents uploaded. The analysis is based on "
                "general knowledge and historical decisions only."
                "</p>"
            )

    rag_evidence_html += "</div>"
    return rag_evidence_html


# ==========================================================
# Uploaded Documents
# ==========================================================


def _format_uploaded_documents(context_docs):
    #
    # Format uploaded context documents section.
    #

    html = (
        "<h3 style='color: #e5e7eb; font-weight: bold; margin-top: 0;'>"
        "📂 Uploaded Context Documents</h3>"
        "<p style='color: #9ca3af; margin-bottom: 15px;'>"
        "Similarity reflects direct semantic match with the question. "
        "These chunks were used as authoritative organizational constraints "
        "regardless of similarity. "
        f"Uploaded {len(context_docs)} document(s)</p>"
    )

    for i, doc in enumerate(context_docs, 1):
        doc = _ensure_string(doc)

        preview = doc[:500] if len(doc) > 500 else doc

        html += (
            f"<div style='border:1px solid #3498db; background-color:#eef6fc; "
            f"padding:12px; margin-bottom:10px; border-radius:6px;'>"
            f"<b style='color: #1e40af; font-weight: bold;'>Document {i}</b> "
            f"<span style='color: #4b5563;'>({len(doc)} chars)</span><br>"
            f"<pre style='white-space: pre-wrap; margin-top: 8px; "
            f"font-size: 0.9em; color: #1f2937;'>{preview}</pre>"
        )

        if len(doc) > 500:
            html += (
                "<p style='color: #6b7280; font-style: italic;'>" "... (truncated)</p>"
            )

        html += "</div>"

    return html


# ==========================================================
# Retrieved Chunks
# ==========================================================


def _format_retrieved_chunks(rag_context: str) -> str:
    #
    # Format retrieved RAG chunks section.
    #

    rag_context = _ensure_string(rag_context)

    html = (
        "<h3 style='color: #e5e7eb; font-weight: bold;'>"
        "📚 Retrieved Evidence (RAG Chunks)</h3>"
        "<p style='color: #9ca3af; margin-bottom: 15px;'>"
        "These chunks were used as authoritative organizational context. "
        "Similarity indicates direct semantic match with the question, "
        "not usefulness for the decision."
        "</p>"
    )

    chunk_pattern = (
        r"\[CHUNK (\d+)\] Source: (.+?) \| Chunk ID: (\d+) "
        r"\| Similarity: ([\d.]+)\s+"
        r"ORGANIZATIONAL FACT:\s+(.+?)(?=\[CHUNK|\Z)"
    )

    chunks = re.findall(chunk_pattern, rag_context, re.DOTALL)

    if chunks:
        for chunk_num, source, chunk_id, similarity, content in chunks:
            html += _format_chunk_card(
                chunk_num,
                source,
                chunk_id,
                similarity,
                content,
            )
    else:
        html += "<p style='color: #9ca3af;'>" "No chunks found in RAG context." "</p>"

    return html


# ==========================================================
# Chunk Card
# ==========================================================


def _format_chunk_card(
    chunk_num: str,
    source: str,
    chunk_id: str,
    similarity: str,
    content: str,
) -> str:

    sim_pct = float(similarity) * 100

    if sim_pct >= 70:
        sim_color = "#16a34a"
    elif sim_pct >= 50:
        sim_color = "#facc15"
    else:
        sim_color = "#6b7280"

    safe_content = _ensure_string(content).strip()

    html = (
        f"<div style='border:1px solid #16a34a; background-color:#f0fdf4; "
        f"padding:12px; margin-bottom:10px; border-radius:6px;'>"
        f"<div style='display:flex; justify-content:space-between; "
        f"margin-bottom:8px;'>"
        f"<b style='color:#15803d; font-weight:bold;'>"
        f"Chunk {chunk_num}</b>"
        f"<span style='background:{sim_color}; color:white; "
        f"padding:2px 8px; border-radius:12px; font-size:0.85em; "
        f"font-weight:bold;'>"
        f"{sim_pct:.0f}% query similarity</span>"
        f"</div>"
        f"<div style='font-size:0.85em; color:#4b5563; margin-bottom:8px;'>"
        f"<b style='color:#000000; font-weight:bold;'>Source:</b> {source} | "
        f"<b style='color:#000000; font-weight:bold;'>Chunk ID:</b> {chunk_id}"
        f"</div>"
        f"<pre style='white-space:pre-wrap; background:white; padding:8px; "
        f"border-radius:4px; font-size:0.9em; color:#1f2937;'>"
        f"{safe_content}</pre>"
        f"</div>"
    )

    return html
