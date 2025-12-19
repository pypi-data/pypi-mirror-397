# codegen: frontend, sdk
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from pydantic import BaseModel, Field

from .enum import (
    ActionResultType,
    AgentActionInvocationMode,
    AgentActionStatus,
    AgentActionType,
    AgentStatus,
)


class Agent(BaseModel):
    """
    Pydantic model for agents representing the complete data structure
    for database communication between backend and frontend.
    """

    # Core database fields
    id: Optional[int] = -1
    date_created: Optional[float] = 0
    application_id: int
    agent_name: str
    description: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    status: AgentStatus = AgentStatus.ENABLED

    # Configuration fields
    agent_config: Optional[Dict[str, Any]] = None
    max_iterations: int = 10

    # Execution state fields (runtime state, not stored in database)
    strategy: Optional[Dict[str, Any]] = Field(default_factory=dict)
    state: Optional[Dict[str, Any]] = Field(default_factory=dict)
    action_log: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    scratchpad: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    # Strategy prompts configuration
    strategy_prompts: Optional[Dict[str, str]] = Field(default_factory=dict)

    # Agent hierarchy and path (runtime fields)
    agent_path: str = ""
    base_url: Optional[str] = (
        None  # Runtime field extracted from agent_config and cascaded from parent
    )

    # Relationships and additional fields from joins
    actions: List["AgentAction"] = Field(default_factory=list)  # AgentAction objects
    sub_agents: List["Agent"] = Field(default_factory=list)  # Sub-agent relationships

    # Statistics and counts from database joins
    conversation_count: Optional[int] = 0
    intent_count: Optional[int] = 0
    action_count: Optional[int] = 0
    sub_agent_count: Optional[int] = 0

    # Application info from joins
    application_name: Optional[str] = None

    # Execution metrics (runtime only)
    last_execution_time: Optional[float] = None
    last_execution_status: Optional[str] = None
    total_executions: Optional[int] = 0
    success_rate: Optional[float] = None
    replicas: int = 1

    def print_tree(self, indent: int = 0) -> str:
        """Return a pretty-printed tree of the agent hierarchy and actions.

        - Sub-agents are marked as [SA]
        - Actions are marked as [AA] (API/Integration/Webhook) or [LA] (LLM)
        """
        lines: List[str] = []

        def action_label(action: "AgentAction") -> str:
            try:
                a_type = getattr(action, "action_type", None)
                value = getattr(a_type, "value", a_type)
                invocation_mode = getattr(action, "invocation_mode", None)

                # Get shortened invocation mode
                mode_short = ""
                if invocation_mode:
                    mode_value = getattr(invocation_mode, "value", invocation_mode)
                    if mode_value == AgentActionInvocationMode.BACKGROUND.value:
                        mode_short = "BG"
                    elif mode_value == AgentActionInvocationMode.FOREGROUND.value:
                        mode_short = "FG"

                if value == AgentActionType.LLM_CALL.value:
                    return f"[LA {mode_short}]" if mode_short else "[LA]"
                # Treat API_CALL/WEBHOOK/INTEGRATION and any other non-LLM as API-type
                return f"[AA {mode_short}]" if mode_short else "[AA]"
            except Exception:
                return "[AA]"

        def add_children(agent: "Agent", prefix: str) -> None:
            # Build ordered children: actions first, then sub-agents
            action_nodes: List[Tuple[str, "AgentAction"]] = [
                ("action", a) for a in (agent.actions or [])
            ]
            subagent_nodes: List[Tuple[str, "Agent"]] = [
                ("agent", sa) for sa in (agent.sub_agents or [])
            ]
            children: List[Tuple[str, Union["AgentAction", "Agent"]]] = action_nodes + subagent_nodes  # type: ignore[assignment]

            for idx, (node_type, node) in enumerate(children):
                is_last = idx == len(children) - 1
                connector = "└── " if is_last else "├── "
                if node_type == "action":
                    act = cast("AgentAction", node)
                    label = action_label(act)
                    name = getattr(act, "action_name", "(unnamed action)")
                    lines.append(f"{prefix}{connector}{label} {name}")
                else:
                    # Sub-agent: call its own print_tree and merge
                    sa = cast("Agent", node)
                    subtree_lines = (sa.print_tree(indent=0) or "").split("\n")
                    root_name = (
                        subtree_lines[0]
                        if subtree_lines
                        else getattr(sa, "agent_name", "(unnamed agent)")
                    )
                    lines.append(f"{prefix}{connector}[SA] {root_name}")
                    child_prefix = f"{prefix}{'    ' if is_last else '│   '}"
                    for sub_line in subtree_lines[1:]:
                        lines.append(f"{child_prefix}{sub_line}")

        # Root line (do not mark as [SA])
        lines.append(f"{(' ' * indent)}{self.agent_name}")
        add_children(self, prefix=(" " * indent))
        return "\n".join(lines)


class AgentAction(BaseModel):
    """
    Pydantic model for agent actions representing API calls, LLM calls, etc.
    """

    # Core database fields
    id: Optional[int] = -1
    date_created: Optional[float] = 0
    agent_id: int
    action_name: str
    action_type: AgentActionType
    description: str
    status: AgentActionStatus = AgentActionStatus.ENABLED
    is_default: bool = (
        False  # Whether this is the default action when not using reasoning
    )
    action_result_type: ActionResultType = (
        ActionResultType.GATHER_INFO
    )  # How to handle the action result
    action_config: Optional[Dict[str, Any]] = (
        None  # Configuration for the action (API, LLM, etc.)
    )
    meta: Dict[str, Any] = Field(default_factory=dict)

    # Invocation behavior
    invocation_mode: AgentActionInvocationMode = Field(
        default=AgentActionInvocationMode.FOREGROUND
    )

    # Execution metrics (runtime only)
    last_execution_time: Optional[float] = None
    last_execution_status: Optional[str] = None
    total_executions: Optional[int] = 0
    success_rate: Optional[float] = None


Agent.model_rebuild()
AgentAction.model_rebuild()
