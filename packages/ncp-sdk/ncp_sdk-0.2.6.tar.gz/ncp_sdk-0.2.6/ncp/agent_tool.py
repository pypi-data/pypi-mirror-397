"""AgentTool - Wraps an Agent as a Tool for multi-agent composition.

This module provides the AgentTool class that allows agents to be used as tools
by other agents, enabling multi-agent orchestration patterns.

Example:
    >>> from ncp import Agent, AgentTool
    >>>
    >>> sql_agent = Agent(name="sql_agent", description="SQL expert", instructions="...")
    >>> sql_tool = AgentTool(sql_agent)
    >>>
    >>> orchestrator = Agent(
    ...     name="orchestrator",
    ...     tools=[sql_tool],  # Use agent as a tool
    ... )
"""

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from .tool import Tool

if TYPE_CHECKING:
    from .agent import Agent


class AgentTool(Tool):
    """Wraps an Agent as a Tool for multi-agent composition.

    AgentTool allows an agent to be used as a tool by another agent,
    enabling hierarchical multi-agent systems where a parent agent
    can delegate work to specialized child agents.

    Each execution runs the child agent with fresh context (no conversation
    history sharing) and returns only the final text response.

    Attributes:
        agent: The wrapped Agent instance
        name: Tool name (defaults to agent name with '_tool' suffix)
        description: Tool description (defaults to agent description)

    Example:
        >>> from ncp import Agent, AgentTool
        >>>
        >>> # Create a specialized agent
        >>> math_agent = Agent(
        ...     name="math_expert",
        ...     description="Solves complex math problems",
        ...     instructions="You are a math expert..."
        ... )
        >>>
        >>> # Wrap it as a tool
        >>> math_tool = AgentTool(math_agent)
        >>>
        >>> # Or with custom name/description
        >>> math_tool = AgentTool(
        ...     math_agent,
        ...     name="calculator",
        ...     description="Delegate math problems to the math expert"
        ... )
        >>>
        >>> # Use in an orchestrator agent
        >>> orchestrator = Agent(
        ...     name="assistant",
        ...     description="General assistant",
        ...     instructions="You help users with various tasks...",
        ...     tools=[math_tool]  # Can delegate to math_agent
        ... )
    """

    def __init__(
        self,
        agent: "Agent",
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Initialize an AgentTool.

        Args:
            agent: The Agent to wrap as a tool
            name: Optional custom name (defaults to '{agent.name}_tool')
            description: Optional custom description (defaults to agent's description)

        Raises:
            ValueError: If agent is None
        """
        if agent is None:
            raise ValueError("Agent cannot be None")

        self.agent = agent

        # Use provided name or derive from agent
        tool_name = name or f"{agent.name}_tool"
        tool_description = description or agent.description

        # Initialize base Tool with a placeholder func
        # Actual execution happens on the platform
        super().__init__(
            name=tool_name,
            description=tool_description,
            func=lambda query: None,  # Placeholder, not used in SDK
        )

        # Override the schema to have a single 'query' parameter
        self._schema = self._generate_agent_tool_schema()

        # Status callback for forwarding child agent events to parent
        # This is used by the platform during execution
        self._status_callback: Optional[Callable] = None

    def set_status_callback(self, callback: Optional[Callable]) -> None:
        """Set callback for forwarding child agent status events to parent.

        When set, this callback will be invoked with status data whenever
        the child agent makes a tool call, allowing the parent executor to
        emit status updates to the UI.

        Note: This is used by the platform during execution. In the SDK,
        this is a stub for API compatibility.

        Args:
            callback: Function that receives status data, or None to disable
        """
        self._status_callback = callback

    def _generate_agent_tool_schema(self) -> Dict[str, Any]:
        """Generate the schema for this agent tool.

        Returns:
            OpenAI function calling schema with a single 'query' parameter
        """
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The task or question to delegate to this agent",
                    }
                },
                "required": ["query"],
            },
        }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"AgentTool(name={self.name}, agent={self.agent.name})"
