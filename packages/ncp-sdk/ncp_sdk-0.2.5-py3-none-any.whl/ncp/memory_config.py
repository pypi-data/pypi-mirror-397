"""Memory configuration for NCP agents."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class STMStrategy(Enum):
    """Short-term memory strategies for managing conversation context."""

    LAST_N_MESSAGES = "last_n_messages"
    TOKEN_WINDOW = "token_window"
    # Future strategies can be added here:
    # ADAPTIVE_SUMMARY = "adaptive_summary"
    # HYBRID = "hybrid"


@dataclass
class MemoryConfig:
    """Configuration for agent memory management.

    Controls how agents manage conversation history within the LLM context window.
    Short-term memory (STM) is enabled by default to prevent unbounded context growth.

    Attributes:
        stm_enabled: Whether short-term memory is enabled. Default: True
            - True: Apply STM strategy to manage conversation history
            - False: Stateless mode - no conversation history (only system + current message)
        stm_strategy: Strategy to use for managing context window. Default: TOKEN_WINDOW
        stm_config: Strategy-specific configuration. Default for TOKEN_WINDOW:
            - max_context_tokens: Maximum tokens in model context (default: 131072)
            - generation_buffer: Fraction reserved for generation (default: 0.25)
            - tool_tokens: Tokens reserved for tool schemas (default: 0, updated dynamically)

    Note:
        The first system message is always preserved regardless of configuration.
        This behavior is not user-configurable to ensure agent instructions remain intact.

    Example:
        >>> # Use default settings (TOKEN_WINDOW with 25% generation buffer)
        >>> config = MemoryConfig()

        >>> # Smaller context model with 30% buffer
        >>> config = MemoryConfig(stm_config={
        ...     "max_context_tokens": 32768,
        ...     "generation_buffer": 0.30
        ... })

        >>> # Use LAST_N_MESSAGES strategy (fixed turn count)
        >>> config = MemoryConfig(
        ...     stm_strategy=STMStrategy.LAST_N_MESSAGES,
        ...     stm_config={"max_messages": 20, "include_tools": True}
        ... )

        >>> # Stateless mode (no conversation history, each request independent)
        >>> config = MemoryConfig(stm_enabled=False)
    """

    stm_enabled: bool = True
    stm_strategy: STMStrategy = STMStrategy.TOKEN_WINDOW
    stm_config: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_context_tokens": 131072,
            "generation_buffer": 0.25,
            "tool_tokens": 0,
        }
    )

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.stm_enabled:
            if self.stm_strategy == STMStrategy.TOKEN_WINDOW:
                # Validate max_context_tokens
                max_context_tokens = self.stm_config.get("max_context_tokens", 131072)
                if not isinstance(max_context_tokens, int) or max_context_tokens < 1:
                    raise ValueError(
                        f"max_context_tokens must be a positive integer, got: {max_context_tokens}"
                    )

                # Validate generation_buffer
                generation_buffer = self.stm_config.get("generation_buffer", 0.25)
                if not isinstance(generation_buffer, (int, float)) or not (
                    0.1 <= generation_buffer <= 0.5
                ):
                    raise ValueError(
                        f"generation_buffer must be between 0.1 and 0.5, got: {generation_buffer}"
                    )

                # Validate tool_tokens
                tool_tokens = self.stm_config.get("tool_tokens", 0)
                if not isinstance(tool_tokens, int) or tool_tokens < 0:
                    raise ValueError(
                        f"tool_tokens must be a non-negative integer, got: {tool_tokens}"
                    )

            elif self.stm_strategy == STMStrategy.LAST_N_MESSAGES:
                # Validate max_messages
                max_messages = self.stm_config.get("max_messages", 20)
                if not isinstance(max_messages, int) or max_messages < 1:
                    raise ValueError(
                        f"max_messages must be a positive integer, got: {max_messages}"
                    )

                # Validate include_tools (optional, default True)
                include_tools = self.stm_config.get("include_tools", True)
                if not isinstance(include_tools, bool):
                    raise ValueError(
                        f"include_tools must be a boolean, got: {include_tools}"
                    )
