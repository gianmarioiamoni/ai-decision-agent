# app/prompts/builders/planner_prompt_builder.py
# Prompt builder for planner node - context-grounded planning

from langchain_core.messages import SystemMessage, HumanMessage

from app.prompts.policy import DECISION_SUPPORT_POLICY
from app.prompts.schemas import PromptBundle
from app.prompts.builders.base_prompt_builder import BasePromptBuilder


class PlannerPromptBuilder(BasePromptBuilder):
    #
    # Builds prompts for the planner node.
    #
    # Key Feature: Context-Grounded Planning
    # - If RAG context exists → plan references specific organizational constraints
    # - If no context → generic domain-agnostic plan
    #

    @classmethod
    def build(
        cls,
        question: str,
        context_docs: list,  # ← changed (more robust)
    ) -> PromptBundle:

        # Quick context extraction from raw docs
        context_summary = (
            cls._extract_context_summary(context_docs) if context_docs else ""
        )

        # Determine if we have significant context
        has_context = bool(context_summary and len(context_summary) > 50)
        rag_mode = "authoritative" if has_context else "fallback"

        # Build prompts based on context availability
        if has_context:
            system_prompt = cls._build_contextual_system_prompt()
            human_prompt = cls._build_contextual_human_prompt(question, context_summary)
        else:
            system_prompt = cls._build_generic_system_prompt()
            human_prompt = cls._build_generic_human_prompt(question)

        return PromptBundle(
            system_message=SystemMessage(content=system_prompt),
            human_message=HumanMessage(content=human_prompt),
            rag_significant=has_context,
            rag_mode=rag_mode,
        )

    # ==========================================================
    # ROBUST CONTEXT EXTRACTION (FIXED)
    # ==========================================================

    @classmethod
    def _extract_context_summary(cls, context_docs: list) -> str:
        """
        Extract key organizational constraints from raw documents.

        Accepts:
        - list[str]
        - list[Document]
        - list[dict]
        - mixed content

        Returns:
            First 1500 chars of safely combined content.
        """

        if not context_docs:
            return ""

        safe_chunks = []

        for doc in context_docs:
            if doc is None:
                continue

            # LangChain Document
            if hasattr(doc, "page_content"):
                safe_chunks.append(str(doc.page_content))
                continue

            # Dict-like
            if isinstance(doc, dict):
                if "page_content" in doc:
                    safe_chunks.append(str(doc["page_content"]))
                elif "content" in doc:
                    safe_chunks.append(str(doc["content"]))
                else:
                    safe_chunks.append(str(doc))
                continue

            # Already string
            if isinstance(doc, str):
                safe_chunks.append(doc)
                continue

            # Fallback
            safe_chunks.append(str(doc))

        combined = "\n\n".join(safe_chunks)

        summary = combined[:1500]

        return summary.strip()

    # ==========================================================
    # CONTEXTUAL PROMPTS
    # ==========================================================

    @classmethod
    def _build_contextual_system_prompt(cls) -> str:
        return f"""
{DECISION_SUPPORT_POLICY}

You are a strategic decision planner with access to authoritative organizational context.

**CRITICAL INSTRUCTION - CONTEXT-GROUNDED PLANNING:**

You MUST produce a plan that demonstrates understanding of the SPECIFIC organizational reality.

DO NOT generate generic consulting steps like:
❌ "Evaluate team capabilities"
❌ "Assess technical fit"
❌ "Consider implementation complexity"

INSTEAD, ground every step in concrete organizational factors:
✅ "Given the 8-person team with only 2 backend engineers, assess if..."
✅ "Considering the 2-week sprint cycles, evaluate if..."
✅ "With 5000+ active users requiring <2s page load, verify if..."

**REQUIREMENTS:**
1. Reference SPECIFIC constraints from the context
2. Acknowledge concrete limitations explicitly
3. Use organizational terminology (if present in context)
4. Show domain-specific understanding

**FORMAT:**
Generate 3-5 steps. Each step should:
- Start with a contextual constraint
- Propose a concrete evaluation criterion
- Be actionable and organization-specific
""".strip()

    @classmethod
    def _build_contextual_human_prompt(cls, question: str, rag_context: str) -> str:
        return f"""Organizational Context (MANDATORY - READ CAREFULLY):
{rag_context}

Question:
{question}

Instructions:
Generate a 3-5 step decision plan that is GROUNDED in the specific organizational context above.

Each step must:
1. Reference concrete constraints
2. Demonstrate contextual understanding
3. Avoid generic consulting advice

Generate the plan now:"""

    # ==========================================================
    # GENERIC PROMPTS (FALLBACK)
    # ==========================================================

    @classmethod
    def _build_generic_system_prompt(cls) -> str:
        return f"""
{DECISION_SUPPORT_POLICY}

You are a strategic decision planner.

Generate a high-level, domain-agnostic plan for making a well-reasoned decision.

The plan should:
- Identify key dimensions to analyze
- Remain domain-agnostic
- Avoid premature conclusions
- Be 3-5 steps maximum

Focus on PROCESS, not content.
""".strip()

    @classmethod
    def _build_generic_human_prompt(cls, question: str) -> str:
        return f"""Question:
{question}

Generate a 3-5 step decision plan that identifies:
1. What information is needed
2. What dimensions to evaluate
3. What criteria to apply

Keep it domain-agnostic and process-focused."""
