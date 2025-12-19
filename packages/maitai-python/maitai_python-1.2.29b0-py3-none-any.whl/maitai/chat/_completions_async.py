import asyncio
import logging
import os
import time
import uuid
import warnings
from typing import AsyncIterable, Dict, Iterable, List, Optional, Union

import groq
import httpx
import openai
import openai.types as openai_types
import openai.types.chat as openai_chat_types

from maitai._config import Config
from maitai._evaluator import Evaluator
from maitai._inference import Inference
from maitai._types import (
    Body,
    EvaluateCallback,
    FallbackConfig,
    Headers,
    MaitaiChunk,
    MaitaiCompletion,
    Query,
    ToolFunction,
)
from maitai._utils import (
    convert_open_ai_chat_completion_chunk,
    convert_openai_chat_completion,
    convert_params_to_groq,
    get_chat_completion_params,
    required_args,
    type_to_response_format_param,
)
from maitai.exceptions import (
    InferenceException,
    InferenceWarning,
    MaitaiConnectionError,
)
from maitai.models.chat import ChatCompletionParams, ClientParams, EvaluationContentType
from maitai.models.config import InferenceLocations
from maitai.models.inference import InferenceStreamResponse
from maitai.models.metric import RequestTimingMetric
from maitai.tools import Tools

logger = logging.getLogger("maitai")

DEFAULT_MAX_RETRIES = 2


class AsyncCompletions:
    def __init__(
        self,
        config: Config,
        openai_client: Optional[openai.AsyncClient] = None,
        groq_client: Optional[groq.AsyncGroq] = None,
        client_params: Optional[ClientParams] = None,
    ):
        self._openai_client = openai_client
        self._groq_client = groq_client
        self._client_params = client_params or ClientParams()
        self.inference_client = Inference(config)
        self.evaluator = Evaluator(config)
        self.override_push_timing_metrics = os.environ.get(
            "MAITAI_DONT_PUSH_TIMING_METRICS"
        )
        self.config = config

    @required_args(
        ["intent", "application", "messages"],
        ["intent", "application_ref_name", "messages"],
        ["intent", "application", "messages", "model"],
        ["intent", "application_ref_name", "messages", "model"],
        ["intent", "application", "messages", "model", "stream"],
        ["intent", "application_ref_name", "messages", "model", "stream"],
    )
    async def create(
        self,
        *,
        # Maitai Arguments
        user_id: str = "",
        session_id: Union[str, int] = "",
        reference_id: Union[str, int, None] = None,
        intent: str = "",
        application: str = "",
        callback: Optional[EvaluateCallback] = None,
        server_side_inference: Optional[bool] = None,
        evaluation_enabled: Optional[bool] = None,
        apply_corrections: Optional[bool] = None,
        metadata: dict = {},
        safe_mode: Optional[bool] = None,
        fallback_config: Union[FallbackConfig, dict, None] = None,
        return_request: bool = False,
        push_timing_metrics: bool = True,
        # OpenAI Arguments
        messages: Iterable[openai_chat_types.ChatCompletionMessageParam],
        model: Union[str, openai_types.ChatModel, openai.NotGiven] = openai.NOT_GIVEN,
        frequency_penalty: Union[Optional[float], openai.NotGiven] = openai.NOT_GIVEN,
        function_call: Union[
            openai_chat_types.completion_create_params.FunctionCall, openai.NotGiven
        ] = openai.NOT_GIVEN,
        functions: Union[
            Iterable[openai_chat_types.completion_create_params.Function],
            openai.NotGiven,
        ] = openai.NOT_GIVEN,
        logit_bias: Union[Optional[Dict[str, int]], openai.NotGiven] = openai.NOT_GIVEN,
        logprobs: Union[Optional[bool], openai.NotGiven] = openai.NOT_GIVEN,
        max_tokens: Union[Optional[int], openai.NotGiven] = openai.NOT_GIVEN,
        max_completion_tokens: Union[Optional[int], openai.NotGiven] = openai.NOT_GIVEN,
        n: Union[Optional[int], openai.NotGiven] = openai.NOT_GIVEN,
        presence_penalty: Union[Optional[float], openai.NotGiven] = openai.NOT_GIVEN,
        reasoning_effort: Union[str, openai.NotGiven, None] = openai.NOT_GIVEN,
        response_format: Union[
            openai_chat_types.completion_create_params.ResponseFormat, openai.NotGiven
        ] = openai.NOT_GIVEN,
        seed: Union[Optional[int], openai.NotGiven] = openai.NOT_GIVEN,
        stop: Union[
            Union[Optional[str], List[str]], openai.NotGiven
        ] = openai.NOT_GIVEN,
        stream: Union[Optional[bool], openai.NotGiven] = openai.NOT_GIVEN,
        stream_options: Union[
            Optional[openai_chat_types.ChatCompletionStreamOptionsParam],
            openai.NotGiven,
        ] = openai.NOT_GIVEN,
        temperature: Union[Optional[float], openai.NotGiven] = openai.NOT_GIVEN,
        tool_choice: Union[
            openai_chat_types.ChatCompletionToolChoiceOptionParam, openai.NotGiven
        ] = openai.NOT_GIVEN,
        tools: Union[
            Tools,
            Iterable[Union[openai_chat_types.ChatCompletionToolParam, ToolFunction]],
            openai.NotGiven,
        ] = openai.NOT_GIVEN,
        top_logprobs: Union[Optional[int], openai.NotGiven] = openai.NOT_GIVEN,
        top_p: Union[Optional[float], openai.NotGiven] = openai.NOT_GIVEN,
        user: Union[str, openai.NotGiven] = openai.NOT_GIVEN,
        extra_headers: Union[
            None, Headers, Dict[str, str], openai.NotGiven
        ] = openai.NOT_GIVEN,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NOT_GIVEN,
        parallel_tool_calls: Union[bool, openai.NotGiven] = openai.NOT_GIVEN,
    ) -> Union[MaitaiCompletion, AsyncIterable[MaitaiChunk]]:
        retry_args = locals()
        timing = RequestTimingMetric(
            time_request_start=time.time(),
        )
        # Check environment variable to override push_timing_metrics default
        if self.override_push_timing_metrics:
            push_timing_metrics = False
        if not self.config.api_key:
            raise ValueError("Maitai API Key has not been set")
        if server_side_inference is False and apply_corrections is True:
            raise ValueError("server_side_inference must be true to apply_corrections")
        if apply_corrections is True and evaluation_enabled is False:
            raise ValueError("evaluations must be enabled to apply_corrections")
        if not session_id:
            session_id = str(uuid.uuid4())
        maitai_config = self.config.get_application_action_config(application, intent)
        if server_side_inference is None:
            server_side_inference = (
                maitai_config.inference_location == InferenceLocations.SERVER
            )
        if evaluation_enabled is None:
            evaluation_enabled = maitai_config.evaluation_enabled
        if apply_corrections is None:
            apply_corrections = maitai_config.apply_corrections
        if model == openai.NOT_GIVEN:
            model = maitai_config.model
        if temperature == openai.NOT_GIVEN:
            temperature = maitai_config.temperature
        if safe_mode is None:
            safe_mode = maitai_config.safe_mode
        if stream == openai.NOT_GIVEN:
            stream = False
        if response_format == openai.NOT_GIVEN:
            response_format = {"type": "text"}
        if stop == openai.NOT_GIVEN and maitai_config.stop is not None:
            stop = maitai_config.stop
        if logprobs == openai.NOT_GIVEN:
            logprobs = maitai_config.logprobs
        if max_tokens == openai.NOT_GIVEN and maitai_config.max_tokens is not None:
            max_tokens = maitai_config.max_tokens
        if max_completion_tokens and max_completion_tokens != openai.NOT_GIVEN:
            max_tokens = max_completion_tokens
        if n == openai.NOT_GIVEN and maitai_config.n:
            n = maitai_config.n
        if frequency_penalty == openai.NOT_GIVEN:
            frequency_penalty = maitai_config.frequency_penalty
        if presence_penalty == openai.NOT_GIVEN:
            presence_penalty = maitai_config.presence_penalty
        if timeout == openai.NOT_GIVEN and maitai_config.timeout > 0:
            timeout = maitai_config.timeout
        if fallback_config is None and maitai_config.fallback_config:
            fallback_config = {
                "model": maitai_config.fallback_config.model,
                "strategy": maitai_config.fallback_config.strategy,
                "timeout": maitai_config.fallback_config.timeout,
            }
        completion_params = get_chat_completion_params(
            messages=messages,
            model=model,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_tokens=max_tokens,
            n=n,
            presence_penalty=presence_penalty,
            response_format=response_format,
            seed=seed,
            stop=stop,
            stream=stream,
            stream_options=stream_options,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
            parallel_tool_calls=parallel_tool_calls,
            extra_headers=extra_headers,
            reasoning_effort=reasoning_effort,
        )
        if server_side_inference:
            response_timeout = None
            if isinstance(timeout, float) or isinstance(timeout, int):
                response_timeout = timeout
            request_dict = {
                "application_ref_name": application,
                "session_id": session_id,
                "reference_id": reference_id,
                "action_type": intent,
                "apply_corrections": apply_corrections,
                "evaluation_enabled": evaluation_enabled,
                "params": completion_params,
                "return_evaluation": True if callback else False,
                "user_id": user_id,
                "auth_keys": self.config.auth_keys.model_dump(),
                "metadata": metadata,
                "safe_mode": safe_mode,
                "return_request": return_request,
                "fallback_config": fallback_config,
            }

            if self._client_params is not None:
                request_dict["client_params"] = self._client_params.model_dump()

            try:
                timing.time_pre_request = time.time()
                response = await self.inference_client.infer_async(
                    request_dict, callback, response_timeout
                )
                if stream:
                    if "self" in retry_args:
                        del retry_args["self"]
                    retry_args["server_side_inference"] = False
                    retry_args["model"] = model
                    return self._process_inference_stream_async(
                        response,
                        retry_args,
                        timing,
                        includes_usage=(
                            stream_options.get("include_usage", False)
                            if stream_options and stream_options != openai.NOT_GIVEN
                            else False
                        ),
                        push_timing_metrics=push_timing_metrics,
                    )
                # ChatCompletion only
                async for resp in response:
                    if resp.warning:
                        warnings.warn(resp.warning, InferenceWarning)
                    if resp.error:
                        if "Unknown error occurred" in resp.error:
                            raise MaitaiConnectionError(resp.error)
                        raise InferenceException(resp.error)
                    timing.request_id = resp.chat_completion_response.request_id
                    timing.time_request_end = time.time()
                    if push_timing_metrics:
                        asyncio.create_task(
                            self.inference_client.send_request_timing_data_async(timing)
                        )
                    completion = MaitaiCompletion.model_validate(
                        resp.chat_completion_response.model_dump()
                    )
                    completion.set_response_format(response_format)
                    return completion
                raise InferenceException("No data received")
            except MaitaiConnectionError as e:
                fallback_model = (
                    fallback_config.get("model") if fallback_config else None
                )
                if "gpt" not in model and fallback_model and "gpt" in fallback_model:
                    model = fallback_model
                if "gpt" not in model:
                    raise e
                if safe_mode:
                    raise e
                logger.warning("Maitai issue, retrying on client side")
                server_side_inference = False
        if not server_side_inference:
            groq_model = False
            if "groq:" in model or "maitai:" in model or "llama" in model:
                groq_model = True
                model = model.replace("groq:", "").replace("maitai:", "")
            if "openai:" in model:
                model = model.replace("openai:", "")
            local_params = {
                "messages": messages,
                "model": model,
                "frequency_penalty": frequency_penalty,
                "function_call": function_call,
                "functions": functions,
                "logit_bias": logit_bias,
                "logprobs": logprobs,
                "max_tokens": max_tokens,
                "n": n,
                "presence_penalty": presence_penalty,
                "reasoning_effort": reasoning_effort,
                "response_format": response_format,
                "seed": seed,
                "stop": stop,
                "stream": stream,
                "stream_options": stream_options,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "tools": tools,
                "top_logprobs": top_logprobs,
                "top_p": top_p,
                "user": user,
                "extra_headers": extra_headers,
                "extra_query": extra_query,
                "extra_body": extra_body,
                "timeout": timeout,
                "parallel_tool_calls": parallel_tool_calls,
            }

            if groq_model:
                if self._groq_client is None:
                    if (
                        not self.config.auth_keys.groq_api_key
                        or not self.config.auth_keys.groq_api_key.key_value
                    ):
                        raise ValueError(
                            "Groq API key is required for Groq models but was not provided"
                        )

                    self._groq_client = groq.AsyncGroq(
                        api_key=self.config.auth_keys.groq_api_key.key_value,
                    )
                client_to_use = self._groq_client
                local_params = convert_params_to_groq(local_params)
            else:
                if self._openai_client is None:
                    self._openai_client = openai.AsyncOpenAI(
                        api_key=self.config.auth_keys.openai_api_key.key_value,
                        default_headers=self._client_params.default_headers or None,
                        default_query=self._client_params.default_query or None,
                        base_url=self._client_params.base_url or None,
                    )
                client_to_use = self._openai_client

            if hasattr(response_format, "model_json_schema"):
                response_format = {
                    "type": "json_schema",
                    "json_schema": type_to_response_format_param(response_format),
                }
            if isinstance(tools, Tools):
                tools = tools.get_tool_definitions()

            response = await client_to_use.chat.completions.create(
                **local_params,
            )
            if stream:
                return self._process_async_openai_stream(
                    session_id,
                    reference_id,
                    intent,
                    application,
                    messages,
                    response,
                    evaluation_enabled,
                    completion_params,
                    timing,
                    callback,
                    metadata,
                )
            else:
                timing.time_request_end = time.time()
                maitai_completion = convert_openai_chat_completion(response)
                full_conv = messages + [
                    {
                        "role": "assistant",
                        "content": maitai_completion.choices[0].message.content,
                    }
                ]
                if evaluation_enabled:
                    await self.evaluator.evaluate_async(
                        session_id=session_id,
                        reference_id=reference_id,
                        intent=intent,
                        content_type=EvaluationContentType.MESSAGE,
                        content=full_conv,
                        application_ref_name=application,
                        callback=callback,
                        chat_completion_response=maitai_completion,
                        completion_params=completion_params,
                        timing=timing,
                        metadata=metadata,
                    )
                else:
                    await self.inference_client.store_chat_response_async(
                        session_id=session_id,
                        reference_id=reference_id,
                        intent=intent,
                        application_ref_name=application,
                        chat_completion_response=maitai_completion,
                        completion_params=completion_params,
                        final_chunk=None,
                        content="",
                        timing=timing,
                        metadata=metadata,
                    )
                completion = MaitaiCompletion.model_validate(
                    maitai_completion.model_dump()
                )
                completion.set_response_format(response_format)
                return completion

    async def _process_async_openai_stream(
        self,
        session_id: Union[str, int],
        reference_id: Union[str, int, None],
        intent: str,
        application: str,
        messages: Iterable[openai_chat_types.ChatCompletionMessageParam],
        stream: openai.AsyncStream[openai_chat_types.ChatCompletionChunk],
        evaluation_enabled: bool,
        chat_completion_params: ChatCompletionParams,
        timing: RequestTimingMetric,
        callback: Optional[EvaluateCallback] = None,
        metadata: dict = {},
    ) -> AsyncIterable[MaitaiChunk]:
        full_body = ""
        last_chunk = None
        async for chunk in stream:
            if last_chunk is None:
                timing.time_first_chunk = time.time()
            maitai_chunk = convert_open_ai_chat_completion_chunk(chunk)
            if maitai_chunk.choices:
                last_chunk = maitai_chunk
                content = maitai_chunk.choices[0].delta.content
                if content is not None:
                    full_body += content
            if maitai_chunk.usage and last_chunk is not None and not last_chunk.usage:
                last_chunk.usage = maitai_chunk.usage
            yield MaitaiChunk.model_validate(maitai_chunk.model_dump())
        timing.time_request_end = time.time()
        if last_chunk is None:
            return
        if evaluation_enabled:
            full_conv = messages + [{"role": "assistant", "content": full_body}]
            await self.evaluator.evaluate_async(
                session_id=session_id,
                reference_id=reference_id,
                intent=intent,
                content_type=EvaluationContentType.MESSAGE,
                content=full_conv,
                application_ref_name=application,
                callback=callback,
                chat_completion_chunk=last_chunk,
                completion_params=chat_completion_params,
                timing=timing,
                metadata=metadata,
            )
        else:
            await self.inference_client.store_chat_response_async(
                session_id=session_id,
                reference_id=reference_id,
                intent=intent,
                application_ref_name=application,
                completion_params=chat_completion_params,
                final_chunk=last_chunk,
                content=full_body,
                chat_completion_response=None,
                timing=timing,
                metadata=metadata,
            )

    async def _process_inference_stream_async(
        self,
        stream: AsyncIterable[InferenceStreamResponse],
        retry_args: dict,
        timing: RequestTimingMetric,
        includes_usage: bool = False,
        push_timing_metrics: bool = True,
    ) -> AsyncIterable[MaitaiChunk]:
        first = True
        try:
            async for infer_resp in stream:
                if infer_resp.warning:
                    warnings.warn(infer_resp.warning, InferenceWarning)
                if infer_resp.error:
                    raise InferenceException(infer_resp.error)
                chunk = infer_resp.chat_completion_chunk
                if chunk is not None:
                    if first:
                        timing.time_first_chunk = time.time()
                        timing.request_id = chunk.request_id
                        first = False
                    yield MaitaiChunk.model_validate(chunk.model_dump())
                    if chunk.choices and chunk.choices[0].finish_reason:
                        timing.time_request_end = time.time()
                        if push_timing_metrics:
                            asyncio.create_task(
                                self.inference_client.send_request_timing_data_async(
                                    timing
                                )
                            )
                    if chunk.choices and chunk.choices[0].finish_reason:
                        return
        except MaitaiConnectionError as e:
            if "gpt" not in retry_args.get("model", "") and "gpt" in (
                retry_args.get("fallback_model", "") or ""
            ):
                retry_args["model"] = retry_args["fallback_model"]
            if "gpt" in retry_args.get("model", ""):
                retry_args["model"] = retry_args["model"].replace("openai:", "")
                logger.warning("Maitai issue, retrying on client side")
                response = await self.create(**retry_args)
                async for resp in response:
                    yield resp
            else:
                raise e
