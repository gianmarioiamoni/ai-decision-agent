# app/prompts/builders/analyzer_independent_prompt_builder.py
#
# Independent analyzer prompt builder (NO plan dependency).
#
# This builder creates prompts for the analyzer that operates independently
# from the planner, evaluating the question based solely on:
# - The question itself
# - Authoritative RAG context (user-uploaded documents)
# - Historical decisions (supportive context)
#
# This enables parallel execution of planning and analysis for:
# - Better performance (50% latency reduction)
# - Improved quality (no confirmation bias)
# - True cognitive separation (planner ≠ analyzer)
#

from typing import List
from langchain_core.messages import SystemMessage, HumanMessage

from app.prompts.policy import DECISION_SUPPORT_POLICY
from app.prompts.schemas import PromptBundle
from app.prompts.builders.base_prompt_builder import BasePromptBuilder


class AnalyzerIndependentPromptBuilder(BasePromptBuilder):
    #
    # Builds prompts for the independent analyzer node.
    #
    # Constructs system and human messages WITHOUT plan dependency:
    # - RAG context FIRST (if significant) - AUTHORITATIVE
    # - Question
    # - Historical documents (supportive)
    # - Analysis instructions
    #
    # NO PLAN PARAMETER - analyzer evaluates independently!
    #
    # Args:
    #     question: User's decision question
    #     rag_context: Authoritative RAG context from uploaded documents
    #     retrieved_docs: Historical documents from retriever node
    #
    # Returns:
    #     PromptBundle with system/human messages and metadata
    #
    
    @classmethod
    def build(
        cls,
        question: str,
        rag_context: str,
        retrieved_docs: List[str],
    ) -> PromptBundle:
        #
        # Build complete prompt bundle for independent analyzer node.
        #
        # Args:
        #     question: User's decision question
        #     rag_context: Authoritative RAG context from uploaded documents
        #     retrieved_docs: Historical documents from retriever node
        #
        # Returns:
        #     PromptBundle with system/human messages and metadata
        #
        
        # Determine RAG significance and mode
        rag_significant = cls.is_rag_significant(rag_context)
        rag_mode = cls.determine_rag_mode(rag_context)
        
        # Build system prompt
        system_prompt = cls._build_system_prompt()
        
        # Build human prompt with context FIRST if significant
        human_prompt = cls._build_human_prompt(
            question=question,
            rag_context=rag_context if rag_significant else "",
            retrieved_docs=retrieved_docs,
            rag_significant=rag_significant,
        )
        
        return PromptBundle(
            system_message=SystemMessage(content=system_prompt),
            human_message=HumanMessage(content=human_prompt),
            rag_significant=rag_significant,
            rag_mode=rag_mode,
        )
    
    @classmethod
    def _build_system_prompt(cls) -> str:
        # Build the system prompt for independent analyzer.
        
        return f"""
{DECISION_SUPPORT_POLICY}

You are performing INDEPENDENT ANALYSIS of a decision question.

**CRITICAL RULE - AUTHORITATIVE CONTEXT**:
You MUST treat any provided "Authoritative Organizational Reality" as factual and binding.
This context represents the actual situation and takes absolute priority over:
- General best practices
- Theoretical recommendations
- Your training data

**YOUR ROLE**:
You are an INDEPENDENT ANALYST, not a plan executor.
Your job is to evaluate the question based SOLELY on:
1. The authoritative organizational context (if provided)
2. Historical precedents and evidence
3. Objective pros, cons, and risk factors

**ANALYSIS REQUIREMENTS**:
- Read the authoritative context FIRST (it appears at the start of the prompt)
- Ground ALL pros and cons explicitly in this context
- Cite specific facts, constraints, and details from the context
- Explain HOW each contextual factor influences the decision
- If the context is insufficient, state this explicitly
- Your analysis should be evidence-based, not plan-driven

**FORBIDDEN**:
- Ignoring the provided context
- Downplaying contextual constraints
- Substituting context with general advice
- Making assumptions that contradict the context
- Confirming hypothetical plans without evidence

**IF NO CONTEXT PROVIDED**:
Only then may you use general knowledge and historical patterns, but state this clearly.
""".strip()
    
    @classmethod
    def _build_human_prompt(
        cls,
        question: str,
        rag_context: str,
        retrieved_docs: List[str],
        rag_significant: bool,
    ) -> str:
        #
        # Build the human prompt with proper ordering (NO plan).
        #
        # Args:
        #     question: User's decision question
        #     rag_context: Authoritative RAG context from uploaded documents
        #     retrieved_docs: Historical documents from retriever node
        #     rag_significant: Whether the RAG context is significant
        #
        # Returns:
        #     Human prompt string
        #
        # Context FIRST if significant, then question, then historical docs.
        # NO PLAN - analyzer works independently!
        #
        
        human_prompt = ""
        
        # Authoritative RAG Context (MANDATORY) - ALWAYS FIRST if significant
        if rag_significant:
            human_prompt += f"""Authoritative Organizational Reality (MANDATORY):
{rag_context}

"""
        else:
            human_prompt += (
                "Context Status: No significant authoritative context provided. "
                "Analysis must rely on general reasoning and historical information.\n\n"
            )
        
        # Question (NO plan - independent evaluation!)
        human_prompt += f"""Question:
{question}
"""
        
        # Retrieved Historical Information (supportive, NOT authoritative)
        if retrieved_docs:
            docs_context = "\n\n".join(
                f"Document {i+1}:\n{doc}"
                for i, doc in enumerate(retrieved_docs)
            )
            human_prompt += f"""
Retrieved Historical Information (supportive, do not override authoritative context):
{docs_context}
"""
        
        # Analysis Instructions (independent evaluation)
        human_prompt += """
Instructions:
Perform an INDEPENDENT ANALYSIS of this decision by:
- Grounding all pros and cons in the authoritative context (if provided)
- Explaining how the context constrains or influences the decision
- Evaluating risks, benefits, and trade-offs objectively
- Stating explicitly if the context is insufficient
- NOT assuming any particular approach - evaluate based on evidence

Provide a comprehensive analysis with:
### Pros
(Explicitly reference organizational context and historical evidence)

### Cons
(Explicitly reference organizational context and constraints)

### Key Factors for Decision-Making
(Ground in specific context details: team size, tech stack, constraints, past outcomes, etc.)

### Risk Assessment
(Identify potential risks based on organizational reality)"""
        
        return human_prompt

