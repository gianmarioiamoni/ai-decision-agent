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
    # This showcases the value of contextual AI vs generic LLM.
    #
    
    @classmethod
    def build(
        cls,
        question: str,
        context_docs: list[str],
    ) -> PromptBundle:
        #
        # Build complete prompt bundle for planner node.
        #
        # Args:
        #     question: User's decision question
        #     context_docs: Raw uploaded documents (list of strings)
        #
        # Returns:
        #     PromptBundle with context-grounded or generic planning instructions
        #
        # Note:
        #     Planner runs BEFORE rag_node, so we use raw context_docs.
        #     We extract key constraints from raw docs for context-grounded planning.
        #

        # Quick context extraction from raw docs
        context_summary = cls._extract_context_summary(context_docs) if context_docs else ""
        
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
    
    @classmethod
    def _extract_context_summary(cls, context_docs: list[str]) -> str:
        # Extract key organizational constraints from raw documents.
        #
        # Quick extraction for planning (full semantic retrieval happens in rag_node).
        #
        # Args:
        #     context_docs: Raw uploaded documents (list of strings)
        #
        # Returns:
        #     Summary of key organizational constraints
        #
        
        if not context_docs:
            return ""
        
        # Combine all docs
        combined = "\n\n".join(context_docs)
        
        # Take first 1500 chars (enough for key constraints)
        # This is a preview for planning; full retrieval happens in rag_node
        summary = combined[:1500]
        
        return summary.strip()
    
    @classmethod
    def _build_contextual_system_prompt(cls) -> str:
        """Build system prompt for context-grounded planning."""
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
1. Reference SPECIFIC constraints from the context (team size, tech stack, timelines)
2. Acknowledge concrete limitations explicitly
3. Use organizational terminology (if present in context)
4. Show domain-specific understanding (not generic)

**FORMAT:**
Generate 3-5 steps, each step should:
- Start with a contextual constraint ("Given X..." or "Considering Y...")
- Propose a concrete evaluation criterion
- Be actionable and specific to this organization

The plan should make it OBVIOUS you understand the organizational reality.
""".strip()
    
    @classmethod
    def _build_contextual_human_prompt(cls, question: str, rag_context: str) -> str:
        """Build human prompt with organizational context."""
        return f"""Organizational Context (MANDATORY - READ CAREFULLY):
{rag_context}

Question:
{question}

Instructions:
Generate a 3-5 step decision plan that is GROUNDED in the specific organizational context above.

Each step must:
1. Reference concrete constraints (team size, expertise, timelines, tech stack)
2. Show you understand the organizational reality
3. Be specific, not generic consulting advice

Example of GOOD contextual step:
"Given the team's limited backend expertise (only 2/8 engineers comfortable with Node.js) and high-velocity 2-week sprints, assess whether the Next.js learning curve is feasible without impacting delivery predictability"

Example of BAD generic step:
"Evaluate team capabilities and assess technical fit"

Generate the plan now:"""
    
    @classmethod
    def _build_generic_system_prompt(cls) -> str:
        """Build system prompt for generic planning (fallback)."""
        return f"""
{DECISION_SUPPORT_POLICY}

You are a strategic decision planner.

Generate a high-level, domain-agnostic plan for making a well-reasoned decision.

The plan should:
- Identify key dimensions to analyze
- Remain domain-agnostic (no specific industry assumptions)
- Avoid premature conclusions or recommendations
- Be 3-5 steps maximum

Focus on PROCESS, not content.
""".strip()
    
    @classmethod
    def _build_generic_human_prompt(cls, question: str) -> str:
        """Build human prompt for generic planning."""
        return f"""Question:
{question}

Generate a 3-5 step decision plan that identifies:
1. What information is needed
2. What dimensions to evaluate
3. What criteria to apply

Keep it domain-agnostic and process-focused."""

