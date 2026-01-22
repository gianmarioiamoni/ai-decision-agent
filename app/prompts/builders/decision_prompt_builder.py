# app/prompts/builders/decision_prompt_builder.py
# Prompt builder for decision node

from typing import List, Dict
from langchain_core.messages import SystemMessage, HumanMessage

from app.prompts.policy import DECISION_SUPPORT_POLICY
from app.prompts.schemas import PromptBundle
from app.prompts.builders.base_prompt_builder import BasePromptBuilder


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
        
        # Build complete prompt bundle for decision node.
        # Args:
        #     question: User's decision question
        #     analysis: Generated analysis from analyzer node
        #     rag_context: Authoritative RAG context from uploaded documents
        #     similar_decisions: Similar past decisions from memory
        # Returns:
        #     PromptBundle with system/human messages and metadata
        
        # Determine RAG significance and mode
        rag_significant = cls.is_rag_significant(rag_context)
        rag_mode = cls.determine_rag_mode(rag_context)
        
        # Build system prompt
        system_prompt = cls._build_system_prompt(
            rag_context=rag_context if rag_significant else "",
            similar_decisions=similar_decisions,
        )
        
        # Build human prompt with context FIRST if significant
        human_prompt = cls._build_human_prompt(
            question=question,
            analysis=analysis,
            rag_context=rag_context if rag_significant else "",
            rag_significant=rag_significant,
        )
        
        return PromptBundle(
            system_message=SystemMessage(content=system_prompt),
            human_message=HumanMessage(content=human_prompt),
            rag_significant=rag_significant,
            rag_mode=rag_mode,
        )
    
    @classmethod
    def _build_system_prompt(
        cls,
        rag_context: str,
        similar_decisions: List[Dict],
    ) -> str:
        """Build the system prompt for decision node."""
        system_prompt = f"""
{DECISION_SUPPORT_POLICY}

You are now producing the final decision.

Based on the provided analysis, produce:
1) A clear decision
2) A brief justification grounded in the context
3) A confidence score between 0 and 1
"""
        
        # Add similar decisions context with EXPLICIT consistency check requirement
        if similar_decisions:
            similar_texts = ""
            for sim in similar_decisions:
                if sim.get("similarity", 0) >= 0.75:  # SIMILARITY_THRESHOLD
                    similar_texts += f"- Decision #{sim['decision_id']} (similarity {sim['similarity']:.2f}): {sim['content'][:200]}...\n"
            
            if similar_texts:
                system_prompt += f"""

**HISTORICAL CONTEXT (MANDATORY ANALYSIS):**

{len(similar_decisions)} similar past decisions found:
{similar_texts}

**CRITICAL INSTRUCTION - HISTORICAL CONSISTENCY:**
You MUST include a section titled "### Historical Consistency Check" that:
1. Lists each similar past decision briefly
2. States whether this decision ALIGNS or DIVERGES from past patterns
3. If diverges, explains WHY (new constraints, different context, lessons learned)

This demonstrates organizational learning and decision continuity.
"""
            else:
                system_prompt += """

**HISTORICAL CONTEXT:**
No sufficiently similar past decisions found (similarity threshold: 0.75).
This appears to be a novel decision for this organization.
"""
        
        system_prompt += """

**CONSTRAINT ENFORCEMENT**:
You MUST NOT recommend an option that conflicts with the operational or organizational
constraints described in the context, unless you explicitly justify why the constraint
should be overridden and what mitigation is required.
"""
        
        # Add required citation if RAG context present
        if rag_context:
            system_prompt += """

**REQUIRED CITATION**:
After your decision and confidence score, include a section titled "Contextual Factors Influencing This Decision"
and list the specific contextual factors (from the "Authoritative Context" if provided) that most influenced this decision.
If no authoritative context was provided, state "No specific organizational context influenced this decision."
"""
        
        # Format with historical consistency check if similar decisions exist
        if similar_decisions and any(sim.get("similarity", 0) >= 0.75 for sim in similar_decisions):
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
    
    @classmethod
    def _build_human_prompt(
        cls,
        question: str,
        analysis: str,
        rag_context: str,
        rag_significant: bool,
    ) -> str:
        
        # Build the human prompt with proper ordering.
        
        # Context FIRST if significant, then question/analysis.
        human_prompt = ""
        
        # Authoritative Context (MANDATORY) - ALWAYS FIRST if significant
        if rag_significant:
            human_prompt += f"""Authoritative Organizational Reality (MANDATORY):
{rag_context}

"""
        
        # Question and Analysis
        human_prompt += f"""Question:
{question}

Analysis Summary:
{analysis}

Instructions:
Produce the final decision with:
1. A clear decision statement
2. Justification grounded in the authoritative context
3. A confidence score between 0 and 1
4. List of contextual factors that influenced this decision"""
        
        return human_prompt

