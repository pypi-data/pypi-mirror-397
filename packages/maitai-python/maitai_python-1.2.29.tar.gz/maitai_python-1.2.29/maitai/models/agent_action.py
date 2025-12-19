# codegen: frontend, sdk

"""
Models for agent action request/response tracking.

These models support unified tracking of both LLM and API agent action executions.
"""

import time
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ApiRequest(BaseModel):
    """Metadata for API action requests (analogous to ChatCompletionRequest)"""
    
    id: Optional[int] = None
    date_created: Optional[int] = None
    request_id: str
    company_id: int
    application_id: int
    session_id: str
    reference_id: Optional[str] = None
    
    # Request metadata
    http_method: str
    url: str
    headers: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    timeout_ms: Optional[int] = None
    
    # Metadata
    meta: Dict[str, Any] = Field(default_factory=dict)


class ApiResponse(BaseModel):
    """Metadata for API action responses (analogous to ChatCompletionResponse)"""
    
    id: Optional[int] = None
    request_id: str
    date_created: Optional[int] = None
    
    # Response metadata
    status_code: int
    response_time_ms: Optional[int] = None
    headers: Optional[Dict[str, Any]] = None
    
    # Response body (raw JSON response body only, not headers/status)
    response_body: Optional[str] = None
    
    # Error tracking
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    # Metadata
    meta: Dict[str, Any] = Field(default_factory=dict)


class AgentActionRequest(BaseModel):
    """Unified tracking for all agent action executions (LLM and API)"""
    
    id: Optional[int] = None
    date_created: Optional[int] = None
    
    # Links to agent action and task
    agent_action_id: int
    task_id: str
    session_id: str
    
    # Action identification
    action_type: str  # 'LLM_CALL' or 'API_CALL'
    
    # Reference to the actual request (chat_completion_request.request_id OR api_request.request_id)
    underlying_request_id: str
    
    # Arguments passed to the action
    action_args: Optional[Dict[str, Any]] = None
    
    # Metadata
    meta: Dict[str, Any] = Field(default_factory=dict)


class AgentActionResponse(BaseModel):
    """Unified response tracking for all agent actions (based on DirectToolResult)"""
    
    id: Optional[int] = None
    agent_action_request_id: int
    date_created: Optional[int] = None
    
    # High-level response metadata (from DirectToolResult)
    status: str  # SUCCESS, ERROR, TIMEOUT, etc.
    feedback: Optional[str] = None
    
    # Timing
    response_time_ms: Optional[int] = None
    
    # Error tracking
    error_message: Optional[str] = None
    
    # Response body (populated from DynamoDB for API calls, chat_completion_response for LLM calls)
    response_body: Optional[str] = None
    
    # Metadata (action-type-specific data)
    # For API calls: status_code, headers, url
    # For LLM calls: model, tokens, correction_applied, etc.
    meta: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Final response returned by agent execution (what the user receives)"""
    
    id: Optional[int] = None
    date_created: Optional[int] = None
    
    # Link to agent request
    agent_request_id: int
    task_id: str
    
    # Response status
    status: str  # COMPLETED, ERROR, REJECTED, etc.
    
    # Link to final action that produced the response
    final_agent_action_request_id: Optional[int] = None
    
    # Response content
    response_text: Optional[str] = None
    
    # Execution metadata
    feedback: Optional[str] = None
    error_message: Optional[str] = None
    
    # Timing
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    execution_time_ms: Optional[int] = None
    first_token_time: Optional[int] = None
    iterations_used: Optional[int] = None
    
    # Delegation intent
    delegation_intent: Optional[str] = None
    
    # Metadata
    meta: Dict[str, Any] = Field(default_factory=dict)

