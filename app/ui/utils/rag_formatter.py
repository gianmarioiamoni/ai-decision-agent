# app/ui/utils/rag_formatter.py
"""
RAG context formatting utilities for UI display.

This module provides functions to format retrieved RAG context and uploaded documents
into HTML for display in the Gradio interface.
"""

import re
from typing import List, Tuple


def format_rag_context_for_ui(
    context_docs: List[str],
    rag_context: str
) -> str:
    """
    Format RAG context and uploaded documents into styled HTML for UI display.
    
    This function creates a readable HTML representation of:
    1. Uploaded context documents (with preview)
    2. Retrieved evidence chunks (with similarity scores)
    
    Args:
        context_docs: List of uploaded document contents
        rag_context: Retrieved RAG context string with chunk metadata
    
    Returns:
        Styled HTML string for display in Gradio interface
    """
    rag_evidence_html = "<div style='font-family: monospace;'>"
    
    # Section 1: Uploaded Context Documents
    if context_docs:
        rag_evidence_html += _format_uploaded_documents(context_docs)
        rag_evidence_html += "<hr style='margin: 20px 0; border: 1px solid #e2e8f0;'>"
    
    # Section 2: Retrieved Evidence Chunks
    if rag_context:
        rag_evidence_html += _format_retrieved_chunks(rag_context)
    else:
        if not context_docs:
            rag_evidence_html += (
                "<p style='color: #9ca3af; font-style: italic;'>"
                "No context documents uploaded. The analysis is based on "
                "general knowledge and historical decisions only."
                "</p>"
            )
    
    rag_evidence_html += "</div>"
    return rag_evidence_html


def _format_uploaded_documents(context_docs: List[str]) -> str:
    """
    Format uploaded context documents section.
    
    Args:
        context_docs: List of uploaded document contents
    
    Returns:
        HTML string for uploaded documents section
    """
    html = (
        "<h3 style='color: #e5e7eb; font-weight: bold; margin-top: 0;'>"
        "📂 Uploaded Context Documents</h3>"
        f"<p style='color: #9ca3af; margin-bottom: 15px;'>"
        f"Uploaded {len(context_docs)} document(s)</p>"
    )
    
    for i, doc in enumerate(context_docs, 1):
        preview = doc[:500] if len(doc) > 500 else doc
        html += (
            f"<div style='border:1px solid #3498db; background-color:#eef6fc; "
            f"padding:12px; margin-bottom:10px; border-radius:6px;'>"
            f"<b style='color: #1e40af; font-weight: bold;'>Document {i}</b> "
            f"<span style='color: #4b5563;'>({len(doc)} chars)</span><br>"
            f"<pre style='white-space: pre-wrap; margin-top: 8px; font-size: 0.9em; "
            f"color: #1f2937;'>{preview}</pre>"
        )
        if len(doc) > 500:
            html += "<p style='color: #6b7280; font-style: italic;'>... (truncated)</p>"
        html += "</div>"
    
    return html


def _format_retrieved_chunks(rag_context: str) -> str:
    """
    Format retrieved RAG chunks section.
    
    Parses the rag_context string to extract chunks with metadata (source, chunk ID, similarity)
    and formats them into styled HTML cards.
    
    Args:
        rag_context: RAG context string with chunk metadata
    
    Returns:
        HTML string for retrieved chunks section
    """
    html = (
        "<h3 style='color: #e5e7eb; font-weight: bold;'>"
        "📚 Retrieved Evidence (RAG Chunks)</h3>"
        "<p style='color: #9ca3af; margin-bottom: 15px;'>"
        "These specific chunks were retrieved and used to ground the analysis:"
        "</p>"
    )
    
    # Parse chunks from rag_context
    chunk_pattern = (
        r'\[CHUNK (\d+)\] Source: (.+?) \| Chunk ID: (\d+) \| Similarity: ([\d.]+)\s+'
        r'ORGANIZATIONAL FACT:\s+(.+?)(?=\[CHUNK|\Z)'
    )
    chunks = re.findall(chunk_pattern, rag_context, re.DOTALL)
    
    if chunks:
        for chunk_num, source, chunk_id, similarity, content in chunks:
            html += _format_chunk_card(chunk_num, source, chunk_id, similarity, content)
    else:
        html += "<p style='color: #9ca3af;'>No chunks found in RAG context.</p>"
    
    return html


def _format_chunk_card(
    chunk_num: str,
    source: str,
    chunk_id: str,
    similarity: str,
    content: str
) -> str:
    """
    Format a single RAG chunk into a styled HTML card.
    
    Args:
        chunk_num: Chunk number
        source: Source document name
        chunk_id: Unique chunk identifier
        similarity: Similarity score (0.0-1.0)
        content: Chunk content text
    
    Returns:
        HTML string for chunk card
    """
    sim_pct = float(similarity) * 100
    
    # Color based on similarity score
    if sim_pct >= 70:
        sim_color = "#16a34a"  # Green
    elif sim_pct >= 50:
        sim_color = "#facc15"  # Yellow
    else:
        sim_color = "#ef4444"  # Red
    
    html = (
        f"<div style='border:1px solid #16a34a; background-color:#f0fdf4; "
        f"padding:12px; margin-bottom:10px; border-radius:6px;'>"
        f"<div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>"
        f"<b style='color: #15803d; font-weight: bold;'>Chunk {chunk_num}</b>"
        f"<span style='background: {sim_color}; color: white; padding: 2px 8px; "
        f"border-radius: 12px; font-size: 0.85em; font-weight: bold;'>"
        f"{sim_pct:.0f}% relevant</span>"
        f"</div>"
        f"<div style='font-size: 0.85em; color: #4b5563; margin-bottom: 8px;'>"
        f"<b style='color: #000000; font-weight: bold;'>Source:</b> {source} | "
        f"<b style='color: #000000; font-weight: bold;'>Chunk ID:</b> {chunk_id}"
        f"</div>"
        f"<pre style='white-space: pre-wrap; background: white; padding: 8px; "
        f"border-radius: 4px; font-size: 0.9em; color: #1f2937;'>{content.strip()}</pre>"
        f"</div>"
    )
    
    return html

