# codegen: frontend, sdk
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AgentRoutingRule(BaseModel):
    """
    Pydantic model for agent routing rules (embeddings stored at condition level).
    """

    id: Optional[int] = None
    date_created: Optional[float] = None
    date_updated: Optional[float] = None
    agent_id: int
    rule_index: Optional[int] = None
    label: Optional[str] = None
    condition_expression: str
    condition_expression_template: Optional[str] = None
    condition_meta: Dict[str, Any] = Field(default_factory=dict)
    route_type: Literal["agent", "action", "llm", "none"]
    route_agent_id: Optional[int] = None
    route_action_id: Optional[int] = None
    enabled: bool = True
    conditions: List["AgentRoutingRuleCondition"] = Field(default_factory=list)


class AgentRoutingRuleCondition(BaseModel):
    id: Optional[int] = None
    date_created: Optional[float] = None
    date_updated: Optional[float] = None

    rule_id: int
    condition_index: Optional[int] = None

    target_type: Literal["request", "state"]
    variable_path: str

    operator: Literal[
        "equals",
        "not_equals",
        "gt",
        "gte",
        "lt",
        "lte",
        "like",
        "matches",
        "sem_match",
        "sem_similarity",
        "classify",
        "not_classify",
        "sentiment",
        "is_null",
        "is_not_null",
    ]

    value_text: Optional[str] = None
    value_number: Optional[float] = None
    value_bool: Optional[bool] = None
    comparison_op: Optional[
        Literal[">", "\u003e=", "=", "\u003c=", "\u003c", "IS", "IS_NOT"]
    ] = None
    threshold_number: Optional[float] = None
    enabled: bool = True
    embedding: Optional[List[float]] = None


class AgentRoutingResult(BaseModel):
    """
    Unified tracking of all routing decisions (both rules and LLM modes).
    One record per routing decision (route_completion call).
    """

    id: Optional[int] = None
    date_created: Optional[float] = None

    # Agent and request context
    agent_id: int
    task_id: str
    session_id: str
    request_id: str

    # Routing mode and type
    routing_mode: Literal["rules", "llm"]
    evaluation_mode: Literal["foreground", "background"]

    # Normalized routing results (applies to both rules and LLM modes)
    selected_rule_id: Optional[int] = None
    selected_action_id: Optional[int] = None
    selected_agent_id: Optional[int] = None

    # Fallback information (only for rules mode when no match)
    fallback_type: Optional[Literal["llm", "none"]] = None

    # Performance metrics
    duration_ms: Optional[int] = None

    # Mode-specific details and variables
    meta: Dict[str, Any] = Field(default_factory=dict)


class AgentRoutingRuleEvaluation(BaseModel):
    """
    Detailed evaluation results for individual rules (rules mode only).
    One record per rule evaluated during a routing decision.
    """

    id: Optional[int] = None
    date_created: Optional[float] = None

    # Link to parent routing result
    routing_result_id: int

    # Rule identification (denormalized for query performance)
    rule_id: Optional[int] = None
    rule_index: int
    rule_label: Optional[str] = None

    # Evaluation results
    passed: bool
    evaluation_order: int
    evaluation_duration_ms: Optional[int] = None

    # Condition summary
    conditions_total: int
    conditions_passed: int

    # Logic expression with pass/fail indicators
    logic_expression: Optional[str] = None

    # Error information
    error: Optional[str] = None

    # Additional metadata
    meta: Dict[str, Any] = Field(default_factory=dict)


class AgentRoutingRuleConditionEvaluation(BaseModel):
    """
    Detailed evaluation results for individual conditions within rules.
    One record per condition evaluated during a rule evaluation.
    """

    id: Optional[int] = None
    date_created: Optional[float] = None

    # Link to parent rule evaluation
    rule_evaluation_id: int

    # Condition identification
    condition_id: Optional[int] = None
    condition_index: int

    # Evaluation results
    passed: bool
    evaluation_duration_ms: Optional[int] = None

    # Target variable information
    target_variable_label: str
    target_variable_value: Optional[str] = None

    # Comparison details
    operator: str
    comparison_value: Optional[str] = None

    # Error information
    error: Optional[str] = None

    # Additional metadata (includes semantic/classification results)
    meta: Dict[str, Any] = Field(default_factory=dict)
