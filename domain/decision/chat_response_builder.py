from dataclasses import dataclass


@dataclass(frozen=True)
class ChatDecisionResponse:
    text: str


class ChatDecisionResponseBuilder:
    @staticmethod
    def build(
        decision: str,
        confidence: float,
        rationale: list[str] | None = None,
    ) -> ChatDecisionResponse:
        #
        # Build a concise, user-facing chat response.
        #

        lines = []

        # Main recommendation
        lines.append(decision.strip())

        # Optional rationale (short, conversational)
        if rationale:
            lines.append("")
            lines.append("Key factors considered:")
            for item in rationale[:3]:
                lines.append(f"- {item}")

        # Optional follow-up
        lines.append("")
        lines.append(
            "You can provide additional context, "
            "ask for alternatives, or request a deeper analysis."
        )

        return ChatDecisionResponse(text="\n".join(lines))
