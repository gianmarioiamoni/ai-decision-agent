# app/prompts/builders/decision_prompt_builder.py
# Prompt builder for decision node

from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from app.prompts.policy import DECISION_SUPPORT_POLICY
from app.prompts.schemas import PromptBundle
from app.prompts.builders.base_prompt_builder import BasePromptBuilder
from app.constants import SIMILARITY_THRESHOLD


class DecisionPromptBuilder(BasePromptBuilder):

    # Builds prompts for the decision node.
    # Constructs system and human messages with:
    # - RAG context FIRST (if significant)
    # - Question
    # - Analysis summary
    # - Similar past decisions
    # - Instructions for final decision

    @classmethod
    def build(
        cls,
        question: str,
        analysis: str,
        rag_context: str,
        similar_decisions: List[Dict],
    ) -> PromptBundle:

        # Defensive sanitization (critical for enterprise robustness)
        safe_question = str(question or "")
        safe_analysis = cls._safe_to_string(analysis)
        safe_rag_context = cls._safe_to_string(rag_context)
        safe_similar = similar_decisions or []

        # Determine RAG significance and mode
        rag_significant = cls.is_rag_significant(safe_rag_context)
        rag_mode = cls.determine_rag_mode(safe_rag_context)

        # Build system prompt
        system_prompt = cls._build_system_prompt(
            rag_context=safe_rag_context if rag_significant else "",
            similar_decisions=safe_similar,
        )

        # Build human prompt
        human_prompt = cls._build_human_prompt(
            question=safe_question,
            analysis=safe_analysis,
            rag_context=safe_rag_context if rag_significant else "",
            rag_significant=rag_significant,
        )

        return PromptBundle(
            system_message=SystemMessage(content=system_prompt),
            human_message=HumanMessage(content=human_prompt),
            rag_significant=rag_significant,
            rag_mode=rag_mode,
        )

    # ------------------------------------------------------------------
    # System Prompt
    # ------------------------------------------------------------------

    @classmethod
    def _build_system_prompt(
        cls,
        rag_context: str,
        similar_decisions: List[Dict],
    ) -> str:

        system_prompt = f"""
{DECISION_SUPPORT_POLICY}

You are now producing the final decision.

Based on the provided analysis, produce:
1) A clear decision
2) A brief justification grounded in the context

IMPORTANT:
- Do NOT include any numeric confidence values (percentages or decimals).
- Confidence scoring is handled externally by the system.
- You may express confidence only qualitatively (e.g. high, moderate, low).
"""

        # Historical context handling (defensive)
        if similar_decisions:

            similar_texts = ""

            for idx, sim in enumerate(similar_decisions):

                if not isinstance(sim, dict):
                    continue

                similarity = float(sim.get("similarity") or 0.0)

                if similarity >= SIMILARITY_THRESHOLD:

                    decision_text = cls._safe_to_string(
                        sim.get("decision") or sim.get("content") or ""
                    )

                    preview = decision_text[:200]

                    similar_texts += (
                        f"- Past Decision #{idx} "
                        f"(similarity {similarity:.2f}): "
                        f"{preview}...\n"
                    )

            if similar_texts:

                system_prompt += f"""

**HISTORICAL CONTEXT (MANDATORY ANALYSIS):**

{len(similar_decisions)} similar past decisions found:
{similar_texts}

**CRITICAL INSTRUCTION - HISTORICAL CONSISTENCY:**
You MUST include a section titled "### Historical Consistency Check" that:
1. Lists each similar past decision briefly
2. States whether this decision ALIGNS or DIVERGES from past patterns
3. If diverges, explains WHY

This demonstrates organizational learning and decision continuity.
"""
            else:
                system_prompt += """

**HISTORICAL CONTEXT:**
No sufficiently similar past decisions found.
This appears to be a novel decision for this organization.
"""

        system_prompt += """

**CONSTRAINT ENFORCEMENT**:
You MUST NOT recommend an option that conflicts with the operational or organizational
constraints described in the context unless explicitly justified.
"""

        if rag_context:
            system_prompt += """

**REQUIRED CITATION**:
After your decision and confidence score, include a section titled
"Contextual Factors Influencing This Decision" and list the specific contextual
factors that influenced this decision.
"""

        # Output format
        if similar_decisions and any(
            float(sim.get("similarity") or 0.0) >= SIMILARITY_THRESHOLD
            for sim in similar_decisions
            if isinstance(sim, dict)
        ):
            system_prompt += """

Respond in the following format:

Decision:
<decision text>

Confidence:
<number between 0 and 1>

### Historical Consistency Check
- Past Decision #X (similarity Y): [brief summary]
- **Consistency:** This decision [aligns with / diverges from] past pattern because...

Contextual Factors Influencing This Decision:
<list of factors>
"""
        else:
            system_prompt += """

Respond in the following format:

Decision:
<decision text>

Confidence:
<number between 0 and 1>

Contextual Factors Influencing This Decision:
<list of factors>
"""

        return system_prompt.strip()

    # ------------------------------------------------------------------
    # Human Prompt
    # ------------------------------------------------------------------

    @classmethod
    def _build_human_prompt(
        cls,
        question: str,
        analysis: str,
        rag_context: str,
        rag_significant: bool,
    ) -> str:

        human_prompt = ""

        if rag_significant:
            human_prompt += f"""Authoritative Organizational Reality (MANDATORY):
{rag_context}

"""

        human_prompt += f"""Question:
{question}

Analysis Summary:
{analysis}

Instructions:
Produce the final decision with:
1. A clear decision statement
2. Justification grounded in the authoritative context
3. A confidence score between 0 and 1
4. List of contextual factors that influenced this decision
"""

        return human_prompt

    # ------------------------------------------------------------------
    # Sanitizer Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_to_string(value: Any) -> str:
        # Ensures any incoming value becomes a string safely.
        # Prevents regex and formatting errors downstream.

        if value is None:
            return ""

        if isinstance(value, str):
            return value

        if isinstance(value, list):
            return "\n".join(str(v) for v in value)

        if hasattr(value, "page_content"):
            return str(value.page_content)

        return str(value)
