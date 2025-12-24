"""OTLP-based LangChain integration using standard OpenTelemetry spans.

This module provides a callback handler that traces LangChain operations
using standard OpenTelemetry spans, making it portable to any OTLP backend.

Usage:
    from lumenova_beacon import BeaconClient
    from lumenova_beacon import BeaconCallbackHandler
    from langchain_openai import ChatOpenAI

    # Initialize BeaconClient with OTLP (sets up TracerProvider)
    client = BeaconClient()

    # Create OTEL-based callback handler
    handler = BeaconCallbackHandler()

    # Use with LangChain
    llm = ChatOpenAI()
    response = llm.invoke("Hello", config={"callbacks": [handler]})

Environment Variables:
    BEACON_ENDPOINT - Beacon API endpoint (for OTLP export)
    BEACON_API_KEY - Beacon API key (for OTLP export)
    BEACON_SESSION_ID - Default session ID (optional)
"""

import json
import logging
import time
from typing import Any, Sequence
from uuid import UUID

from opentelemetry import trace, context as otel_context
from opentelemetry.trace import Status, StatusCode, SpanKind

from lumenova_beacon.core.client import get_client
from lumenova_beacon.types import SpanType

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.agents import AgentAction, AgentFinish
    from langchain_core.documents import Document
    from langchain_core.messages import BaseMessage
    from langchain_core.outputs import LLMResult
except ImportError:
    raise ImportError(
        "langchain-core is required for LangChain OTLP integration. "
        "Install it with: pip install langchain-core"
    )

logger = logging.getLogger(__name__)


class BeaconCallbackHandler(BaseCallbackHandler):
    """OTEL-based callback handler for tracing LangChain operations.

    Spans are exported via the configured TracerProvider/SpanExporter, making
    this handler portable to any OTLP-compatible backend.

    Handles:
    - Chain operations (on_chain_start/end/error)
    - LLM calls (on_llm_start/end/error, on_chat_model_start)
    - Tool invocations (on_tool_start/end/error)
    - Retriever queries (on_retriever_start/end/error)
    - Agent actions (on_agent_action/finish)

    Example:
        >>> from lumenova_beacon import BeaconClient
        >>> from lumenova_beacon import BeaconCallbackHandler
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> # Initialize BeaconClient with OTLP (sets up TracerProvider)
        >>> client = BeaconClient()
        >>>
        >>> # Create OTEL-based callback handler
        >>> handler = BeaconCallbackHandler()
        >>>
        >>> # Use with LangChain
        >>> llm = ChatOpenAI()
        >>> response = llm.invoke("Hello", config={"callbacks": [handler]})
    """

    # Span type attributes
    ATTR_SPAN_TYPE = "beacon.span_type"
    ATTR_COMPONENT_TYPE = "langchain.component_type"

    # GenAI semantic conventions
    # See: https://opentelemetry.io/docs/specs/semconv/gen-ai/
    ATTR_LLM_SYSTEM = "gen_ai.system"
    ATTR_LLM_MODEL = "gen_ai.request.model"
    ATTR_LLM_PROMPT = "gen_ai.prompt"
    ATTR_LLM_COMPLETION = "gen_ai.completion"
    ATTR_LLM_PROMPT_TOKENS = "gen_ai.usage.prompt_tokens"
    ATTR_LLM_COMPLETION_TOKENS = "gen_ai.usage.completion_tokens"
    ATTR_LLM_TOTAL_TOKENS = "gen_ai.usage.total_tokens"

    # TTFT (Time-to-First-Token) attributes
    ATTR_TTFT_MS = "gen_ai.response.time_to_first_token_ms"
    ATTR_STREAMING = "gen_ai.request.streaming"

    # LangChain-specific attributes
    ATTR_LANGCHAIN_INPUT = "langchain.input"
    ATTR_LANGCHAIN_OUTPUT = "langchain.output"

    # GenAI Agent attributes (OTEL standard)
    ATTR_AGENT_NAME = "gen_ai.agent.name"
    ATTR_AGENT_ID = "gen_ai.agent.id"
    ATTR_AGENT_DESCRIPTION = "gen_ai.agent.description"

    # Deployment attributes (OTEL standard)
    ATTR_DEPLOYMENT_ENVIRONMENT = "deployment.environment.name"

    # Model request parameters (OTEL standard)
    ATTR_REQUEST_TEMPERATURE = "gen_ai.request.temperature"
    ATTR_REQUEST_TOP_P = "gen_ai.request.top_p"
    ATTR_REQUEST_TOP_K = "gen_ai.request.top_k"
    ATTR_REQUEST_MAX_TOKENS = "gen_ai.request.max_tokens"
    ATTR_REQUEST_FREQUENCY_PENALTY = "gen_ai.request.frequency_penalty"
    ATTR_REQUEST_PRESENCE_PENALTY = "gen_ai.request.presence_penalty"

    # Beacon-specific attributes
    ATTR_BEACON_SESSION_ID = "beacon.session_id"
    ATTR_BEACON_METADATA_PREFIX = "beacon.metadata."

    def __init__(
        self,
        tracer_name: str = "lumenova_beacon.langchain",
        session_id: str | None = None,
        environment: str | None = None,
        agent_name: str | None = None,
        agent_id: str | None = None,
        agent_description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Initialize the OTEL-based LangChain callback handler.

        Args:
            tracer_name: Name for the OpenTelemetry tracer
            session_id: Default session ID for all spans (optional)
            environment: Environment name (e.g., "production", "staging", "development")
                Maps to OTEL attribute: deployment.environment.name
            agent_name: Human-readable name of the GenAI agent
                Maps to OTEL attribute: gen_ai.agent.name
            agent_id: Unique identifier of the GenAI agent
                Maps to OTEL attribute: gen_ai.agent.id
            agent_description: Description of the GenAI agent
                Maps to OTEL attribute: gen_ai.agent.description
            metadata: Custom metadata dict to add to all spans (key-value pairs)
                Maps to OTEL attributes: beacon.metadata.*
        """
        super().__init__()
        self._tracer = trace.get_tracer(tracer_name)
        self._session_id = session_id if session_id is not None else self.client.config.session_id
        self._environment = environment
        self._agent_name = agent_name
        self._agent_id = agent_id
        self._agent_description = agent_description
        self._metadata = metadata or {}

        # Track active spans by run_id
        self._runs: dict[str, dict[str, Any]] = {}
        # Persistent context store - survives span end for parent context lookup
        self._contexts: dict[str, Any] = {}
        self._langgraph_parent_ids: set[str] = set()

        # TTFT tracking for streaming calls
        self._first_token_times: dict[str, float | None] = {}  # run_id -> first token timestamp
        self._start_perf_times: dict[str, float] = {}  # run_id -> high-precision start time

        logger.debug(f"Initialized BeaconCallbackHandler with tracer: {tracer_name}")

    @property
    def client(self):
        return get_client()

    def _serialize_for_json(self, obj: Any) -> Any:
        """Recursively serialize an object to ensure JSON compatibility.

        Args:
            obj: Object to serialize

        Returns:
            JSON-compatible representation of the object
        """
        if obj is None:
            return None

        if isinstance(obj, (str, int, float, bool)):
            return obj

        if isinstance(obj, UUID):
            return str(obj)

        if isinstance(obj, BaseMessage):
            result = {
                "role": obj.type if hasattr(obj, "type") else "unknown",
                "content": obj.content if hasattr(obj, "content") else str(obj),
            }
            if hasattr(obj, "additional_kwargs") and obj.additional_kwargs:
                result["additional_kwargs"] = self._serialize_for_json(obj.additional_kwargs)
            return result

        if isinstance(obj, Document):
            return {
                "page_content": obj.page_content,
                "metadata": self._serialize_for_json(obj.metadata) if hasattr(obj, "metadata") else {},
            }

        if isinstance(obj, dict):
            return {key: self._serialize_for_json(value) for key, value in obj.items()}

        if isinstance(obj, (list, tuple)):
            return [self._serialize_for_json(item) for item in obj]

        if isinstance(obj, set):
            return [self._serialize_for_json(item) for item in obj]

        # Handle Pydantic models
        if hasattr(obj, "model_dump"):
            try:
                return self._serialize_for_json(obj.model_dump())
            except Exception:
                pass
        elif hasattr(obj, "dict"):
            try:
                return self._serialize_for_json(obj.dict())
            except Exception:
                pass

        try:
            return str(obj)
        except Exception:
            return "<unserializable>"

    def _extract_name(self, serialized: dict[str, Any], **kwargs: Any) -> str:
        """Extract component name from serialized data.

        Args:
            serialized: Component's serialized definition
            **kwargs: Additional arguments

        Returns:
            Component name string
        """
        try:
            if "name" in kwargs and kwargs["name"] is not None:
                return str(kwargs["name"])
            if "name" in serialized:
                return serialized["name"]
            if "id" in serialized and isinstance(serialized["id"], list):
                return serialized["id"][-1] if serialized["id"] else "Unknown"
            return "Unknown"
        except Exception as e:
            logger.debug(f"Error extracting component name: {e}")
            return "Unknown"

    def _has_langgraph_metadata(
        self,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        """Check if this span has LangGraph-specific metadata.

        Args:
            metadata: Callback metadata
            tags: Callback tags

        Returns:
            True if this span has LangGraph metadata
        """
        try:
            if metadata:
                for key in metadata.keys():
                    if key.startswith("langgraph_"):
                        return True

            if tags:
                for tag in tags:
                    if isinstance(tag, str) and tag.startswith("graph:step:"):
                        return True

            return False
        except Exception:
            return False

    def _set_model_parameters(self, span: Any, kwargs: dict[str, Any]) -> None:
        """Extract and set model parameters as OTEL standard attributes.

        Args:
            span: The OTEL span to set attributes on
            kwargs: The kwargs dict from serialized model data
        """
        # Map LangChain parameter names to OTEL standard attributes
        param_mapping = {
            "temperature": self.ATTR_REQUEST_TEMPERATURE,
            "top_p": self.ATTR_REQUEST_TOP_P,
            "top_k": self.ATTR_REQUEST_TOP_K,
            "max_tokens": self.ATTR_REQUEST_MAX_TOKENS,
            "max_output_tokens": self.ATTR_REQUEST_MAX_TOKENS,  # Alternative name
            "frequency_penalty": self.ATTR_REQUEST_FREQUENCY_PENALTY,
            "presence_penalty": self.ATTR_REQUEST_PRESENCE_PENALTY,
        }

        for param_name, attr_name in param_mapping.items():
            if param_name in kwargs and kwargs[param_name] is not None:
                span.set_attribute(attr_name, kwargs[param_name])

    def _start_span(
        self,
        run_id: UUID,
        parent_run_id: UUID | None,
        name: str,
        span_kind: SpanKind,
        span_type: SpanType,
    ) -> None:
        """Start a new OTEL span for a LangChain operation.

        Args:
            run_id: Unique run identifier
            parent_run_id: Parent run identifier (for nesting)
            name: Span name
            span_kind: OTEL span kind
            span_type: Beacon span type (SpanType enum)
        """
        # Get parent context - check persistent store if not in active runs
        context = None
        if parent_run_id:
            parent_key = str(parent_run_id)
            if parent_key in self._runs:
                context = self._runs[parent_key].get("context")
            elif parent_key in self._contexts:
                # Parent span ended but context preserved for child spans
                context = self._contexts[parent_key]

        # Start span with parent context
        span = self._tracer.start_span(
            name,
            kind=span_kind,
            context=context,
        )

        # Set common attributes
        span.set_attribute(self.ATTR_SPAN_TYPE, span_type.value)
        span.set_attribute(self.ATTR_COMPONENT_TYPE, name)

        if self._session_id:
            span.set_attribute(self.ATTR_BEACON_SESSION_ID, self._session_id)

        # Set deployment environment (OTEL standard)
        if self._environment:
            span.set_attribute(self.ATTR_DEPLOYMENT_ENVIRONMENT, self._environment)

        # Set agent attributes (OTEL standard)
        if self._agent_name:
            span.set_attribute(self.ATTR_AGENT_NAME, self._agent_name)
        if self._agent_id:
            span.set_attribute(self.ATTR_AGENT_ID, self._agent_id)
        if self._agent_description:
            span.set_attribute(self.ATTR_AGENT_DESCRIPTION, self._agent_description)

        # Set custom metadata
        if self._metadata:
            for key, value in self._metadata.items():
                attr_key = f"{self.ATTR_BEACON_METADATA_PREFIX}{key}"
                if isinstance(value, (str, int, float, bool)):
                    span.set_attribute(attr_key, value)
                else:
                    span.set_attribute(attr_key, json.dumps(value, default=str))

        # Store context persistently for future children
        span_context = trace.set_span_in_context(span)
        self._contexts[str(run_id)] = span_context

        # ATTACH the context to make span "current" during execution
        # This allows @trace decorated functions to find the parent span
        token = otel_context.attach(span_context)

        # Store span, context, and token in active runs
        self._runs[str(run_id)] = {
            "span": span,
            "context": span_context,
            "context_token": token,
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "start_perf_time": time.perf_counter(),  # High-precision start time for TTFT
        }

    def _end_span(self, run_id: UUID, error: BaseException | None = None) -> None:
        """End an OTEL span.

        Args:
            run_id: Run identifier of the span to end
            error: Optional exception if the operation failed
        """
        run_id_str = str(run_id)
        if run_id_str not in self._runs:
            return

        run_data = self._runs[run_id_str]
        span = run_data["span"]

        # Note: We intentionally do NOT call otel_context.detach() here.
        # In async code (LangGraph, etc.), context tokens created in one coroutine
        # cannot be detached in another, and OpenTelemetry logs errors before
        # propagating exceptions. The span still works correctly without detach.

        if error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
        else:
            span.set_status(Status(StatusCode.OK))

        span.end()

        # If this is a root span (no parent), clean up all contexts for this trace
        if run_data.get("parent_run_id") is None:
            self._cleanup_trace_contexts(run_id_str)

        del self._runs[run_id_str]

    def _cleanup_trace_contexts(self, root_run_id: str) -> None:
        """Clean up stored contexts for a completed trace.

        This prevents memory leaks by removing contexts when the root span ends.

        Args:
            root_run_id: Run ID of the root span that just ended
        """
        try:
            if root_run_id not in self._contexts:
                return

            # Get the trace_id from the root span's context
            root_context = self._contexts[root_run_id]
            root_span = trace.get_current_span(root_context)
            if root_span is None:
                return

            root_span_context = root_span.get_span_context()
            root_trace_id = root_span_context.trace_id

            # Remove all contexts with the same trace_id
            to_remove = []
            for run_id, context in self._contexts.items():
                span = trace.get_current_span(context)
                if span is not None:
                    span_context = span.get_span_context()
                    if span_context.trace_id == root_trace_id:
                        to_remove.append(run_id)

            for run_id in to_remove:
                del self._contexts[run_id]

        except Exception as e:
            logger.debug(f"Error cleaning up trace contexts: {e}")

    # Chain callbacks

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle chain start event."""
        try:
            name = self._extract_name(serialized, **kwargs)

            # Check for LangGraph metadata
            if parent_run_id and self._has_langgraph_metadata(metadata=metadata, tags=tags):
                self._langgraph_parent_ids.add(str(parent_run_id))

            self._start_span(run_id, parent_run_id, name, SpanKind.INTERNAL, SpanType.CHAIN)

            if str(run_id) in self._runs:
                span = self._runs[str(run_id)]["span"]
                serialized_inputs = self._serialize_for_json(inputs)
                span.set_attribute(self.ATTR_LANGCHAIN_INPUT, json.dumps(serialized_inputs, default=str))

                # Set metadata as attributes
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            span.set_attribute(f"langchain.metadata.{key}", value)
                        else:
                            span.set_attribute(f"langchain.metadata.{key}", json.dumps(value, default=str))

                if tags:
                    span.set_attribute("langchain.tags", json.dumps(tags))

                # Try to extract graph name from LangGraph metadata if agent_name not set
                if not self._agent_name and metadata:
                    graph_name = metadata.get("langgraph_checkpoint_ns") or metadata.get("name")
                    if graph_name:
                        span.set_attribute(self.ATTR_AGENT_NAME, graph_name)

        except Exception as e:
            logger.error(f"Error in on_chain_start: {e}")

    def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle chain end event."""
        try:
            if str(run_id) in self._runs:
                span = self._runs[str(run_id)]["span"]
                serialized_outputs = self._serialize_for_json(outputs)
                span.set_attribute(self.ATTR_LANGCHAIN_OUTPUT, json.dumps(serialized_outputs, default=str))

                # Handle LangGraph parent detection
                if str(run_id) in self._langgraph_parent_ids:
                    if parent_run_id is None:
                        span.set_attribute(self.ATTR_SPAN_TYPE, SpanType.AGENT.value)
                    self._langgraph_parent_ids.discard(str(run_id))

            self._end_span(run_id)

        except Exception as e:
            logger.error(f"Error in on_chain_end: {e}")

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle chain error event."""
        try:
            self._langgraph_parent_ids.discard(str(run_id))
            self._end_span(run_id, error)
        except Exception as e:
            logger.error(f"Error in on_chain_error: {e}")

    # LLM callbacks

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle LLM start event (for non-chat models)."""
        try:
            name = self._extract_name(serialized, **kwargs)
            self._start_span(run_id, parent_run_id, name, SpanKind.CLIENT, SpanType.GENERATION)

            # Initialize TTFT tracking (None means waiting for first token)
            self._first_token_times[str(run_id)] = None

            if str(run_id) in self._runs:
                span = self._runs[str(run_id)]["span"]
                span.set_attribute(self.ATTR_LLM_SYSTEM, "langchain")
                span.set_attribute(self.ATTR_LLM_PROMPT, json.dumps(prompts, default=str))

                # Extract model name and parameters from serialized kwargs
                if "kwargs" in serialized:
                    model_kwargs = serialized["kwargs"]
                    if "model_name" in model_kwargs:
                        span.set_attribute(self.ATTR_LLM_MODEL, model_kwargs["model_name"])
                    # Extract model parameters (OTEL standard)
                    self._set_model_parameters(span, model_kwargs)

        except Exception as e:
            logger.error(f"Error in on_llm_start: {e}")

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle chat model start event."""
        try:
            name = self._extract_name(serialized, **kwargs)
            self._start_span(run_id, parent_run_id, name, SpanKind.CLIENT, SpanType.GENERATION)

            # Initialize TTFT tracking (None means waiting for first token)
            self._first_token_times[str(run_id)] = None

            if str(run_id) in self._runs:
                span = self._runs[str(run_id)]["span"]
                span.set_attribute(self.ATTR_LLM_SYSTEM, "langchain")

                # Serialize messages
                flat_messages = [msg for batch in messages for msg in batch]
                serialized_messages = [self._serialize_for_json(msg) for msg in flat_messages]
                span.set_attribute(self.ATTR_LLM_PROMPT, json.dumps(serialized_messages, default=str))

                # Extract model name and parameters from serialized kwargs
                if "kwargs" in serialized:
                    model_kwargs = serialized["kwargs"]
                    if "model_name" in model_kwargs:
                        span.set_attribute(self.ATTR_LLM_MODEL, model_kwargs["model_name"])
                    # Extract model parameters (OTEL standard)
                    self._set_model_parameters(span, model_kwargs)

                # Include tools if present
                tools = kwargs.get("invocation_params", {}).get("tools")
                if tools:
                    span.set_attribute("langchain.tools", json.dumps(tools, default=str))

        except Exception as e:
            logger.error(f"Error in on_chat_model_start: {e}")

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle LLM end event."""
        try:
            run_id_str = str(run_id)
            if run_id_str in self._runs:
                span = self._runs[run_id_str]["span"]

                # Extract response
                if response.generations and response.generations[0]:
                    gen = response.generations[0][0]
                    if hasattr(gen, "message"):
                        serialized_output = self._serialize_for_json(gen.message)
                        span.set_attribute(self.ATTR_LLM_COMPLETION, json.dumps(serialized_output, default=str))
                    elif hasattr(gen, "text"):
                        span.set_attribute(self.ATTR_LLM_COMPLETION, json.dumps({"text": gen.text}, default=str))

                # Extract usage
                if response.llm_output:
                    usage = response.llm_output.get("token_usage") or response.llm_output.get("usage", {})
                    if usage:
                        span.set_attribute(self.ATTR_LLM_PROMPT_TOKENS, usage.get("prompt_tokens", 0))
                        span.set_attribute(self.ATTR_LLM_COMPLETION_TOKENS, usage.get("completion_tokens", 0))
                        span.set_attribute(self.ATTR_LLM_TOTAL_TOKENS, usage.get("total_tokens", 0))

                    # Extract model name
                    if "model_name" in response.llm_output:
                        span.set_attribute(self.ATTR_LLM_MODEL, response.llm_output["model_name"])

                # Calculate and set TTFT for streaming calls
                first_token_time = self._first_token_times.pop(run_id_str, None)
                if first_token_time is not None:
                    # Streaming call - calculate TTFT
                    start_perf_time = self._runs[run_id_str].get("start_perf_time")
                    if start_perf_time is not None:
                        ttft_ms = (first_token_time - start_perf_time) * 1000
                        span.set_attribute(self.ATTR_TTFT_MS, ttft_ms)
                        span.set_attribute(self.ATTR_STREAMING, True)
                else:
                    # Clean up tracking state even if no first token was received
                    self._first_token_times.pop(run_id_str, None)

            self._end_span(run_id)

        except Exception as e:
            logger.error(f"Error in on_llm_end: {e}")

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle LLM error event."""
        try:
            # Clean up TTFT tracking state
            self._first_token_times.pop(str(run_id), None)
            self._end_span(run_id, error)
        except Exception as e:
            logger.error(f"Error in on_llm_error: {e}")

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Any = None,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle new token event for streaming LLM calls.

        This callback captures the time-to-first-token (TTFT) metric by
        recording the timestamp when the first token is received.

        Args:
            token: The new token string
            chunk: Optional generation chunk object
            run_id: Unique run identifier
            parent_run_id: Parent run identifier (for nesting)
            **kwargs: Additional arguments
        """
        try:
            run_id_str = str(run_id)

            # Only record the first token time
            if run_id_str in self._first_token_times and self._first_token_times[run_id_str] is None:
                self._first_token_times[run_id_str] = time.perf_counter()

        except Exception as e:
            logger.debug(f"Error in on_llm_new_token: {e}")

    # Tool callbacks

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle tool start event."""
        try:
            name = self._extract_name(serialized, **kwargs)
            self._start_span(run_id, parent_run_id, name, SpanKind.INTERNAL, SpanType.TOOL)

            if str(run_id) in self._runs:
                span = self._runs[str(run_id)]["span"]
                input_data = inputs if inputs else input_str
                serialized_input = self._serialize_for_json(input_data)
                span.set_attribute("tool.input", json.dumps(serialized_input, default=str))

        except Exception as e:
            logger.error(f"Error in on_tool_start: {e}")

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle tool end event."""
        try:
            if str(run_id) in self._runs:
                span = self._runs[str(run_id)]["span"]
                serialized_output = self._serialize_for_json(output)
                # Truncate large outputs
                output_str = json.dumps(serialized_output, default=str)
                if len(output_str) > 10000:
                    output_str = output_str[:10000] + "..."
                span.set_attribute("tool.output", output_str)

            self._end_span(run_id)

        except Exception as e:
            logger.error(f"Error in on_tool_end: {e}")

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle tool error event."""
        try:
            self._end_span(run_id, error)
        except Exception as e:
            logger.error(f"Error in on_tool_error: {e}")

    # Retriever callbacks

    def on_retriever_start(
        self,
        serialized: dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle retriever start event."""
        try:
            name = self._extract_name(serialized, **kwargs)
            self._start_span(run_id, parent_run_id, name, SpanKind.INTERNAL, SpanType.RETRIEVAL)

            if str(run_id) in self._runs:
                span = self._runs[str(run_id)]["span"]
                span.set_attribute("retriever.query", query)

        except Exception as e:
            logger.error(f"Error in on_retriever_start: {e}")

    def on_retriever_end(
        self,
        documents: Sequence[Document],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle retriever end event."""
        try:
            if str(run_id) in self._runs:
                span = self._runs[str(run_id)]["span"]
                span.set_attribute("retriever.document_count", len(documents))

                # Serialize documents
                serialized_docs = [self._serialize_for_json(doc) for doc in documents]
                docs_str = json.dumps(serialized_docs, default=str)
                if len(docs_str) > 10000:
                    docs_str = docs_str[:10000] + "..."
                span.set_attribute("retriever.documents", docs_str)

            self._end_span(run_id)

        except Exception as e:
            logger.error(f"Error in on_retriever_end: {e}")

    def on_retriever_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle retriever error event."""
        try:
            self._end_span(run_id, error)
        except Exception as e:
            logger.error(f"Error in on_retriever_error: {e}")

    # Agent callbacks

    def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle agent action event."""
        try:
            parent_id = str(parent_run_id) if parent_run_id else None
            if parent_id and parent_id in self._runs:
                span = self._runs[parent_id]["span"]
                action_data = {
                    "tool": action.tool,
                    "tool_input": action.tool_input,
                    "log": action.log if hasattr(action, "log") else None,
                }
                span.set_attribute(f"agent.action.{str(run_id)[:8]}", json.dumps(action_data, default=str))

        except Exception as e:
            logger.error(f"Error in on_agent_action: {e}")

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Handle agent finish event."""
        try:
            parent_id = str(parent_run_id) if parent_run_id else None
            if parent_id and parent_id in self._runs:
                span = self._runs[parent_id]["span"]
                finish_data = {
                    "return_values": finish.return_values,
                    "log": finish.log if hasattr(finish, "log") else None,
                }
                span.set_attribute("agent.finish", json.dumps(finish_data, default=str))

        except Exception as e:
            logger.error(f"Error in on_agent_finish: {e}")