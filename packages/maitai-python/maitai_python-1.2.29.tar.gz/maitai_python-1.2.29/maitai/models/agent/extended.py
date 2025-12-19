# codegen: sdk

"""
Agent models for the maitai_models.agent module.

This file contains all the Pydantic models related to agents, breaking the
circular dependency with maitai_models.agent.
"""
import json
import re
import time
import uuid
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, List, Optional, Union

from pydantic import AliasChoices, BaseModel, Field

from maitai.models.agent.base import Agent
from maitai.models.chat import ChatCompletionParams, ChatCompletionResponse

from .enum import ActionResultType, LoopStatus, ToolType


class DirectToolResult(BaseModel):
    """Result from a direct tool execution."""

    status: str
    feedback: Optional[str] = None
    result: Any = None


class ActionError(BaseModel):
    """Error result from an action."""

    status: str = "ERROR"
    error: Optional[str] = None


class TaskStateUpdate(BaseModel):
    """Update to task state."""

    date_created: int
    key_updated: str
    value_previous: Any
    value_updated: Any


class TaskState(BaseModel):
    """Agent task state management."""

    state: Dict[str, Any] = Field(default_factory=dict)
    updates: List[TaskStateUpdate] = Field(default_factory=list)

    def update(self, state_key: str, new_value: Any) -> None:
        """Update the state of the agent."""
        old_value = self.state.get(state_key)
        self.updates.append(
            TaskStateUpdate(
                date_created=int(time.time() * 1000),
                key_updated=state_key,
                value_previous=old_value,
                value_updated=new_value,
            )
        )
        self.state[state_key] = new_value


class ActionLogEntry(BaseModel):
    """Single entry that can contain nested action logs."""

    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    agent_path: str
    action_name: str
    action_type: str  # "orchestration", "processing", "action", "sub_agent"

    # Execution details
    status: str = "RUNNING"
    start_time: int = Field(default_factory=lambda: int(time.time() * 1000))
    end_time: Optional[int] = None
    execution_time_ms: int = 0
    feedback: Optional[str] = None
    error_details: Optional[str] = None
    action_args: Optional[Dict[str, Any]] = None

    # Nested action log for sub-agent executions
    sub_actions: Optional["ActionLog"] = None

    def complete(
        self,
        status: str = "SUCCESS",
        feedback: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """Mark the action as completed."""
        self.end_time = int(time.time() * 1000)
        self.execution_time_ms = self.end_time - self.start_time
        self.status = status
        if feedback:
            self.feedback = feedback
        if error:
            self.error_details = error


class ActionLog(BaseModel):
    """Simple list-based action log that can be nested."""

    entries: List[ActionLogEntry] = Field(default_factory=list)

    def add_action(
        self,
        agent_name: str,
        agent_path: str,
        action_name: str,
        action_type: str,
        action_args: Optional[Dict[str, Any]] = None,
    ) -> ActionLogEntry:
        """Add a new action entry."""
        entry = ActionLogEntry(
            agent_name=agent_name,
            agent_path=agent_path,
            action_name=action_name,
            action_type=action_type,
            action_args=action_args or {},
        )
        self.entries.append(entry)
        return entry

    def get_flat_list(self) -> List[ActionLogEntry]:
        """Get all actions as a flat list, including nested actions."""
        result = []
        for entry in self.entries:
            result.append(entry)
            if entry.sub_actions:
                result.extend(entry.sub_actions.get_flat_list())
        return result

    def to_formatted_string(self) -> str:
        """Return a formatted string output of the action log."""
        lines = []
        for entry in self.get_flat_list():
            # Format timestamp from start_time (milliseconds)
            timestamp = (
                datetime.fromtimestamp(entry.start_time / 1000).strftime("%I:%M:%S.%f")[
                    :-3
                ]
                + " "
                + datetime.fromtimestamp(entry.start_time / 1000).strftime("%p")
            )

            # Build action args string if they exist
            args_str = ""
            if entry.action_args:
                ## Remove the __action_instance_id from the action args
                action_args = entry.action_args.copy()
                action_args.pop("__action_instance_id", None)
                args_str = f"({action_args})"

            # Build feedback string if it exists
            feedback_str = ""
            if entry.status != "SUCCESS" and entry.feedback:
                feedback_str = f" - {entry.feedback}"

            # Format the line
            line = f"{timestamp} [{entry.agent_name}] `{entry.action_name}{args_str}`: {entry.status}{feedback_str}"
            lines.append(line)

        return "\n".join(lines)


class ScratchpadEntry(BaseModel):
    """Single entry that can contain nested scratchpad."""

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    agent_path: str
    date_created: int = Field(default_factory=lambda: int(time.time() * 1000))
    entry_value: str
    entry_type: str = "note"  # "note", "insight", "decision", "result", "delegation"

    # Optional nested scratchpad for sub-agent notes
    sub_scratchpad: Optional["Scratchpad"] = None

    # Optional link to related action
    related_action_id: Optional[str] = None


class ScratchpadNoteItem(BaseModel):
    """Single note item from LLM response for scratchpad."""

    entry_type: str = "note"
    note: str


class ScratchpadNotesResponse(BaseModel):
    """Expected format for scratchpad notes response from LLM.

    Format: {"notes": [{"entry_type": "...", "note": "..."}, ...]}
    """

    notes: List[ScratchpadNoteItem] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScratchpadNotesResponse":
        """Create from dict, extracting notes list."""
        raw_notes = data.get("notes", [])
        if not isinstance(raw_notes, list):
            raw_notes = []
        notes = []
        for item in raw_notes:
            if isinstance(item, dict):
                notes.append(
                    ScratchpadNoteItem(
                        entry_type=str(item.get("entry_type", "note")),
                        note=str(item.get("note", "")),
                    )
                )
        return cls(notes=notes)

    @classmethod
    def from_list(cls, data: List[Any]) -> "ScratchpadNotesResponse":
        """Create from list (fallback for when LLM returns array directly)."""
        if not isinstance(data, list):
            return cls(notes=[])
        notes = []
        for item in data:
            if isinstance(item, dict):
                notes.append(
                    ScratchpadNoteItem(
                        entry_type=str(item.get("entry_type", "note")),
                        note=str(item.get("note", "")),
                    )
                )
        return cls(notes=notes)

    @classmethod
    def parse_from_text(cls, text: str) -> Optional["ScratchpadNotesResponse"]:
        """
        Clean and parse scratchpad response text, handling various formats:
        - Expected: {"notes": [...]}
        - Fallback: [...] (array directly)
        - Handles markdown code blocks, extra whitespace, etc.
        """
        if not text or not text.strip():
            return None

        # Step 1: Remove markdown code block markers
        cleaned = text.strip()
        cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^```\s*", "", cleaned)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        # Step 2: Try to parse as JSON directly
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return cls.from_dict(parsed)
            elif isinstance(parsed, list):
                return cls.from_list(parsed)
        except json.JSONDecodeError:
            pass

        # Step 3: Try to extract JSON object from text
        try:
            obj_match = re.search(
                r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", cleaned, re.DOTALL
            )
            if obj_match:
                parsed = json.loads(obj_match.group(0))
                if isinstance(parsed, dict):
                    return cls.from_dict(parsed)
        except (json.JSONDecodeError, AttributeError):
            pass

        # Step 4: Try to extract JSON array from text
        try:
            array_match = re.search(
                r"\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]", cleaned, re.DOTALL
            )
            if array_match:
                parsed = json.loads(array_match.group(0))
                if isinstance(parsed, list):
                    return cls.from_list(parsed)
        except (json.JSONDecodeError, AttributeError):
            pass

        # Step 5: Try more aggressive extraction (greedy)
        try:
            obj_match = re.search(r"\{[\s\S]*\}", cleaned)
            if obj_match:
                parsed = json.loads(obj_match.group(0))
                if isinstance(parsed, dict):
                    return cls.from_dict(parsed)
        except json.JSONDecodeError:
            pass

        try:
            array_match = re.search(r"\[[\s\S]*\]", cleaned)
            if array_match:
                parsed = json.loads(array_match.group(0))
                if isinstance(parsed, list):
                    return cls.from_list(parsed)
        except json.JSONDecodeError:
            pass

        return None


class Scratchpad(BaseModel):
    """Simple list-based scratchpad that can be nested."""

    entries: List[ScratchpadEntry] = Field(default_factory=list)

    def add_entry(
        self,
        agent_name: str,
        agent_path: str,
        entry_value: str,
        entry_type: str = "note",
        related_action_id: Optional[str] = None,
    ) -> ScratchpadEntry:
        """Add a new scratchpad entry."""
        entry = ScratchpadEntry(
            agent_name=agent_name,
            agent_path=agent_path,
            entry_value=entry_value,
            entry_type=entry_type,
            related_action_id=related_action_id,
        )
        self.entries.append(entry)
        return entry

    def get_flat_list(self) -> List[ScratchpadEntry]:
        """Get all entries as a flat list, including nested entries."""
        result = []
        for entry in self.entries:
            result.append(entry)
            if entry.sub_scratchpad:
                result.extend(entry.sub_scratchpad.get_flat_list())
        return result

    def to_formatted_string(self) -> str:
        """Return a formatted string output of the scratchpad."""
        lines = []
        for entry in self.get_flat_list():
            # Format timestamp from date_created (milliseconds)
            timestamp = (
                datetime.fromtimestamp(entry.date_created / 1000).strftime(
                    "%I:%M:%S.%f"
                )[:-3]
                + " "
                + datetime.fromtimestamp(entry.date_created / 1000).strftime("%p")
            )

            # Build related action string if it exists
            related_action_str = ""
            if entry.related_action_id:
                related_action_str = f" (related to: {entry.related_action_id})"

            # Format the line
            line = f"{timestamp} [{entry.agent_name}] `{entry.entry_type}`: {entry.entry_value}{related_action_str}"
            lines.append(line)

        return "\n".join(lines)

    def to_string(self) -> str:
        """Get all entries as a string."""
        return "\n".join([entry.entry_value for entry in self.get_flat_list()])


class WorkspaceEntry(BaseModel):
    """Raw result text storage for actions and sub-agent results.

    Each entry represents work done - either an action execution (ActionResult) or
    a sub-agent execution (AgentResponse). AgentResponse contains workspace recursively,
    creating a natural tree structure.
    """

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    agent_path: str
    date_created: int = Field(default_factory=lambda: int(time.time() * 1000))
    source_type: str  # "action" | "sub_agent"
    action_name: str
    status: Optional[str] = None
    feedback: Optional[str] = None
    delegation_intent: Optional[str] = None

    # Store either ActionResult (for actions) or AgentResponse (for sub-agents)
    # AgentResponse contains workspace recursively, creating a natural tree structure
    result: Optional[Union["ActionResult", "AgentResponse"]] = None


class Workspace(BaseModel):
    """Workspace holds raw data blobs that can be referenced during response.

    This is intended to be shared between an agent's parent and all of its descendants
    for the lifetime of a task execution.
    """

    entries: List[WorkspaceEntry] = Field(default_factory=list)
    # Root agent_path that initiated this branch workspace
    branch_root_path: Optional[str] = None

    def add_result(
        self,
        *,
        agent_name: str,
        agent_path: str,
        source_type: str,
        action_name: str,
        status: Optional[str] = None,
        feedback: Optional[str] = None,
        delegation_intent: Optional[str] = None,
        result: Optional[Union["ActionResult", "AgentResponse"]] = None,
    ) -> WorkspaceEntry:
        entry = WorkspaceEntry(
            agent_name=agent_name,
            agent_path=agent_path,
            source_type=source_type,
            action_name=action_name,
            status=status,
            feedback=feedback,
            delegation_intent=delegation_intent,
            result=result,
        )
        self.entries.append(entry)
        return entry

    def get_flat_list(self) -> List[WorkspaceEntry]:
        """Get all entries as a flat list, including nested entries from sub-agent responses."""
        result = []
        for entry in self.entries:
            result.append(entry)
            # If entry has a result that is an AgentResponse with workspace, include those entries recursively
            # (AgentResponse contains workspace, which creates the tree structure)
            if (
                entry.result
                and isinstance(entry.result, AgentResponse)
                and entry.result.workspace
            ):
                result.extend(entry.result.workspace.get_flat_list())
        return result

    def to_formatted_string(self, max_entries: Optional[int] = None) -> str:
        lines: List[str] = []
        entries = self.get_flat_list()
        if max_entries is not None and len(entries) > max_entries:
            entries = entries[-max_entries:]
        for entry in entries:
            timestamp = (
                datetime.fromtimestamp(entry.date_created / 1000).strftime(
                    "%I:%M:%S.%f"
                )[:-3]
                + " "
                + datetime.fromtimestamp(entry.date_created / 1000).strftime("%p")
            )
            # Extract text from result object if available
            raw_preview = ""
            if entry.result:
                try:
                    result_obj = entry.result
                    if hasattr(result_obj, "result"):
                        result_value = getattr(result_obj, "result", None)
                        if result_value:
                            if isinstance(result_value, dict):
                                if "response" in result_value:
                                    raw_preview = str(result_value["response"])
                                else:
                                    raw_preview = str(result_value)
                            else:
                                raw_preview = str(result_value)
                    elif hasattr(result_obj, "feedback"):
                        raw_preview = str(getattr(result_obj, "feedback", ""))
                except Exception:
                    pass
            if entry.feedback:
                raw_preview = entry.feedback
            if len(raw_preview) > 2000:
                raw_preview = raw_preview[:2000] + "…"
            # Only time and raw result dump
            line = f"{timestamp}\n{raw_preview}"
            lines.append(line)
        return "\n".join(lines)

    def to_tree_string(self, max_entries: Optional[int] = None, indent: int = 0) -> str:
        """Format workspace entries as a hierarchical tree, surfacing results from actions and sub-agents.

        This traverses the workspace tree recursively, showing:
        - Action results (ActionResult) with their results
        - Sub-agent responses (AgentResponse) with their workspace nested

        Args:
            max_entries: Maximum number of entries to show (applied at top level)
            indent: Current indentation level for nested entries

        Returns:
            Formatted string representing the workspace tree
        """
        lines: List[str] = []
        entries = self.entries
        if max_entries is not None and indent == 0 and len(entries) > max_entries:
            entries = entries[-max_entries:]

        for entry in entries:
            indent_str = "  " * indent
            timestamp = (
                datetime.fromtimestamp(entry.date_created / 1000).strftime(
                    "%I:%M:%S.%f"
                )[:-3]
                + " "
                + datetime.fromtimestamp(entry.date_created / 1000).strftime("%p")
            )

            # Format entry header
            source_indicator = f"[{entry.source_type}]"
            lines.append(
                f"{indent_str}{timestamp} {source_indicator} {entry.action_name} ({entry.agent_name})"
            )
            if entry.status:
                lines.append(f"{indent_str}  Status: {entry.status}")
            if entry.feedback:
                feedback_preview = entry.feedback
                if len(feedback_preview) > 200:
                    feedback_preview = feedback_preview[:200] + "…"
                lines.append(f"{indent_str}  Feedback: {feedback_preview}")

            # Extract and format result content
            if entry.result:
                # Check if it's an ActionResult (has tool_type attribute)
                result_obj = entry.result
                if hasattr(result_obj, "tool_type") and hasattr(
                    result_obj, "action_name"
                ):
                    # This is an ActionResult - extract result value
                    try:
                        result_value = getattr(result_obj, "result", None)
                        if result_value:
                            lines.append(f"{indent_str}  Result:")
                            try:
                                if isinstance(result_value, dict):
                                    # Try to extract meaningful content
                                    if "response" in result_value:
                                        response_content = result_value["response"]
                                        if isinstance(response_content, str):
                                            content_preview = response_content
                                            if len(content_preview) > 500:
                                                content_preview = (
                                                    content_preview[:500] + "…"
                                                )
                                            lines.append(
                                                f"{indent_str}    {content_preview}"
                                            )
                                        elif isinstance(response_content, dict):
                                            result_str = str(response_content)
                                            if len(result_str) > 500:
                                                result_str = result_str[:500] + "…"
                                            lines.append(
                                                f"{indent_str}    {result_str}"
                                            )
                                    else:
                                        # Show the whole result dict, truncated
                                        result_str = str(result_value)
                                        if len(result_str) > 500:
                                            result_str = result_str[:500] + "…"
                                        lines.append(f"{indent_str}    {result_str}")
                                elif isinstance(result_value, str):
                                    content_preview = result_value
                                    if len(content_preview) > 500:
                                        content_preview = content_preview[:500] + "…"
                                    lines.append(f"{indent_str}    {content_preview}")
                                else:
                                    result_str = str(result_value)
                                    if len(result_str) > 500:
                                        result_str = result_str[:500] + "…"
                                    lines.append(f"{indent_str}    {result_str}")
                            except Exception:
                                lines.append(
                                    f"{indent_str}    (unable to format result)"
                                )
                    except Exception:
                        pass
                # Check if it's an AgentResponse (has workspace and agent_name but no tool_type)
                elif (
                    hasattr(result_obj, "workspace")
                    and hasattr(result_obj, "agent_name")
                    and not hasattr(result_obj, "tool_type")
                ):
                    # This is an AgentResponse
                    try:
                        agent_name = getattr(result_obj, "agent_name", "agent")
                        lines.append(f"{indent_str}  Response from {agent_name}:")
                        # Extract chat response content if available using getattr
                        chat_response = getattr(result_obj, "chat_response", None)
                        if chat_response:
                            try:
                                if hasattr(chat_response, "choices"):
                                    choices = getattr(chat_response, "choices", [])
                                    if choices and len(choices) > 0:
                                        message = getattr(choices[0], "message", None)
                                        if message:
                                            content = getattr(message, "content", "")
                                            if content:
                                                content_preview = content
                                                if len(content_preview) > 500:
                                                    content_preview = (
                                                        content_preview[:500] + "…"
                                                    )
                                                lines.append(
                                                    f"{indent_str}    {content_preview}"
                                                )
                            except Exception:
                                pass
                        # Include feedback if available using getattr
                        feedback = getattr(result_obj, "feedback", None)
                        if feedback:
                            feedback_preview = feedback
                            if len(feedback_preview) > 200:
                                feedback_preview = feedback_preview[:200] + "…"
                            lines.append(
                                f"{indent_str}    Feedback: {feedback_preview}"
                            )
                        # Recursively include sub-agent's workspace using getattr
                        workspace = getattr(result_obj, "workspace", None)
                        if workspace:
                            entries = getattr(workspace, "entries", [])
                            if entries:
                                lines.append(
                                    f"{indent_str}  Workspace from {agent_name}:"
                                )
                                nested_workspace = workspace.to_tree_string(
                                    max_entries=None,  # Don't limit nested entries
                                    indent=indent + 1,
                                )
                                if nested_workspace:
                                    lines.append(nested_workspace)
                    except Exception:
                        pass

            # If no result object, show feedback if available
            elif entry.feedback:
                feedback_preview = entry.feedback
                if len(feedback_preview) > 500:
                    feedback_preview = feedback_preview[:500] + "…"
                lines.append(f"{indent_str}  {feedback_preview}")

        return "\n".join(lines)

    def _find_output_data(self, obj: Any) -> Optional[Any]:
        """Recursively search for 'output_data' key in a JSON structure.

        Specifically searches for the path: result.result.response.output_data

        Args:
            obj: The object to search (can be dict, list, or any JSON-serializable type)

        Returns:
            The value of 'output_data' if found (preserves original type), None otherwise
        """
        try:
            # Convert to dict if it's a Pydantic model or other object
            if hasattr(obj, "model_dump"):
                obj = obj.model_dump()
            elif hasattr(obj, "dict"):
                obj = obj.dict()
            elif not isinstance(obj, (dict, list)):
                # Try to serialize to JSON and parse back
                try:
                    obj = json.loads(json.dumps(obj, default=str))
                except Exception:
                    return None

            # Try specific path first: result.result.response.output_data
            if isinstance(obj, dict):
                # Check for result.result.response.output_data path
                if "result" in obj:
                    result_value = obj["result"]
                    if isinstance(result_value, dict) and "response" in result_value:
                        response_value = result_value["response"]
                        if (
                            isinstance(response_value, dict)
                            and "output_data" in response_value
                        ):
                            return response_value["output_data"]
                        # Also check if response itself has nested response.output_data
                        if (
                            isinstance(response_value, dict)
                            and "response" in response_value
                        ):
                            nested_response = response_value["response"]
                            if (
                                isinstance(nested_response, dict)
                                and "output_data" in nested_response
                            ):
                                return nested_response["output_data"]

                # Fallback: search recursively for 'output_data' anywhere
                if "output_data" in obj:
                    value = obj["output_data"]
                    return value

                # Search nested dictionaries and lists
                for value in obj.values():
                    result = self._find_output_data(value)
                    if result is not None:
                        return result

            # Recursively search lists
            elif isinstance(obj, list):
                for item in obj:
                    result = self._find_output_data(item)
                    if result is not None:
                        return result

            return None
        except Exception:
            return None

    def _format_output_data_for_xml(self, output_data: Any) -> str:
        """Format output_data value for XML attribute.

        Args:
            output_data: The output_data value (can be any type)

        Returns:
            XML-safe string representation
        """
        if output_data is None:
            return ""

        # For simple types, convert to string
        if isinstance(output_data, (str, int, float, bool)):
            return str(output_data)

        # For complex types (dict, list), JSON-stringify
        # This will produce a JSON string with quotes, which we'll XML-escape
        try:
            json_str = json.dumps(output_data, ensure_ascii=False)
            return json_str
        except Exception:
            # Fallback to string representation
            return str(output_data)

    def _escape_xml_attr(self, value: Any) -> str:
        """Escape XML attribute value.

        Args:
            value: The value to escape

        Returns:
            Escaped string safe for XML attributes
        """
        if value is None:
            return ""
        text = str(value)
        # Replace newlines and other whitespace with spaces to keep XML valid
        text = " ".join(text.split())
        # Escape XML special characters
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        return text

    def to_xml_context_string(self, max_entries: Optional[int] = None) -> str:
        """Format workspace entries as XML for LLM context.

        Format: <entry time=<timestamp> agent=<agent> action=<action> status=<status> feedback=<feedback>(only if status is not SUCCESS) result=<output_data> />

        Args:
            max_entries: Maximum number of entries to show (None = all entries)

        Returns:
            XML formatted string of workspace entries
        """
        entries = self.get_flat_list()
        truncated = False
        if max_entries is not None and len(entries) > max_entries:
            entries = entries[-max_entries:]
            truncated = True

        lines = []
        if truncated:
            lines.append("...truncated...")
        for entry in entries:
            # Format timestamp
            timestamp = entry.date_created

            # Format agent name
            agent_name = self._escape_xml_attr(entry.agent_name)

            # Format action name
            action_name = self._escape_xml_attr(entry.action_name)

            # Format status
            status_val = self._escape_xml_attr(entry.status or "")

            # Format feedback (only if status is not SUCCESS)
            feedback_val = ""
            if entry.status and entry.status.upper() != "SUCCESS" and entry.feedback:
                feedback_val = f' feedback="{self._escape_xml_attr(entry.feedback)}"'

            # Extract response from result
            # Handle ActionResult only (skip AgentResponse for now)
            # Structure for ActionResult:
            #   entry.result -> ActionResult
            #   entry.result.result -> DirectToolResult
            #   entry.result.result.result -> dict with 'response' field
            result_content = ""
            if entry.result:
                try:
                    # Check if this is an ActionResult (has tool_type field) vs AgentResponse
                    if hasattr(entry.result, "tool_type"):
                        # This is an ActionResult - navigate to entry.result.result.result.response
                        inner_result = getattr(entry.result, "result", None)
                        if inner_result:
                            # inner_result is DirectToolResult
                            direct_result = getattr(inner_result, "result", None)
                            if direct_result:
                                # direct_result is dict|None with 'response' field
                                if isinstance(direct_result, dict):
                                    response = direct_result.get("response")
                                    if response is not None:
                                        # response can be ChatCompletionMessage (for LLM) or dict (for API)
                                        # Convert to dict if it's a Pydantic model
                                        if hasattr(response, "model_dump"):
                                            response_dict = response.model_dump(
                                                mode="json"
                                            )
                                        elif hasattr(response, "dict"):
                                            response_dict = response.dict()
                                        elif isinstance(response, dict):
                                            response_dict = response
                                        else:
                                            # Fallback: convert to string
                                            response_dict = str(response)

                                        # Serialize to JSON - no escaping needed, just for display
                                        result_json = json.dumps(
                                            response_dict,
                                            default=str,
                                            ensure_ascii=False,
                                        )
                                        if result_json:
                                            result_content = result_json
                    # AgentResponse handling will be added later
                except Exception:
                    pass

            # Build XML entry - put JSON directly in element content (no escaping needed for display)
            if result_content:
                entry_xml = f'\t<entry \n\t\ttime="{timestamp}" \n\t\tagent="{agent_name}" \n\t\taction="{action_name}" \n\t\tstatus="{status_val}"{feedback_val} \n\t\tresult="{result_content}" \n\t/>'
            else:
                entry_xml = f'\t<entry \n\t\ttime="{timestamp}" \n\t\tagent="{agent_name}" \n\t\taction="{action_name}" \n\t\tstatus="{status_val}"{feedback_val} \n\t/>'
            lines.append(entry_xml)

        return "\n".join(lines)


class Milestone(BaseModel):
    """A milestone representing a high-level checkpoint in the strategy."""

    id: str = Field(default="")
    title: str = Field(default="")
    completed: bool = Field(default=False)


class Strategy(BaseModel):
    """Agent strategy information."""

    date_created: int = Field(default=-1)
    milestones: List[Milestone] = Field(default_factory=list)
    # Track the request text this strategy was built for
    # Used to detect when a sub-agent is called with a different request
    source_request: Optional[str] = Field(default=None)

    def to_plan(self) -> str:
        """Convert milestones to a plan string format (numbered milestones only)."""
        if not self.milestones:
            return ""

        lines = []
        for idx, milestone in enumerate(self.milestones, start=1):
            lines.append(f"{idx}. {milestone.title}")

        return "\n".join(lines)

    @staticmethod
    def parse_milestones_from_text(text: str) -> List["Milestone"]:
        """Parse milestones from LLM response text.

        Expected format is JSON:
        {
          "milestones": [
            {"title": "Milestone 1"},
            {"title": "Milestone 2"}
          ]
        }
        """

        from maitai.models.agent.extended import Milestone

        milestones = []
        if not text or not text.strip():
            return milestones

        # Try to extract JSON from the response (might have markdown code blocks)
        json_text = text.strip()

        # Remove markdown code blocks if present
        json_match = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", json_text)
        if json_match:
            json_text = json_match.group(1)
        else:
            # Try to find JSON object in the text
            json_match = re.search(r"\{[\s\S]*\}", json_text)
            if json_match:
                json_text = json_match.group(0)

        try:
            data = json.loads(json_text)
            milestone_list = data.get("milestones", [])

            for idx, milestone_data in enumerate(milestone_list, start=1):
                if isinstance(milestone_data, dict):
                    title = milestone_data.get("title", "").strip()
                    if title:
                        milestone = Milestone(
                            id=f"m_{idx}", title=title, completed=False
                        )
                        milestones.append(milestone)
                elif isinstance(milestone_data, str):
                    # Fallback: handle string format
                    milestone = Milestone(
                        id=f"m_{idx}", title=milestone_data.strip(), completed=False
                    )
                    milestones.append(milestone)

        except json.JSONDecodeError:
            # Fallback to legacy text parsing if JSON parsing fails
            lines = text.strip().split("\n")
            milestone_pattern = re.compile(r"^\s*(\d+)[\.\)]\s+(.+)$")

            for line in lines:
                line = line.rstrip()
                if not line.strip():
                    continue

                milestone_match = milestone_pattern.match(line)
                if milestone_match:
                    milestone_idx = len(milestones) + 1
                    milestone_title = milestone_match.group(2).strip()
                    milestone = Milestone(
                        id=f"m_{milestone_idx}", title=milestone_title, completed=False
                    )
                    milestones.append(milestone)

        return milestones

    def to_text(self) -> str:
        """Get text representation of strategy with milestones only."""
        if not self.milestones:
            return "None"

        lines = []
        for idx, milestone in enumerate(self.milestones, start=1):
            milestone_status = "✓" if milestone.completed else " "
            milestone_text = f"{idx}. [{milestone_status}] {milestone.title}"
            lines.append(milestone_text)

        return "\n".join(lines)

    def build_strategy_user_message(
        self,
        sub_agents: List["Agent"],
        actions: List["AgentAction"],
        user_request: str,
        capabilities: Optional[List[str]] = None,
        special_notes: Optional[str] = None,
    ) -> str:
        """Generate a user message for building the strategy.

        If provided, ``special_notes`` are included as an additional context block
        under the tag <special_notes> so that the base strategy prompt remains
        unchanged and the addendum augments it.
        """
        blocks: List[str] = []
        blocks.append(f"<request>\n{user_request}\n</request>")
        blocks.append(
            "<sub-agents>\n"
            + ", ".join(
                [f"{agent.agent_name}: {agent.description}" for agent in sub_agents]
            )
            + "\n</sub-agents>"
        )
        blocks.append(
            "<actions>\n"
            + ", ".join(
                [f"{action.action_name}: {action.description}" for action in actions]
            )
            + "\n</actions>"
        )
        # Include agent capabilities (decorated orchestration/processing tools) if provided
        try:
            if capabilities:
                cleaned_caps = [
                    c for c in capabilities if isinstance(c, str) and c.strip()
                ]
                if cleaned_caps:
                    blocks.append(
                        "<capabilities>\n"
                        + ", ".join(cleaned_caps)
                        + "\n</capabilities>"
                    )
        except Exception:
            # Best-effort enrichment; omit if anything goes wrong
            pass
        if special_notes and special_notes.strip():
            blocks.append(f"<special_notes>\n{special_notes.strip()}\n</special_notes>")
        return "\n".join(blocks)

    def rebuild_strategy_user_message(
        self,
        original_strategy: str,
        feedback: str,
        new_requirements: str,
        scratchpad: str,
    ) -> str:
        """Generate a user message for rebuilding the strategy."""
        return dedent(
            f"""
            <original_strategy>\n{original_strategy}\n</original_strategy>
            <feedback>\n{feedback}\n</feedback>
            <new_requirements>\n{new_requirements}\n</new_requirements>
            <scratchpad>\n{scratchpad}\n</scratchpad>
        """
        ).strip()


class StrategyPrompts(BaseModel):
    """Customizable prompts for strategy operations."""

    build_strategy: str = Field(
        default="""You are a strategic planning assistant. Your job is to analyze the user request and create high-level milestones to accomplish it.

Given the following context:
- `<sub-agents>`: Agent capabilities and available tools
- `<actions>`: Available actions
- `<capabilities>`: Internal orchestration/processing capabilities you can leverage (e.g., write to scratchpad)
- `<user_request>`: User request details
- `<special_notes>`: Any additional notes or context that may be relevant to helping you build a good strategy.

Create a milestone-based strategy. Milestones are high-level checkpoints that represent major accomplishments or phases of the task.

IMPORTANT GUIDELINES:
1. Keep milestones SIMPLE and DIRECT - for straightforward requests (e.g., "launch Slack", "open a file"), use 1-2 milestones maximum
2. Each milestone should represent a concrete, actionable phase - avoid abstract milestones like "clarify intent" or "identify capabilities"
3. Don't overthink simple requests - if the request is clear, create milestones that directly accomplish it
4. Only create multiple milestones if the request genuinely requires distinct phases or sequential steps

ACTION-ORIENTED MILESTONES:
5. Use ACTION VERBS that describe what must be DONE: click, type, navigate, select, open, send, paste, drag, upload
6. When a milestone involves multiple distinct actions, split them into separate milestones
7. Avoid passive or observational language like "verify", "ensure", "confirm" unless paired with a specific action
8. Be explicit about HOW something is accomplished, not just WHAT the outcome should be

PRINCIPLES:
- "Copy" requires an action: clicking a copy button, pressing Cmd+C, or right-click > Copy
- "Share" requires an action: clicking share, pasting a link, or sending a message
- "Save" requires an action: clicking save button, pressing Cmd+S, or confirming a dialog
- Compound actions like "do X and Y" should become separate milestones when X and Y are distinct operations

FORMATTING REQUIREMENTS:
1. Respond with a valid JSON object only
2. Do NOT include steps - only milestone titles
3. Steps will be generated separately for each milestone

Each milestone should be terse and focused - no emojis.
Produce the minimum number of milestones necessary to complete the request - don't be too verbose. 
Break the request down into logical phases or major accomplishments, not granular step-by-step instructions.

JSON Schema:
{
  "milestones": [
    {"title": "Milestone 1 title"},
    {"title": "Milestone 2 title"},
    {"title": "Milestone 3 title"}
  ]
}

Example:
<request>Launch Slack</request>
{
  "milestones": [
    {"title": "Launch the Slack application"}
  ]
}

Example:
<request>Send an email to John with the quarterly report attached</request>
{
  "milestones": [
    {"title": "Open email compose window in Gmail"},
    {"title": "Enter John's email address and subject line"},
    {"title": "Click attach button and select the quarterly report file"},
    {"title": "Click send button to send the email"}
  ]
}

Example:
<request>Schedule a meeting with the design team for tomorrow at 2pm</request>
{
  "milestones": [
    {"title": "Open Google Calendar and click to create new event"},
    {"title": "Set the meeting time to tomorrow at 2pm"},
    {"title": "Add design team members as attendees"},
    {"title": "Click save to create the calendar event"}
  ]
}

Example:
<request>Download the invoice PDF and save it to the Finance folder</request>
{
  "milestones": [
    {"title": "Click the download button for the invoice PDF"},
    {"title": "Open Finder and navigate to the Finance folder"},
    {"title": "Move the downloaded file to the Finance folder"}
  ]
}

Example:
<request>Share the project document link with the team on Teams</request>
{
  "milestones": [
    {"title": "Open the project document and click the Share button"},
    {"title": "Click Copy Link to copy the sharing URL"},
    {"title": "Navigate to the team channel in Microsoft Teams"},
    {"title": "Paste and send the link in the channel"}
  ]
}

Example:
<request>Fill out the expense report form with today's receipts</request>
{
  "milestones": [
    {"title": "Navigate to the expense report form"},
    {"title": "Enter expense details in the form fields"},
    {"title": "Upload receipt images using the attachment button"},
    {"title": "Click submit button to submit the expense report"}
  ]
}
"""
    )

    rebuild_strategy: str = Field(
        default=dedent(
            """
            You are a strategic planning assistant tasked with revising an existing strategy based on new information or feedback.

            Given:
            - `<original_strategy>`: The original strategy (milestones)
            - `<feedback>`: Feedback about what worked/didn't work
            - `<scratchpad>`: The agent's scratchpad of notes and insights

            Create an updated strategy that:
            1. Addresses the feedback and issues encountered
            2. Adapts to new information or requirements
            3. Builds on completed work where possible
            4. Provides clear next steps forward

            Maintain the same format as the original strategy - a numbered list of high-level milestones. Each milestone should be terse and focused - no emojis. Pick up the strategy where it left off. Do NOT start over.
            If some milestones were already completed successfully, remove them from the updated strategy and only include remaining milestones.

            THINGS TO CONSIDER:
            - An agent cannot alter or perform an action in a different way other than supplying different parameters. Often times if an action failed, it's best to try a different action entirely.
            - If a delegated task did not yield the desired result, it's best to try to delegate the task to a different agent if there are other applicable options.
            - Use the scratchpad for reference of what worked and what didn't work as well. 

            Example:
            <original_strategy>
            1. Go to the Doordash page in browser
            2. Start a group order and copy the order link
            3. Go to the general channel in Slack and post the order link in clipboard
            </original_strategy>
            <feedback>Successfully navigated to Doordash and started the group order. The link was copied. However, when trying to navigate to Slack, the browser closed unexpectedly.</feedback>
            1. Go to the general channel in Slack and post the order link in clipboard

            Example:
            <original_strategy>
            1. Navigate to the engineering channel in Slack
            2. Post a message asking the team to share their updates for the day
            </original_strategy>
            <feedback>Successfully navigated to the engineering channel.</feedback>
            1. Post a message asking the team to share their updates for the day
        """
        ).strip()
    )


class AgentAction(BaseModel):
    """Database model for agent actions."""

    id: Optional[int] = -1
    date_created: Optional[float] = 0
    agent_id: int
    action_name: str
    action_type: str  # "api_call", "llm_call", "webhook", "integration", etc.
    description: str
    enabled: bool = True
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


class AgentRequest(BaseModel):
    """
    Request contract for orchestrator and agent-to-agent execution.

    Designed to serve both root orchestration requests (from the orchestrator)
    and delegations between agents with a unified shape.
    """

    # Target identifiers
    agent_id: Optional[int] = Field(
        default=None, validation_alias=AliasChoices("agent_id", "agentId")
    )
    company_id: Optional[int] = Field(
        default=2, validation_alias=AliasChoices("company_id", "companyId")
    )
    application_id: Optional[int] = Field(
        default=0, validation_alias=AliasChoices("application_id", "applicationId")
    )

    # New string fields
    application: Optional[str] = None
    agent: Optional[str] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    request_id: Optional[str] = (
        None  # Unique ID for this specific agent request (distinct from task_id)
    )

    # Core request parameters - using ChatCompletionParams directly
    params: ChatCompletionParams

    # Delegation context (minimal; optional for root requests)
    requesting_agent_name: Optional[str] = None
    requesting_agent_path: Optional[str] = None

    # Execution preferences (optional)
    execution_mode: Optional[str] = Field(
        default="auto", validation_alias=AliasChoices("execution_mode", "executionMode")
    )  # "direct", "reasoning", "auto"
    max_iterations: Optional[int] = Field(
        default=None, validation_alias=AliasChoices("max_iterations", "maxIterations")
    )
    max_steps: Optional[int] = Field(
        default=-1, validation_alias=AliasChoices("max_steps", "maxSteps")
    )  # -1 = no limit, counts LLM orchestration calls across all agents

    # Runtime flags
    high_performance: Optional[bool] = Field(
        default=False,
        validation_alias=AliasChoices("high_performance", "highPerformance"),
    )
    disable_chaining: Optional[bool] = Field(
        default=None,
        validation_alias=AliasChoices("disable_chaining", "disableChaining"),
    )

    # Delegation intent (how to handle the result)
    delegation_intent: ActionResultType = ActionResultType.GATHER_INFO

    # Metadata for request context (timestamps, profiling, etc.)
    meta: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_delegation(
        cls,
        parent_agent,
        request_text: str,
        context: Optional[str] = None,
        delegation_intent: ActionResultType = ActionResultType.GATHER_INFO,
        task_id: Optional[str] = None,
        execution_mode: Optional[str] = None,
        high_performance: Optional[bool] = None,
        disable_chaining: Optional[bool] = None,
        max_iterations: Optional[int] = None,
    ) -> "AgentRequest":
        """Create an AgentRequest from a parent agent delegation.

        Args:
            parent_agent: The parent agent making the delegation
            request_text: The request text for the sub-agent
            context: Optional context for the sub-agent
            delegation_intent: How to use the result
            task_id: Optional task ID
            execution_mode: Execution mode to use. If None, inherits from parent's _current_execution_mode or defaults to "auto"
            high_performance: Optional override for the high_performance flag
            disable_chaining: Optional override for the disable_chaining flag
            max_iterations: Optional override for max_iterations
        """
        # Build a single user message containing both context and request
        blocks: List[str] = []
        if context:
            blocks.append(f"<context>\n{context}\n</context>")
        blocks.append(f"<request>\n{request_text}\n</request>")
        # Create a ChatMessage properly typed for ChatCompletionParams
        from maitai.models.chat import ChatMessage

        user_message = ChatMessage(role="user", content="\n".join(blocks))

        # Get session_id from parent agent's current request to ensure all downstream agents use the same session_id
        parent_session_id = getattr(parent_agent, "_current_session_id", None)

        # Inherit execution mode from parent if not explicitly provided
        if execution_mode is None:
            execution_mode = (
                getattr(parent_agent, "_current_execution_mode", None) or "auto"
            )

        orig_req = getattr(parent_agent, "_original_agent_request", None)

        # Inherit flags from parent agent unless override provided
        if high_performance is None:
            high_performance = getattr(parent_agent, "high_performance", None)
            if (
                high_performance is None
                and orig_req
                and hasattr(orig_req, "high_performance")
            ):
                high_performance = orig_req.high_performance

        if disable_chaining is None:
            disable_chaining = getattr(parent_agent, "disable_chaining", None)
            if (
                disable_chaining is None
                and orig_req
                and hasattr(orig_req, "disable_chaining")
            ):
                disable_chaining = orig_req.disable_chaining

        if max_iterations is None and orig_req and hasattr(orig_req, "max_iterations"):
            max_iterations = orig_req.max_iterations

        # Inherit max_steps from parent request
        max_steps = -1
        if (
            orig_req
            and hasattr(orig_req, "max_steps")
            and orig_req.max_steps is not None
        ):
            max_steps = orig_req.max_steps

        # Share meta dict reference to propagate step counter across hierarchy
        inherited_meta = {}
        if orig_req and hasattr(orig_req, "meta") and orig_req.meta:
            inherited_meta = orig_req.meta

        # Create ChatCompletionParams directly
        params = ChatCompletionParams(
            messages=[user_message], model="gpt-5-chat-latest"
        )

        return cls(
            params=params,
            session_id=parent_session_id,
            requesting_agent_name=parent_agent.agent_name,
            requesting_agent_path=getattr(parent_agent, "_current_agent_id_path", None),
            execution_mode=execution_mode,
            delegation_intent=delegation_intent,
            task_id=task_id,
            high_performance=high_performance,
            disable_chaining=disable_chaining,
            max_iterations=max_iterations,
            max_steps=max_steps,
            meta=inherited_meta,
        )


class AgentResponse(BaseModel):
    """Response with nested execution context."""

    agent_name: str
    agent_path: str
    status: str = "COMPLETED"  # Default to success status
    chat_response: Optional[Any] = (
        None  # ChatCompletionResponse - avoid circular import
    )
    feedback: Optional[str] = None
    error: Optional[str] = None

    start_time: int = Field(default_factory=lambda: int(time.time() * 1000))
    end_time: Optional[int] = None
    execution_time_ms: int = 0
    iterations_used: int = 0
    steps_used: int = 0  # Total LLM orchestration steps across all agents

    # Delegation intent that was used for this request
    delegation_intent: Optional[ActionResultType] = None

    # Simple nested context
    action_log: ActionLog = Field(default_factory=ActionLog)
    scratchpad: Scratchpad = Field(default_factory=Scratchpad)
    workspace: "Workspace" = Field(default_factory=lambda: Workspace())

    # Metadata for response context (timestamps, profiling, etc.)
    meta: Dict[str, Any] = Field(default_factory=dict)

    def complete(self, status: str = "COMPLETED", feedback: Optional[str] = None):
        """Mark the response as completed."""
        self.status = status
        self.end_time = int(time.time() * 1000)
        self.execution_time_ms = self.end_time - self.start_time
        if feedback:
            self.feedback = feedback


class ActionResult(BaseModel):
    """Result of executing a single action/tool call."""

    tool_type: ToolType
    agent_name: str
    agent_path: str
    action_name: str
    action_args: str
    status: str
    result: Any = None
    feedback: Optional[str] = None
    date_created: int = Field(default_factory=lambda: int(time.time() * 1000))

    # Result type for both actions and sub-agent results
    delegation_intent: Optional[ActionResultType] = None

    # Agent ID that executed this action (for ACL filtering in processing)
    agent_id: Optional[int] = None


class AgentLoopResults(BaseModel):
    """Results from the agent reasoning loop."""

    status: LoopStatus
    response: Optional[ChatCompletionResponse] = None
    feedback: Optional[str] = None
    iterations: int = 0


# Keep compatibility for existing imports
Action = ActionResult  # Alias for backwards compatibility

# Resolve forward references for Pydantic v2
ActionLogEntry.model_rebuild()
ScratchpadEntry.model_rebuild()
AgentResponse.model_rebuild()
