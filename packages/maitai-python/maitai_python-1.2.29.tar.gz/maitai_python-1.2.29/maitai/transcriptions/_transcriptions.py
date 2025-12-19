import io
import json
from typing import BinaryIO, Iterator, Mapping, Optional, Union

import httpx
import openai
from openai._types import NOT_GIVEN, NotGiven
from openai.types.audio import Transcription
from openai.types.audio.transcription_text_delta_event import (
    TranscriptionTextDeltaEvent,
)

from maitai._config import Config


class Transcriptions:
    def __init__(self, config: Config):
        self.config = config

    def _get_client_config(self):
        """Get base_url and api_key using Maitai's config infrastructure."""
        base_url = self.config.maitai_transcription_host
        api_key = self.config.api_key
        return base_url, api_key

    def _create_multipart_form_data(
        self,
        file: Union[str, BinaryIO, tuple],
        model: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[float] = None,
        timestamp_granularities: Optional[list[str]] = None,
        stream: Optional[bool] = None,
        application: Optional[str] = None,
        intent: Optional[str] = None,
        session_id: Optional[str] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        extra_query: Optional[Mapping[str, object]] = None,
        extra_body: Optional[Mapping[str, object]] = None,
    ) -> tuple[bytes, str]:
        """Create multipart form data for the transcription request."""

        # Create multipart form data
        boundary = "----WebKitFormBoundary" + "".join(
            str(ord(c)) for c in "1234567890abcdef"[:16]
        )
        body = io.BytesIO()

        def write_field(name: str, value: str):
            body.write(f"--{boundary}\r\n".encode())
            body.write(
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
            )
            body.write(f"{value}\r\n".encode())

        def write_file_field(
            name: str, filename: str, content: bytes, content_type: str
        ):
            body.write(f"--{boundary}\r\n".encode())
            body.write(
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode()
            )
            body.write(f"Content-Type: {content_type}\r\n\r\n".encode())
            body.write(content)
            body.write(b"\r\n")

        # Handle file parameter
        if isinstance(file, tuple):
            # Tuple format: (filename, content, content_type)
            filename, content, content_type = file
            if hasattr(content, "read") and callable(getattr(content, "read")):
                content = content.read()
            elif isinstance(content, str):
                content = content.encode("utf-8")
            elif not isinstance(content, bytes):
                raise ValueError(f"Unsupported content type in tuple: {type(content)}")
        elif isinstance(file, str):
            # String filename
            with open(file, "rb") as f:
                content = f.read()
            filename = file
            content_type = "audio/wav"
        elif hasattr(file, "read") and callable(getattr(file, "read")):
            # File-like object
            content = file.read()
            filename = getattr(file, "name", "audio.wav")
            content_type = "audio/wav"
        else:
            raise ValueError(f"Unsupported file type: {type(file)}")

        # Add file field
        write_file_field("file", filename, content, content_type)

        # Add other fields
        write_field("model", model)

        if language:
            write_field("language", language)
        if prompt:
            write_field("prompt", prompt)
        if response_format:
            write_field("response_format", response_format)
        if temperature is not None:
            write_field("temperature", str(temperature))
        if timestamp_granularities:
            for granularity in timestamp_granularities:
                write_field("timestamp_granularities[]", granularity)
        if stream is not None:
            write_field("stream", "true" if stream else "false")

        if extra_query:
            for key, value in extra_query.items():
                write_field(key, json.dumps(value))
        if extra_body:
            for key, value in extra_body.items():
                write_field(key, json.dumps(value))

        # Add Maitai-specific fields
        if application:
            write_field("application", application)
        if intent:
            write_field("intent", intent)
        if session_id:
            write_field("session_id", session_id)

        body.write(f"--{boundary}--\r\n".encode())

        content_type = f"multipart/form-data; boundary={boundary}"
        return body.getvalue(), content_type

    def _make_request(
        self,
        data: bytes,
        content_type: str,
        stream: bool = False,
        response_format: Optional[str] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        timeout: Union[float, openai.Timeout, None, NotGiven] = NOT_GIVEN,
    ):
        """Make the HTTP request to the transcription endpoint."""
        base_url, api_key = self._get_client_config()

        # Construct the URL
        url = f"{base_url.rstrip('/')}/audio/transcriptions"

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": content_type,
        }

        if extra_headers:
            headers.update(extra_headers)

        # Set up timeout
        if timeout is NOT_GIVEN or timeout is None:
            timeout_value = 60.0
        elif isinstance(timeout, (int, float)):
            timeout_value = float(timeout)
        else:
            # Handle openai.Timeout object
            timeout_value = 60.0

        # Make the request
        with httpx.Client(timeout=timeout_value) as client:
            response = client.post(url, content=data, headers=headers)
            response.raise_for_status()

            if stream:
                # For streaming, return a generator that processes the response line by line
                return self._stream_response(response)
            else:
                # Check if response is text format
                content_type = response.headers.get("content-type", "")
                if "text/plain" in content_type or response_format == "text":
                    # Return plain text response
                    return response.text
                else:
                    # For non-streaming, return the JSON response
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        return Transcription(**response_data)
                    else:
                        # If response is plain text (response_format="text")
                        return response_data

    def _stream_response(
        self, response: httpx.Response
    ) -> Iterator[TranscriptionTextDeltaEvent]:
        """Stream the response line by line to avoid loading entire response into memory."""
        for line in response.iter_lines():
            line = line.strip()
            if line.startswith("data: "):
                data_str = line[6:]  # Remove 'data: ' prefix
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    # Handle the ASRChunk format from the Go backend
                    if isinstance(data, dict):
                        # Extract text from the ASRChunk format
                        text = ""
                        if "text" in data and data["text"] is not None:
                            text = data["text"]
                        elif (
                            "delta" in data
                            and isinstance(data["delta"], dict)
                            and "text" in data["delta"]
                            and data["delta"]["text"] is not None
                        ):
                            text = data["delta"]["text"]

                        # Yield all chunks, including empty ones, to match Go backend behavior
                        # This ensures we get the same number of chunks as the OpenAI SDK
                        yield TranscriptionTextDeltaEvent(
                            type="transcript.text.delta", delta=text
                        )
                except json.JSONDecodeError:
                    continue

    def create(
        self,
        *,
        file: Union[str, BinaryIO, tuple],
        model: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[float] = None,
        timestamp_granularities: Optional[list[str]] = None,
        stream: Optional[bool] = None,
        application: Optional[str] = None,
        intent: Optional[str] = None,
        session_id: Optional[str] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        extra_query: Optional[Mapping[str, object]] = None,
        extra_body: Optional[Mapping[str, object]] = None,
        timeout: Union[float, openai.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> Union[Transcription, str, Iterator[TranscriptionTextDeltaEvent]]:
        """
        Create a transcription of the given audio file.

        Args:
            file: The audio file to transcribe (can be a file path, file-like object, or tuple)
            model: The model to use for transcription
            language: Language of the audio (optional)
            prompt: Prompt for the transcription (optional)
            response_format: Format of the response ("json", "text", "verbose_json")
            temperature: Temperature for sampling (optional)
            timestamp_granularities: Granularities for timestamps (optional)
            stream: Whether to stream the response (optional)
            application: Maitai application name (optional)
            intent: Maitai intent name (optional)
            session_id: Maitai session ID (optional)
            extra_headers: Extra headers to include (optional)
            extra_query: Extra query parameters (optional)
            extra_body: Extra body parameters (optional)
            timeout: Request timeout (optional)

        Returns:
            Transcription object or iterator of streaming events
        """
        # Create multipart form data
        data, content_type = self._create_multipart_form_data(
            file=file,
            model=model,
            language=language,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
            timestamp_granularities=timestamp_granularities,
            stream=stream,
            application=application,
            intent=intent,
            session_id=session_id,
            extra_query=extra_query,
            extra_body=extra_body,
        )

        # Make the request
        return self._make_request(
            data=data,
            content_type=content_type,
            stream=stream or False,
            response_format=response_format,
            extra_headers=extra_headers,
            timeout=timeout,
        )
