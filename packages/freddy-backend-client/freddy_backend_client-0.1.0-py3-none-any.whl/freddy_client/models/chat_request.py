from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_request_metadata_type_0 import ChatRequestMetadataType0
    from ..models.input_message import InputMessage
    from ..models.reasoning_config import ReasoningConfig
    from ..models.tool_config import ToolConfig


T = TypeVar("T", bound="ChatRequest")


@_attrs_define
class ChatRequest:
    """Request schema for chat/response endpoint.

    Matches Aitronos API specification with snake_case fields.

        Attributes:
            inputs (list[InputMessage]): Array of input messages. Last user message is the query.
            organization_id (None | str | Unset): Organization ID. Required if user belongs to multiple organizations. Auto-
                selected if user belongs to exactly one organization. Returns error if user belongs to no organizations.
            thread_id (None | str | Unset): Thread ID to continue conversation. Creates new thread if null.
            assistant_id (None | str | Unset): Assistant ID to bind to thread. Can only be set when creating a new thread or
                on the first message. Once a thread has messages, the assistant binding is locked.
            previous_response_id (None | str | Unset): Response ID to reset context from. Messages after this point are
                ignored, enabling conversation reset after message edits.
            model (str | Unset): Model key from the Freddy model catalog (e.g., 'gpt-4o', 'claude-3-5-sonnet') Default:
                'gpt-4o'.
            tools (list[ToolConfig] | None | Unset): Array of tool configurations to enable during conversation
            stream (bool | Unset): Enable streaming (SSE). Default false returns complete response. Default: False.
            instructions (None | str | Unset): System instructions defining model behavior
            temperature (float | None | Unset): Randomness (0.0-1.0). Lower=focused, higher=creative
            top_p (float | None | Unset): Nucleus sampling (0.0-1.0). Alternative to temperature. Note: Some models only
                support one sampling parameter; if both are provided, an error will be returned.
            max_output_synapses (int | None | Unset): Maximum output length (tokens)
            reasoning (None | ReasoningConfig | Unset): Unified reasoning configuration for reasoning-capable models.
                Controls computational effort and optional reasoning summary. API automatically maps to provider-specific
                parameters.
            include (list[str] | None | Unset): Specify additional data to include in the response. Options: 'all',
                'tools.available', 'tools.used', 'web_search.sources', 'code_interpreter.outputs', 'file_search.results',
                'message.logprobs', 'reasoning.encrypted', 'request.logs', 'usage.detailed', 'rules.debug', 'rules'
            metadata (ChatRequestMetadataType0 | None | Unset): Custom key-value pairs for tracking
            disable_rules (bool | Unset): Disable user-level rule application (assistant, user, vector_store). System-level
                rules (model, organization) are always applied. Default: False.
            store (bool | Unset): Controls thread visibility. When true (default), thread appears in list. When false,
                thread is hidden from list (useful for internal operations, background tasks). Default: True.
            output_mode (None | str | Unset): Response format mode. Options: 'text' (default, rich text with markdown),
                'plain' (plain text with all formatting removed), 'blocks' (typed blocks for custom UI rendering). Affects both
                streaming events and response_blocks field.
    """

    inputs: list[InputMessage]
    organization_id: None | str | Unset = UNSET
    thread_id: None | str | Unset = UNSET
    assistant_id: None | str | Unset = UNSET
    previous_response_id: None | str | Unset = UNSET
    model: str | Unset = "gpt-4o"
    tools: list[ToolConfig] | None | Unset = UNSET
    stream: bool | Unset = False
    instructions: None | str | Unset = UNSET
    temperature: float | None | Unset = UNSET
    top_p: float | None | Unset = UNSET
    max_output_synapses: int | None | Unset = UNSET
    reasoning: None | ReasoningConfig | Unset = UNSET
    include: list[str] | None | Unset = UNSET
    metadata: ChatRequestMetadataType0 | None | Unset = UNSET
    disable_rules: bool | Unset = False
    store: bool | Unset = True
    output_mode: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.chat_request_metadata_type_0 import ChatRequestMetadataType0
        from ..models.reasoning_config import ReasoningConfig

        inputs = []
        for inputs_item_data in self.inputs:
            inputs_item = inputs_item_data.to_dict()
            inputs.append(inputs_item)

        organization_id: None | str | Unset
        if isinstance(self.organization_id, Unset):
            organization_id = UNSET
        else:
            organization_id = self.organization_id

        thread_id: None | str | Unset
        if isinstance(self.thread_id, Unset):
            thread_id = UNSET
        else:
            thread_id = self.thread_id

        assistant_id: None | str | Unset
        if isinstance(self.assistant_id, Unset):
            assistant_id = UNSET
        else:
            assistant_id = self.assistant_id

        previous_response_id: None | str | Unset
        if isinstance(self.previous_response_id, Unset):
            previous_response_id = UNSET
        else:
            previous_response_id = self.previous_response_id

        model = self.model

        tools: list[dict[str, Any]] | None | Unset
        if isinstance(self.tools, Unset):
            tools = UNSET
        elif isinstance(self.tools, list):
            tools = []
            for tools_type_0_item_data in self.tools:
                tools_type_0_item = tools_type_0_item_data.to_dict()
                tools.append(tools_type_0_item)

        else:
            tools = self.tools

        stream = self.stream

        instructions: None | str | Unset
        if isinstance(self.instructions, Unset):
            instructions = UNSET
        else:
            instructions = self.instructions

        temperature: float | None | Unset
        if isinstance(self.temperature, Unset):
            temperature = UNSET
        else:
            temperature = self.temperature

        top_p: float | None | Unset
        if isinstance(self.top_p, Unset):
            top_p = UNSET
        else:
            top_p = self.top_p

        max_output_synapses: int | None | Unset
        if isinstance(self.max_output_synapses, Unset):
            max_output_synapses = UNSET
        else:
            max_output_synapses = self.max_output_synapses

        reasoning: dict[str, Any] | None | Unset
        if isinstance(self.reasoning, Unset):
            reasoning = UNSET
        elif isinstance(self.reasoning, ReasoningConfig):
            reasoning = self.reasoning.to_dict()
        else:
            reasoning = self.reasoning

        include: list[str] | None | Unset
        if isinstance(self.include, Unset):
            include = UNSET
        elif isinstance(self.include, list):
            include = self.include

        else:
            include = self.include

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, ChatRequestMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        disable_rules = self.disable_rules

        store = self.store

        output_mode: None | str | Unset
        if isinstance(self.output_mode, Unset):
            output_mode = UNSET
        else:
            output_mode = self.output_mode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inputs": inputs,
            }
        )
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if thread_id is not UNSET:
            field_dict["thread_id"] = thread_id
        if assistant_id is not UNSET:
            field_dict["assistant_id"] = assistant_id
        if previous_response_id is not UNSET:
            field_dict["previous_response_id"] = previous_response_id
        if model is not UNSET:
            field_dict["model"] = model
        if tools is not UNSET:
            field_dict["tools"] = tools
        if stream is not UNSET:
            field_dict["stream"] = stream
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if top_p is not UNSET:
            field_dict["top_p"] = top_p
        if max_output_synapses is not UNSET:
            field_dict["max_output_synapses"] = max_output_synapses
        if reasoning is not UNSET:
            field_dict["reasoning"] = reasoning
        if include is not UNSET:
            field_dict["include"] = include
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if disable_rules is not UNSET:
            field_dict["disable_rules"] = disable_rules
        if store is not UNSET:
            field_dict["store"] = store
        if output_mode is not UNSET:
            field_dict["output_mode"] = output_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_request_metadata_type_0 import ChatRequestMetadataType0
        from ..models.input_message import InputMessage
        from ..models.reasoning_config import ReasoningConfig
        from ..models.tool_config import ToolConfig

        d = dict(src_dict)
        inputs = []
        _inputs = d.pop("inputs")
        for inputs_item_data in _inputs:
            inputs_item = InputMessage.from_dict(inputs_item_data)

            inputs.append(inputs_item)

        def _parse_organization_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        organization_id = _parse_organization_id(d.pop("organization_id", UNSET))

        def _parse_thread_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        thread_id = _parse_thread_id(d.pop("thread_id", UNSET))

        def _parse_assistant_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        assistant_id = _parse_assistant_id(d.pop("assistant_id", UNSET))

        def _parse_previous_response_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        previous_response_id = _parse_previous_response_id(
            d.pop("previous_response_id", UNSET)
        )

        model = d.pop("model", UNSET)

        def _parse_tools(data: object) -> list[ToolConfig] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tools_type_0 = []
                _tools_type_0 = data
                for tools_type_0_item_data in _tools_type_0:
                    tools_type_0_item = ToolConfig.from_dict(tools_type_0_item_data)

                    tools_type_0.append(tools_type_0_item)

                return tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ToolConfig] | None | Unset, data)

        tools = _parse_tools(d.pop("tools", UNSET))

        stream = d.pop("stream", UNSET)

        def _parse_instructions(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        instructions = _parse_instructions(d.pop("instructions", UNSET))

        def _parse_temperature(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        temperature = _parse_temperature(d.pop("temperature", UNSET))

        def _parse_top_p(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        top_p = _parse_top_p(d.pop("top_p", UNSET))

        def _parse_max_output_synapses(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_output_synapses = _parse_max_output_synapses(
            d.pop("max_output_synapses", UNSET)
        )

        def _parse_reasoning(data: object) -> None | ReasoningConfig | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                reasoning_type_0 = ReasoningConfig.from_dict(data)

                return reasoning_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReasoningConfig | Unset, data)

        reasoning = _parse_reasoning(d.pop("reasoning", UNSET))

        def _parse_include(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                include_type_0 = cast(list[str], data)

                return include_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        include = _parse_include(d.pop("include", UNSET))

        def _parse_metadata(data: object) -> ChatRequestMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = ChatRequestMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChatRequestMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        disable_rules = d.pop("disable_rules", UNSET)

        store = d.pop("store", UNSET)

        def _parse_output_mode(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        output_mode = _parse_output_mode(d.pop("output_mode", UNSET))

        chat_request = cls(
            inputs=inputs,
            organization_id=organization_id,
            thread_id=thread_id,
            assistant_id=assistant_id,
            previous_response_id=previous_response_id,
            model=model,
            tools=tools,
            stream=stream,
            instructions=instructions,
            temperature=temperature,
            top_p=top_p,
            max_output_synapses=max_output_synapses,
            reasoning=reasoning,
            include=include,
            metadata=metadata,
            disable_rules=disable_rules,
            store=store,
            output_mode=output_mode,
        )

        chat_request.additional_properties = d
        return chat_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
