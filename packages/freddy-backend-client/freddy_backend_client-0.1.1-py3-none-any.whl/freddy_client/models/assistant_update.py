from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.assistant_update_assistant_metadata_type_0 import (
        AssistantUpdateAssistantMetadataType0,
    )
    from ..models.assistant_update_logit_bias_type_0 import (
        AssistantUpdateLogitBiasType0,
    )
    from ..models.assistant_update_system_message_type_0_item import (
        AssistantUpdateSystemMessageType0Item,
    )
    from ..models.assistant_update_text_config_type_0 import (
        AssistantUpdateTextConfigType0,
    )
    from ..models.reasoning_config_schema import ReasoningConfigSchema
    from ..models.tool_configuration_schema import ToolConfigurationSchema


T = TypeVar("T", bound="AssistantUpdate")


@_attrs_define
class AssistantUpdate:
    """Schema for updating an assistant.

    Attributes:
        name (None | str | Unset):
        description (None | str | Unset):
        avatar_id (None | str | Unset):
        icon_id (None | str | Unset):
        icon_type (None | str | Unset):
        icon_data (None | str | Unset):
        is_default (bool | None | Unset):
        default_model_key (None | str | Unset):
        allowed_model_providers (list[str] | None | Unset):
        instructions (None | str | Unset):
        instructions_thread_id (None | str | Unset):
        system_message (list[AssistantUpdateSystemMessageType0Item] | None | Unset):
        context_strategy (None | str | Unset):
        context_window (int | None | Unset):
        max_tool_calls (int | None | Unset):
        parallel_tool_calls (bool | None | Unset):
        service_tier (None | str | Unset):
        store_responses (bool | None | Unset):
        temperature (float | None | Unset): Randomness (0.0-1.0). Lower=focused, higher=creative
        frequency_penalty (float | None | Unset):
        presence_penalty (float | None | Unset):
        logit_bias (AssistantUpdateLogitBiasType0 | None | Unset):
        top_logprobs (int | None | Unset):
        top_p (float | None | Unset):
        output_mode (None | str | Unset):
        response_format (None | str | Unset):
        seed (int | None | Unset):
        stop_sequences (list[str] | None | Unset):
        max_completion_tokens (int | None | Unset):
        access_mode (None | str | Unset):
        access_departments (list[str] | None | Unset):
        access_users (list[str] | None | Unset):
        editable_by_users (list[str] | None | Unset):
        editable_by_roles (list[str] | None | Unset):
        visible_to_roles (list[str] | None | Unset):
        api_enabled (bool | None | Unset):
        public_enabled (bool | None | Unset):
        is_active (bool | None | Unset):
        streaming (bool | None | Unset):
        memory_enabled (bool | None | Unset):
        moderation_enabled (bool | None | Unset):
        safety_level (None | str | Unset):
        truncation (bool | None | Unset):
        preset_prompts (list[str] | None | Unset):
        assistant_metadata (AssistantUpdateAssistantMetadataType0 | None | Unset):
        text_config (AssistantUpdateTextConfigType0 | None | Unset):
        tool_configurations (None | ToolConfigurationSchema | Unset):
        reasoning (None | ReasoningConfigSchema | Unset):
        vector_store_ids (list[str] | None | Unset):
        rule_ids (list[str] | None | Unset): Rule IDs to attach/replace on assistant
    """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    avatar_id: None | str | Unset = UNSET
    icon_id: None | str | Unset = UNSET
    icon_type: None | str | Unset = UNSET
    icon_data: None | str | Unset = UNSET
    is_default: bool | None | Unset = UNSET
    default_model_key: None | str | Unset = UNSET
    allowed_model_providers: list[str] | None | Unset = UNSET
    instructions: None | str | Unset = UNSET
    instructions_thread_id: None | str | Unset = UNSET
    system_message: list[AssistantUpdateSystemMessageType0Item] | None | Unset = UNSET
    context_strategy: None | str | Unset = UNSET
    context_window: int | None | Unset = UNSET
    max_tool_calls: int | None | Unset = UNSET
    parallel_tool_calls: bool | None | Unset = UNSET
    service_tier: None | str | Unset = UNSET
    store_responses: bool | None | Unset = UNSET
    temperature: float | None | Unset = UNSET
    frequency_penalty: float | None | Unset = UNSET
    presence_penalty: float | None | Unset = UNSET
    logit_bias: AssistantUpdateLogitBiasType0 | None | Unset = UNSET
    top_logprobs: int | None | Unset = UNSET
    top_p: float | None | Unset = UNSET
    output_mode: None | str | Unset = UNSET
    response_format: None | str | Unset = UNSET
    seed: int | None | Unset = UNSET
    stop_sequences: list[str] | None | Unset = UNSET
    max_completion_tokens: int | None | Unset = UNSET
    access_mode: None | str | Unset = UNSET
    access_departments: list[str] | None | Unset = UNSET
    access_users: list[str] | None | Unset = UNSET
    editable_by_users: list[str] | None | Unset = UNSET
    editable_by_roles: list[str] | None | Unset = UNSET
    visible_to_roles: list[str] | None | Unset = UNSET
    api_enabled: bool | None | Unset = UNSET
    public_enabled: bool | None | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    streaming: bool | None | Unset = UNSET
    memory_enabled: bool | None | Unset = UNSET
    moderation_enabled: bool | None | Unset = UNSET
    safety_level: None | str | Unset = UNSET
    truncation: bool | None | Unset = UNSET
    preset_prompts: list[str] | None | Unset = UNSET
    assistant_metadata: AssistantUpdateAssistantMetadataType0 | None | Unset = UNSET
    text_config: AssistantUpdateTextConfigType0 | None | Unset = UNSET
    tool_configurations: None | ToolConfigurationSchema | Unset = UNSET
    reasoning: None | ReasoningConfigSchema | Unset = UNSET
    vector_store_ids: list[str] | None | Unset = UNSET
    rule_ids: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.assistant_update_assistant_metadata_type_0 import (
            AssistantUpdateAssistantMetadataType0,
        )
        from ..models.assistant_update_logit_bias_type_0 import (
            AssistantUpdateLogitBiasType0,
        )
        from ..models.assistant_update_text_config_type_0 import (
            AssistantUpdateTextConfigType0,
        )
        from ..models.reasoning_config_schema import ReasoningConfigSchema
        from ..models.tool_configuration_schema import ToolConfigurationSchema

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        avatar_id: None | str | Unset
        if isinstance(self.avatar_id, Unset):
            avatar_id = UNSET
        else:
            avatar_id = self.avatar_id

        icon_id: None | str | Unset
        if isinstance(self.icon_id, Unset):
            icon_id = UNSET
        else:
            icon_id = self.icon_id

        icon_type: None | str | Unset
        if isinstance(self.icon_type, Unset):
            icon_type = UNSET
        else:
            icon_type = self.icon_type

        icon_data: None | str | Unset
        if isinstance(self.icon_data, Unset):
            icon_data = UNSET
        else:
            icon_data = self.icon_data

        is_default: bool | None | Unset
        if isinstance(self.is_default, Unset):
            is_default = UNSET
        else:
            is_default = self.is_default

        default_model_key: None | str | Unset
        if isinstance(self.default_model_key, Unset):
            default_model_key = UNSET
        else:
            default_model_key = self.default_model_key

        allowed_model_providers: list[str] | None | Unset
        if isinstance(self.allowed_model_providers, Unset):
            allowed_model_providers = UNSET
        elif isinstance(self.allowed_model_providers, list):
            allowed_model_providers = self.allowed_model_providers

        else:
            allowed_model_providers = self.allowed_model_providers

        instructions: None | str | Unset
        if isinstance(self.instructions, Unset):
            instructions = UNSET
        else:
            instructions = self.instructions

        instructions_thread_id: None | str | Unset
        if isinstance(self.instructions_thread_id, Unset):
            instructions_thread_id = UNSET
        else:
            instructions_thread_id = self.instructions_thread_id

        system_message: list[dict[str, Any]] | None | Unset
        if isinstance(self.system_message, Unset):
            system_message = UNSET
        elif isinstance(self.system_message, list):
            system_message = []
            for system_message_type_0_item_data in self.system_message:
                system_message_type_0_item = system_message_type_0_item_data.to_dict()
                system_message.append(system_message_type_0_item)

        else:
            system_message = self.system_message

        context_strategy: None | str | Unset
        if isinstance(self.context_strategy, Unset):
            context_strategy = UNSET
        else:
            context_strategy = self.context_strategy

        context_window: int | None | Unset
        if isinstance(self.context_window, Unset):
            context_window = UNSET
        else:
            context_window = self.context_window

        max_tool_calls: int | None | Unset
        if isinstance(self.max_tool_calls, Unset):
            max_tool_calls = UNSET
        else:
            max_tool_calls = self.max_tool_calls

        parallel_tool_calls: bool | None | Unset
        if isinstance(self.parallel_tool_calls, Unset):
            parallel_tool_calls = UNSET
        else:
            parallel_tool_calls = self.parallel_tool_calls

        service_tier: None | str | Unset
        if isinstance(self.service_tier, Unset):
            service_tier = UNSET
        else:
            service_tier = self.service_tier

        store_responses: bool | None | Unset
        if isinstance(self.store_responses, Unset):
            store_responses = UNSET
        else:
            store_responses = self.store_responses

        temperature: float | None | Unset
        if isinstance(self.temperature, Unset):
            temperature = UNSET
        else:
            temperature = self.temperature

        frequency_penalty: float | None | Unset
        if isinstance(self.frequency_penalty, Unset):
            frequency_penalty = UNSET
        else:
            frequency_penalty = self.frequency_penalty

        presence_penalty: float | None | Unset
        if isinstance(self.presence_penalty, Unset):
            presence_penalty = UNSET
        else:
            presence_penalty = self.presence_penalty

        logit_bias: dict[str, Any] | None | Unset
        if isinstance(self.logit_bias, Unset):
            logit_bias = UNSET
        elif isinstance(self.logit_bias, AssistantUpdateLogitBiasType0):
            logit_bias = self.logit_bias.to_dict()
        else:
            logit_bias = self.logit_bias

        top_logprobs: int | None | Unset
        if isinstance(self.top_logprobs, Unset):
            top_logprobs = UNSET
        else:
            top_logprobs = self.top_logprobs

        top_p: float | None | Unset
        if isinstance(self.top_p, Unset):
            top_p = UNSET
        else:
            top_p = self.top_p

        output_mode: None | str | Unset
        if isinstance(self.output_mode, Unset):
            output_mode = UNSET
        else:
            output_mode = self.output_mode

        response_format: None | str | Unset
        if isinstance(self.response_format, Unset):
            response_format = UNSET
        else:
            response_format = self.response_format

        seed: int | None | Unset
        if isinstance(self.seed, Unset):
            seed = UNSET
        else:
            seed = self.seed

        stop_sequences: list[str] | None | Unset
        if isinstance(self.stop_sequences, Unset):
            stop_sequences = UNSET
        elif isinstance(self.stop_sequences, list):
            stop_sequences = self.stop_sequences

        else:
            stop_sequences = self.stop_sequences

        max_completion_tokens: int | None | Unset
        if isinstance(self.max_completion_tokens, Unset):
            max_completion_tokens = UNSET
        else:
            max_completion_tokens = self.max_completion_tokens

        access_mode: None | str | Unset
        if isinstance(self.access_mode, Unset):
            access_mode = UNSET
        else:
            access_mode = self.access_mode

        access_departments: list[str] | None | Unset
        if isinstance(self.access_departments, Unset):
            access_departments = UNSET
        elif isinstance(self.access_departments, list):
            access_departments = self.access_departments

        else:
            access_departments = self.access_departments

        access_users: list[str] | None | Unset
        if isinstance(self.access_users, Unset):
            access_users = UNSET
        elif isinstance(self.access_users, list):
            access_users = self.access_users

        else:
            access_users = self.access_users

        editable_by_users: list[str] | None | Unset
        if isinstance(self.editable_by_users, Unset):
            editable_by_users = UNSET
        elif isinstance(self.editable_by_users, list):
            editable_by_users = self.editable_by_users

        else:
            editable_by_users = self.editable_by_users

        editable_by_roles: list[str] | None | Unset
        if isinstance(self.editable_by_roles, Unset):
            editable_by_roles = UNSET
        elif isinstance(self.editable_by_roles, list):
            editable_by_roles = self.editable_by_roles

        else:
            editable_by_roles = self.editable_by_roles

        visible_to_roles: list[str] | None | Unset
        if isinstance(self.visible_to_roles, Unset):
            visible_to_roles = UNSET
        elif isinstance(self.visible_to_roles, list):
            visible_to_roles = self.visible_to_roles

        else:
            visible_to_roles = self.visible_to_roles

        api_enabled: bool | None | Unset
        if isinstance(self.api_enabled, Unset):
            api_enabled = UNSET
        else:
            api_enabled = self.api_enabled

        public_enabled: bool | None | Unset
        if isinstance(self.public_enabled, Unset):
            public_enabled = UNSET
        else:
            public_enabled = self.public_enabled

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        streaming: bool | None | Unset
        if isinstance(self.streaming, Unset):
            streaming = UNSET
        else:
            streaming = self.streaming

        memory_enabled: bool | None | Unset
        if isinstance(self.memory_enabled, Unset):
            memory_enabled = UNSET
        else:
            memory_enabled = self.memory_enabled

        moderation_enabled: bool | None | Unset
        if isinstance(self.moderation_enabled, Unset):
            moderation_enabled = UNSET
        else:
            moderation_enabled = self.moderation_enabled

        safety_level: None | str | Unset
        if isinstance(self.safety_level, Unset):
            safety_level = UNSET
        else:
            safety_level = self.safety_level

        truncation: bool | None | Unset
        if isinstance(self.truncation, Unset):
            truncation = UNSET
        else:
            truncation = self.truncation

        preset_prompts: list[str] | None | Unset
        if isinstance(self.preset_prompts, Unset):
            preset_prompts = UNSET
        elif isinstance(self.preset_prompts, list):
            preset_prompts = self.preset_prompts

        else:
            preset_prompts = self.preset_prompts

        assistant_metadata: dict[str, Any] | None | Unset
        if isinstance(self.assistant_metadata, Unset):
            assistant_metadata = UNSET
        elif isinstance(self.assistant_metadata, AssistantUpdateAssistantMetadataType0):
            assistant_metadata = self.assistant_metadata.to_dict()
        else:
            assistant_metadata = self.assistant_metadata

        text_config: dict[str, Any] | None | Unset
        if isinstance(self.text_config, Unset):
            text_config = UNSET
        elif isinstance(self.text_config, AssistantUpdateTextConfigType0):
            text_config = self.text_config.to_dict()
        else:
            text_config = self.text_config

        tool_configurations: dict[str, Any] | None | Unset
        if isinstance(self.tool_configurations, Unset):
            tool_configurations = UNSET
        elif isinstance(self.tool_configurations, ToolConfigurationSchema):
            tool_configurations = self.tool_configurations.to_dict()
        else:
            tool_configurations = self.tool_configurations

        reasoning: dict[str, Any] | None | Unset
        if isinstance(self.reasoning, Unset):
            reasoning = UNSET
        elif isinstance(self.reasoning, ReasoningConfigSchema):
            reasoning = self.reasoning.to_dict()
        else:
            reasoning = self.reasoning

        vector_store_ids: list[str] | None | Unset
        if isinstance(self.vector_store_ids, Unset):
            vector_store_ids = UNSET
        elif isinstance(self.vector_store_ids, list):
            vector_store_ids = self.vector_store_ids

        else:
            vector_store_ids = self.vector_store_ids

        rule_ids: list[str] | None | Unset
        if isinstance(self.rule_ids, Unset):
            rule_ids = UNSET
        elif isinstance(self.rule_ids, list):
            rule_ids = self.rule_ids

        else:
            rule_ids = self.rule_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if avatar_id is not UNSET:
            field_dict["avatar_id"] = avatar_id
        if icon_id is not UNSET:
            field_dict["icon_id"] = icon_id
        if icon_type is not UNSET:
            field_dict["icon_type"] = icon_type
        if icon_data is not UNSET:
            field_dict["icon_data"] = icon_data
        if is_default is not UNSET:
            field_dict["is_default"] = is_default
        if default_model_key is not UNSET:
            field_dict["default_model_key"] = default_model_key
        if allowed_model_providers is not UNSET:
            field_dict["allowed_model_providers"] = allowed_model_providers
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if instructions_thread_id is not UNSET:
            field_dict["instructions_thread_id"] = instructions_thread_id
        if system_message is not UNSET:
            field_dict["system_message"] = system_message
        if context_strategy is not UNSET:
            field_dict["context_strategy"] = context_strategy
        if context_window is not UNSET:
            field_dict["context_window"] = context_window
        if max_tool_calls is not UNSET:
            field_dict["max_tool_calls"] = max_tool_calls
        if parallel_tool_calls is not UNSET:
            field_dict["parallel_tool_calls"] = parallel_tool_calls
        if service_tier is not UNSET:
            field_dict["service_tier"] = service_tier
        if store_responses is not UNSET:
            field_dict["store_responses"] = store_responses
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if frequency_penalty is not UNSET:
            field_dict["frequency_penalty"] = frequency_penalty
        if presence_penalty is not UNSET:
            field_dict["presence_penalty"] = presence_penalty
        if logit_bias is not UNSET:
            field_dict["logit_bias"] = logit_bias
        if top_logprobs is not UNSET:
            field_dict["top_logprobs"] = top_logprobs
        if top_p is not UNSET:
            field_dict["top_p"] = top_p
        if output_mode is not UNSET:
            field_dict["output_mode"] = output_mode
        if response_format is not UNSET:
            field_dict["response_format"] = response_format
        if seed is not UNSET:
            field_dict["seed"] = seed
        if stop_sequences is not UNSET:
            field_dict["stop_sequences"] = stop_sequences
        if max_completion_tokens is not UNSET:
            field_dict["max_completion_tokens"] = max_completion_tokens
        if access_mode is not UNSET:
            field_dict["access_mode"] = access_mode
        if access_departments is not UNSET:
            field_dict["access_departments"] = access_departments
        if access_users is not UNSET:
            field_dict["access_users"] = access_users
        if editable_by_users is not UNSET:
            field_dict["editable_by_users"] = editable_by_users
        if editable_by_roles is not UNSET:
            field_dict["editable_by_roles"] = editable_by_roles
        if visible_to_roles is not UNSET:
            field_dict["visible_to_roles"] = visible_to_roles
        if api_enabled is not UNSET:
            field_dict["api_enabled"] = api_enabled
        if public_enabled is not UNSET:
            field_dict["public_enabled"] = public_enabled
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if streaming is not UNSET:
            field_dict["streaming"] = streaming
        if memory_enabled is not UNSET:
            field_dict["memory_enabled"] = memory_enabled
        if moderation_enabled is not UNSET:
            field_dict["moderation_enabled"] = moderation_enabled
        if safety_level is not UNSET:
            field_dict["safety_level"] = safety_level
        if truncation is not UNSET:
            field_dict["truncation"] = truncation
        if preset_prompts is not UNSET:
            field_dict["preset_prompts"] = preset_prompts
        if assistant_metadata is not UNSET:
            field_dict["assistant_metadata"] = assistant_metadata
        if text_config is not UNSET:
            field_dict["text_config"] = text_config
        if tool_configurations is not UNSET:
            field_dict["tool_configurations"] = tool_configurations
        if reasoning is not UNSET:
            field_dict["reasoning"] = reasoning
        if vector_store_ids is not UNSET:
            field_dict["vector_store_ids"] = vector_store_ids
        if rule_ids is not UNSET:
            field_dict["rule_ids"] = rule_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.assistant_update_assistant_metadata_type_0 import (
            AssistantUpdateAssistantMetadataType0,
        )
        from ..models.assistant_update_logit_bias_type_0 import (
            AssistantUpdateLogitBiasType0,
        )
        from ..models.assistant_update_system_message_type_0_item import (
            AssistantUpdateSystemMessageType0Item,
        )
        from ..models.assistant_update_text_config_type_0 import (
            AssistantUpdateTextConfigType0,
        )
        from ..models.reasoning_config_schema import ReasoningConfigSchema
        from ..models.tool_configuration_schema import ToolConfigurationSchema

        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_avatar_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        avatar_id = _parse_avatar_id(d.pop("avatar_id", UNSET))

        def _parse_icon_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_id = _parse_icon_id(d.pop("icon_id", UNSET))

        def _parse_icon_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_type = _parse_icon_type(d.pop("icon_type", UNSET))

        def _parse_icon_data(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_data = _parse_icon_data(d.pop("icon_data", UNSET))

        def _parse_is_default(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_default = _parse_is_default(d.pop("is_default", UNSET))

        def _parse_default_model_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        default_model_key = _parse_default_model_key(d.pop("default_model_key", UNSET))

        def _parse_allowed_model_providers(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_model_providers_type_0 = cast(list[str], data)

                return allowed_model_providers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        allowed_model_providers = _parse_allowed_model_providers(
            d.pop("allowed_model_providers", UNSET)
        )

        def _parse_instructions(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        instructions = _parse_instructions(d.pop("instructions", UNSET))

        def _parse_instructions_thread_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        instructions_thread_id = _parse_instructions_thread_id(
            d.pop("instructions_thread_id", UNSET)
        )

        def _parse_system_message(
            data: object,
        ) -> list[AssistantUpdateSystemMessageType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                system_message_type_0 = []
                _system_message_type_0 = data
                for system_message_type_0_item_data in _system_message_type_0:
                    system_message_type_0_item = (
                        AssistantUpdateSystemMessageType0Item.from_dict(
                            system_message_type_0_item_data
                        )
                    )

                    system_message_type_0.append(system_message_type_0_item)

                return system_message_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                list[AssistantUpdateSystemMessageType0Item] | None | Unset, data
            )

        system_message = _parse_system_message(d.pop("system_message", UNSET))

        def _parse_context_strategy(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        context_strategy = _parse_context_strategy(d.pop("context_strategy", UNSET))

        def _parse_context_window(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        context_window = _parse_context_window(d.pop("context_window", UNSET))

        def _parse_max_tool_calls(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_tool_calls = _parse_max_tool_calls(d.pop("max_tool_calls", UNSET))

        def _parse_parallel_tool_calls(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        parallel_tool_calls = _parse_parallel_tool_calls(
            d.pop("parallel_tool_calls", UNSET)
        )

        def _parse_service_tier(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        service_tier = _parse_service_tier(d.pop("service_tier", UNSET))

        def _parse_store_responses(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        store_responses = _parse_store_responses(d.pop("store_responses", UNSET))

        def _parse_temperature(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        temperature = _parse_temperature(d.pop("temperature", UNSET))

        def _parse_frequency_penalty(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        frequency_penalty = _parse_frequency_penalty(d.pop("frequency_penalty", UNSET))

        def _parse_presence_penalty(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        presence_penalty = _parse_presence_penalty(d.pop("presence_penalty", UNSET))

        def _parse_logit_bias(
            data: object,
        ) -> AssistantUpdateLogitBiasType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                logit_bias_type_0 = AssistantUpdateLogitBiasType0.from_dict(data)

                return logit_bias_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AssistantUpdateLogitBiasType0 | None | Unset, data)

        logit_bias = _parse_logit_bias(d.pop("logit_bias", UNSET))

        def _parse_top_logprobs(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        top_logprobs = _parse_top_logprobs(d.pop("top_logprobs", UNSET))

        def _parse_top_p(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        top_p = _parse_top_p(d.pop("top_p", UNSET))

        def _parse_output_mode(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        output_mode = _parse_output_mode(d.pop("output_mode", UNSET))

        def _parse_response_format(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        response_format = _parse_response_format(d.pop("response_format", UNSET))

        def _parse_seed(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        seed = _parse_seed(d.pop("seed", UNSET))

        def _parse_stop_sequences(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                stop_sequences_type_0 = cast(list[str], data)

                return stop_sequences_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        stop_sequences = _parse_stop_sequences(d.pop("stop_sequences", UNSET))

        def _parse_max_completion_tokens(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_completion_tokens = _parse_max_completion_tokens(
            d.pop("max_completion_tokens", UNSET)
        )

        def _parse_access_mode(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        access_mode = _parse_access_mode(d.pop("access_mode", UNSET))

        def _parse_access_departments(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                access_departments_type_0 = cast(list[str], data)

                return access_departments_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        access_departments = _parse_access_departments(
            d.pop("access_departments", UNSET)
        )

        def _parse_access_users(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                access_users_type_0 = cast(list[str], data)

                return access_users_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        access_users = _parse_access_users(d.pop("access_users", UNSET))

        def _parse_editable_by_users(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                editable_by_users_type_0 = cast(list[str], data)

                return editable_by_users_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        editable_by_users = _parse_editable_by_users(d.pop("editable_by_users", UNSET))

        def _parse_editable_by_roles(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                editable_by_roles_type_0 = cast(list[str], data)

                return editable_by_roles_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        editable_by_roles = _parse_editable_by_roles(d.pop("editable_by_roles", UNSET))

        def _parse_visible_to_roles(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                visible_to_roles_type_0 = cast(list[str], data)

                return visible_to_roles_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        visible_to_roles = _parse_visible_to_roles(d.pop("visible_to_roles", UNSET))

        def _parse_api_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        api_enabled = _parse_api_enabled(d.pop("api_enabled", UNSET))

        def _parse_public_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        public_enabled = _parse_public_enabled(d.pop("public_enabled", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_streaming(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        streaming = _parse_streaming(d.pop("streaming", UNSET))

        def _parse_memory_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        memory_enabled = _parse_memory_enabled(d.pop("memory_enabled", UNSET))

        def _parse_moderation_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        moderation_enabled = _parse_moderation_enabled(
            d.pop("moderation_enabled", UNSET)
        )

        def _parse_safety_level(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        safety_level = _parse_safety_level(d.pop("safety_level", UNSET))

        def _parse_truncation(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        truncation = _parse_truncation(d.pop("truncation", UNSET))

        def _parse_preset_prompts(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                preset_prompts_type_0 = cast(list[str], data)

                return preset_prompts_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        preset_prompts = _parse_preset_prompts(d.pop("preset_prompts", UNSET))

        def _parse_assistant_metadata(
            data: object,
        ) -> AssistantUpdateAssistantMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                assistant_metadata_type_0 = (
                    AssistantUpdateAssistantMetadataType0.from_dict(data)
                )

                return assistant_metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AssistantUpdateAssistantMetadataType0 | None | Unset, data)

        assistant_metadata = _parse_assistant_metadata(
            d.pop("assistant_metadata", UNSET)
        )

        def _parse_text_config(
            data: object,
        ) -> AssistantUpdateTextConfigType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                text_config_type_0 = AssistantUpdateTextConfigType0.from_dict(data)

                return text_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AssistantUpdateTextConfigType0 | None | Unset, data)

        text_config = _parse_text_config(d.pop("text_config", UNSET))

        def _parse_tool_configurations(
            data: object,
        ) -> None | ToolConfigurationSchema | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tool_configurations_type_0 = ToolConfigurationSchema.from_dict(data)

                return tool_configurations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ToolConfigurationSchema | Unset, data)

        tool_configurations = _parse_tool_configurations(
            d.pop("tool_configurations", UNSET)
        )

        def _parse_reasoning(data: object) -> None | ReasoningConfigSchema | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                reasoning_type_0 = ReasoningConfigSchema.from_dict(data)

                return reasoning_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReasoningConfigSchema | Unset, data)

        reasoning = _parse_reasoning(d.pop("reasoning", UNSET))

        def _parse_vector_store_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                vector_store_ids_type_0 = cast(list[str], data)

                return vector_store_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        vector_store_ids = _parse_vector_store_ids(d.pop("vector_store_ids", UNSET))

        def _parse_rule_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                rule_ids_type_0 = cast(list[str], data)

                return rule_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        rule_ids = _parse_rule_ids(d.pop("rule_ids", UNSET))

        assistant_update = cls(
            name=name,
            description=description,
            avatar_id=avatar_id,
            icon_id=icon_id,
            icon_type=icon_type,
            icon_data=icon_data,
            is_default=is_default,
            default_model_key=default_model_key,
            allowed_model_providers=allowed_model_providers,
            instructions=instructions,
            instructions_thread_id=instructions_thread_id,
            system_message=system_message,
            context_strategy=context_strategy,
            context_window=context_window,
            max_tool_calls=max_tool_calls,
            parallel_tool_calls=parallel_tool_calls,
            service_tier=service_tier,
            store_responses=store_responses,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            logit_bias=logit_bias,
            top_logprobs=top_logprobs,
            top_p=top_p,
            output_mode=output_mode,
            response_format=response_format,
            seed=seed,
            stop_sequences=stop_sequences,
            max_completion_tokens=max_completion_tokens,
            access_mode=access_mode,
            access_departments=access_departments,
            access_users=access_users,
            editable_by_users=editable_by_users,
            editable_by_roles=editable_by_roles,
            visible_to_roles=visible_to_roles,
            api_enabled=api_enabled,
            public_enabled=public_enabled,
            is_active=is_active,
            streaming=streaming,
            memory_enabled=memory_enabled,
            moderation_enabled=moderation_enabled,
            safety_level=safety_level,
            truncation=truncation,
            preset_prompts=preset_prompts,
            assistant_metadata=assistant_metadata,
            text_config=text_config,
            tool_configurations=tool_configurations,
            reasoning=reasoning,
            vector_store_ids=vector_store_ids,
            rule_ids=rule_ids,
        )

        assistant_update.additional_properties = d
        return assistant_update

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
