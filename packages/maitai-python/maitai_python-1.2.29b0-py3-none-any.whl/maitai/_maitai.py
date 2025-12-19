import logging
import os
from typing import Mapping, Optional, Union

import groq
import httpx
import openai

from maitai._config import Config
from maitai._context import ContextManager
from maitai.agent._completions import Completions as AgentCompletions
from maitai.chat._completions import Completions
from maitai.models.chat import AzureParams, ClientParams
from maitai.models.key import Key
from maitai.transcriptions._transcriptions import Transcriptions

logger = logging.getLogger("maitai")

DEFAULT_MAX_RETRIES = 2


class Maitai:
    def __init__(
        self,
        *,
        maitai_api_key: Optional[str] = None,
        api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        cerebras_api_key: Optional[str] = None,
        azure_api_key: Optional[str] = None,
        sambanova_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        deepseek_api_key: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        base_url: Union[str, httpx.URL, None] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
        _strict_response_validation: bool = False,
    ):
        if not maitai_api_key:
            maitai_api_key = os.environ.get("MAITAI_API_KEY")
        if not maitai_api_key:
            raise ValueError(
                "MAITAI_API_KEY has not been set. Either set via environment variable or pass it directly into the client."
            )
        if api_key:
            raise ValueError(
                "api_key is deprecated. Use provider specific keys instead. Supported variables: openai_api_key, groq_api_key, anthropic_api_key, cerebras_api_key, azure_api_key, sambanova_api_key, gemini_api_key, deepseek_api_key"
            )
        self.config = Config(maitai_api_key)
        if openai_api_key:
            if not self.config.auth_keys.openai_api_key:
                self.config.auth_keys.openai_api_key = Key(
                    key_value=openai_api_key,
                )
            else:
                self.config.auth_keys.openai_api_key.key_value = openai_api_key
        if groq_api_key:
            if not self.config.auth_keys.groq_api_key:
                self.config.auth_keys.groq_api_key = Key(
                    key_value=groq_api_key,
                )
            else:
                self.config.auth_keys.groq_api_key.key_value = groq_api_key
        if anthropic_api_key:
            if not self.config.auth_keys.anthropic_api_key:
                self.config.auth_keys.anthropic_api_key = Key(
                    key_value=anthropic_api_key,
                )
            else:
                self.config.auth_keys.anthropic_api_key.key_value = anthropic_api_key
        if cerebras_api_key:
            if not self.config.auth_keys.cerebras_api_key:
                self.config.auth_keys.cerebras_api_key = Key(
                    key_value=cerebras_api_key,
                )
            else:
                self.config.auth_keys.cerebras_api_key.key_value = cerebras_api_key
        if azure_api_key:
            if not self.config.auth_keys.azure_api_key:
                self.config.auth_keys.azure_api_key = Key(
                    key_value=azure_api_key,
                )
            else:
                self.config.auth_keys.azure_api_key.key_value = azure_api_key
        if sambanova_api_key:
            if not self.config.auth_keys.sambanova_api_key:
                self.config.auth_keys.sambanova_api_key = Key(
                    key_value=sambanova_api_key,
                )
            else:
                self.config.auth_keys.sambanova_api_key.key_value = sambanova_api_key
        if gemini_api_key:
            if not self.config.auth_keys.gemini_api_key:
                self.config.auth_keys.gemini_api_key = Key(
                    key_value=gemini_api_key,
                )
            else:
                self.config.auth_keys.gemini_api_key.key_value = gemini_api_key
        if deepseek_api_key:
            if not self.config.auth_keys.deepseek_api_key:
                self.config.auth_keys.deepseek_api_key = Key(
                    key_value=deepseek_api_key,
                )
            else:
                self.config.auth_keys.deepseek_api_key.key_value = deepseek_api_key
        self._openai_client = None
        self._groq_client = None
        azure_params = None
        if azure_api_key:
            azure_params = AzureParams(
                endpoint=azure_endpoint,
                deployment=azure_deployment,
                api_version=azure_api_version,
            )
            self._openai_client = openai.AzureOpenAI(  # type: ignore
                azure_endpoint=azure_endpoint,
                azure_deployment=azure_deployment,
                api_key=azure_api_key,
                api_version=azure_api_version,
                organization=organization,
                project=project,
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
                default_headers=default_headers,
                default_query=default_query,
                http_client=http_client,
                _strict_response_validation=_strict_response_validation,
            )
        elif openai_api_key or os.environ.get("OPENAI_API_KEY"):
            self._openai_client = openai.OpenAI(
                api_key=openai_api_key or os.environ.get("OPENAI_API_KEY"),
                organization=organization,
                project=project,
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
                default_headers=default_headers,
                default_query=default_query,
                http_client=http_client,
                _strict_response_validation=_strict_response_validation,
            )
        if groq_api_key or self.config.auth_keys.groq_api_key:

            self._groq_client = groq.Groq(
                api_key=groq_api_key
                or (
                    self.config.auth_keys.groq_api_key.key_value
                    if self.config.auth_keys.groq_api_key
                    else None
                ),
            )

        client_params = None
        if base_url or default_headers or default_query:
            client_param_dict = {}
            if base_url:
                client_param_dict["base_url"] = base_url
            if default_headers:
                client_param_dict["default_headers"] = default_headers
            if default_query:
                client_param_dict["default_query"] = default_query
            if azure_params:
                client_param_dict["azure_params"] = azure_params
            client_params = ClientParams(**client_param_dict)
        self.chat = Chat(
            self.config, self._openai_client, self._groq_client, client_params
        )
        self.audio = Audio(self.config)
        self.agent = Agent(self.config)
        self.context = ContextManager(self.config)


class Chat:
    def __init__(
        self,
        config: Config,
        openai_client: Optional[openai.Client] = None,
        groq_client: Optional[groq.Groq] = None,
        client_params: Optional[ClientParams] = None,
    ):
        self.completions = Completions(
            config, openai_client, groq_client, client_params
        )


class Audio:
    def __init__(
        self,
        config: Config,
    ):
        self.transcriptions = Transcriptions(config)


class Agent:
    def __init__(
        self,
        config: Config,
    ):
        self.completions = AgentCompletions(config)
