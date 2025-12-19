# codegen: sdk
"""
Enums for the maitai_models.agent module.

This file contains all enum definitions used across the agent system.
"""

from enum import Enum


class AgentStatus(Enum):
    """Status values for agents."""

    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class AgentActionStatus(Enum):
    """Status values for agent actions."""

    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class AgentActionType(Enum):
    """Types of agent actions."""

    API_CALL = "api_call"
    LLM_CALL = "llm_call"
    WEBHOOK = "webhook"
    WEBHOOK_CREATION = "webhook_creation"
    INTEGRATION = "integration"
    CONVERSATION_FLOW = "conversation_flow"


class ActionResultType(Enum):
    """Types of result handling for both actions and sub-agent delegations."""

    GATHER_INFO = "gather_info"  # Use result content for next steps in ongoing strategy (actions + sub-agents)
    COMPLETE_TASK = (
        "complete_task"  # Only care about success/failure status (actions + sub-agents)
    )
    GET_FINAL = "get_final"  # Use result as final response (sub-agents only)


class ToolType(Enum):
    """Types of tools available to agents."""

    ORCHESTRATION = "orchestration"  # Planning and strategy (@orchestration_call)
    PROCESSING = "processing"  # Execution and state management (@processing_call)
    ACTION = "action"  # AgentAction execution (API calls, LLM calls, etc.)
    SUB_AGENT = "sub_agent"  # Calls to other agents


class LoopStatus(Enum):
    """Status of the agent loop."""

    CONTINUE = "CONTINUE"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


class AgentActionInvocationMode(Enum):
    """Invocation mode for agent actions: whether results are user-facing or context-only."""

    FOREGROUND = "foreground"  # Output is surfaced to the user (response-facing)
    BACKGROUND = "background"  # Updates context/state only (not directly surfaced)
