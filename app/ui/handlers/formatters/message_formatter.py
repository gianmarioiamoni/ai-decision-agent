# app/ui/handlers/formatters/message_formatter.py
#
# Formatter for conversation messages.
# Converts message objects to HTML representation.
#

from typing import List, Any
from .base_formatter import BaseFormatter


class MessageFormatter(BaseFormatter):
    """
    Format conversation messages into HTML.
    
    Responsibility: Convert message list to HTML-formatted conversation log.
    """
    
    # Role styling configuration
    ROLE_COLORS = {
        "user": "#2563eb",
        "assistant": "#16a34a",
        "system": "#f59e0b"
    }
    
    ROLE_ICONS = {
        "user": "👤",
        "assistant": "🤖",
        "system": "⚙️"
    }
    
    def format(self, messages: List[Any]) -> str:
        """
        Format conversation messages into HTML.
        
        Args:
            messages: List of message objects (can be dict or objects with attributes)
        
        Returns:
            HTML-formatted messages string
        """
        if not messages:
            return "<p style='color: gray;'>No messages generated</p>"
        
        formatted_messages = []
        
        for msg in messages:
            role, content = self._extract_message_data(msg)
            color = self.ROLE_COLORS.get(role, "#6b7280")
            icon = self.ROLE_ICONS.get(role, "💬")
            
            formatted_messages.append(
                f"<p style='color:{color}'>{icon} <b>{role}</b>: {content}</p>"
            )
        
        return "".join(formatted_messages)
    
    def _extract_message_data(self, msg: Any) -> tuple[str, str]:
        """
        Extract role and content from message object.
        
        Args:
            msg: Message object (dict or object with attributes)
        
        Returns:
            Tuple of (role, content)
        """
        if hasattr(msg, 'type'):
            role = getattr(msg, 'type', 'unknown')
            content = getattr(msg, 'content', str(msg))
        elif isinstance(msg, dict):
            role = msg.get("role", "?")
            content = msg.get("content", "")
        else:
            role = "?"
            content = str(msg)
        
        return role, content

