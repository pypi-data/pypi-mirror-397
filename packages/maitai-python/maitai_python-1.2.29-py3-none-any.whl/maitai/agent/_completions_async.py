from typing import Dict, Mapping, Optional, Union

import openai
from openai._types import NOT_GIVEN, NotGiven

from maitai._config import Config
from maitai._maitai_client import MaitaiClient
from maitai.models.agent.extended import AgentRequest


class AsyncCompletions(MaitaiClient):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        # Initialize OpenAI client with Maitai orchestration endpoint
        self._openai_client = openai.AsyncOpenAI(
            base_url=f"{self.config.maitai_orchestration_host.rstrip('/')}/orchestration",
            api_key=self.config.api_key,
            default_headers={"x-api-key": self.config.api_key},
        )

    def _get_client_config(self):
        """Get base_url and api_key using Maitai's config infrastructure."""
        base_url = self.config.maitai_orchestration_host
        api_key = self.config.api_key
        return base_url, api_key

    def _convert_agent_request_to_openai(self, request: AgentRequest) -> Dict:
        """Convert AgentRequest to OpenAI chat completions format."""
        # Convert ChatMessage objects to OpenAI format
        openai_messages = []
        for msg in request.params.messages:
            openai_messages.append({"role": msg.role, "content": msg.content})

        model = request.params.model or request.agent or "agent"

        # Build the OpenAI request
        openai_request = {
            "model": model,
            "messages": openai_messages,
            "temperature": request.params.temperature,
            "stream": request.params.stream,
        }

        # Add optional parameters if they exist
        if request.params.max_tokens is not None:
            openai_request["max_tokens"] = request.params.max_tokens
        if request.params.top_p is not None:
            openai_request["top_p"] = request.params.top_p
        if request.params.frequency_penalty is not None:
            openai_request["frequency_penalty"] = request.params.frequency_penalty
        if request.params.presence_penalty is not None:
            openai_request["presence_penalty"] = request.params.presence_penalty
        if request.params.stop is not None:
            openai_request["stop"] = request.params.stop

        # Add agent-specific parameters to extra_body
        application_id = (
            request.application_id
            if isinstance(request.application_id, int) and request.application_id > 0
            else None
        )
        extra_body = {
            "agent": request.agent,
            "application": request.application,
            "application_id": application_id,
            "agent_id": request.agent_id if not request.agent else None,
            "session_id": request.session_id,
            "task_id": request.task_id,
            "execution_mode": request.execution_mode,
            "max_iterations": request.max_iterations,
            "high_performance": request.high_performance,
            "disable_chaining": request.disable_chaining,
        }

        # Remove None values from extra_body
        extra_body = {k: v for k, v in extra_body.items() if v is not None}

        openai_request["extra_body"] = extra_body

        return openai_request

    async def create(
        self,
        *,
        request: AgentRequest,
        extra_headers: Optional[Mapping[str, str]] = None,
        timeout: Union[float, openai.Timeout, None, NotGiven] = NOT_GIVEN,
    ):
        """
        Execute an agent request and return OpenAI response directly.

        Args:
            request: The AgentRequest to execute
            extra_headers: Extra headers to include (optional)
            timeout: Request timeout (optional)

        Returns:
            Direct OpenAI response (streaming or non-streaming)
        """
        # Convert AgentRequest to OpenAI format
        openai_request = self._convert_agent_request_to_openai(request)

        # Extract parameters for OpenAI client call
        model = openai_request.pop("model")
        messages = openai_request.pop("messages")
        stream = openai_request.pop("stream", True)
        extra_body = openai_request.pop("extra_body", {})

        # Set up timeout
        timeout_value = timeout if timeout is not NOT_GIVEN else None

        # Call OpenAI client directly and return the response as-is
        return await self._openai_client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            extra_body=extra_body,
            extra_headers=extra_headers,
            timeout=timeout_value,
            **openai_request,  # Include any remaining parameters
        )
