# app/ui/handlers/formatters/base_formatter.py
#
# Abstract base class for all formatters.
# Ensures consistent interface for formatting operations.
#

from abc import ABC, abstractmethod
from typing import Any


class BaseFormatter(ABC):
    """
    Abstract base formatter for converting data to display format.
    
    All formatters must implement the format() method following SRP:
    - Each formatter handles ONE type of data
    - Returns string representation suitable for UI display
    """
    
    @abstractmethod
    def format(self, data: Any) -> str:
        """
        Format input data into UI-ready string.
        
        Args:
            data: Input data to format (type varies by formatter)
        
        Returns:
            Formatted string ready for UI display
        """
        pass

