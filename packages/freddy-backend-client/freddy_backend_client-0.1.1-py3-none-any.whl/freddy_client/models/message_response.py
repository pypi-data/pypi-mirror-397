from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.message_response_role import MessageResponseRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_response_attachments_item import (
        MessageResponseAttachmentsItem,
    )
    from ..models.message_response_iterations_type_0_item import (
        MessageResponseIterationsType0Item,
    )
    from ..models.message_response_metadata import MessageResponseMetadata
    from ..models.message_response_response_blocks_type_0_item import (
        MessageResponseResponseBlocksType0Item,
    )
    from ..models.message_response_tool_calls_type_0_item import (
        MessageResponseToolCallsType0Item,
    )


T = TypeVar("T", bound="MessageResponse")


@_attrs_define
class MessageResponse:
    """Single message response schema.

    Fields tool_calls and iterations are conditionally included only for assistant messages.

        Attributes:
            id (str): Message ID with msg_ prefix
            created_at (datetime.datetime): Creation timestamp
            thread_id (str): Thread ID with thread_ prefix
            role (MessageResponseRole): Message role
            content (str): Message text content
            attachments (list[MessageResponseAttachmentsItem] | Unset): File attachments
            metadata (MessageResponseMetadata | Unset): Custom metadata
            tool_calls (list[MessageResponseToolCallsType0Item] | None | Unset): Tool invocations (assistant only)
            iterations (list[MessageResponseIterationsType0Item] | None | Unset): Reasoning steps (assistant only)
            response_blocks (list[MessageResponseResponseBlocksType0Item] | None | Unset): Structured response blocks (when
                output_mode=blocks/structured)
    """

    id: str
    created_at: datetime.datetime
    thread_id: str
    role: MessageResponseRole
    content: str
    attachments: list[MessageResponseAttachmentsItem] | Unset = UNSET
    metadata: MessageResponseMetadata | Unset = UNSET
    tool_calls: list[MessageResponseToolCallsType0Item] | None | Unset = UNSET
    iterations: list[MessageResponseIterationsType0Item] | None | Unset = UNSET
    response_blocks: list[MessageResponseResponseBlocksType0Item] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        created_at = self.created_at.isoformat()

        thread_id = self.thread_id

        role = self.role.value

        content = self.content

        attachments: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        tool_calls: list[dict[str, Any]] | None | Unset
        if isinstance(self.tool_calls, Unset):
            tool_calls = UNSET
        elif isinstance(self.tool_calls, list):
            tool_calls = []
            for tool_calls_type_0_item_data in self.tool_calls:
                tool_calls_type_0_item = tool_calls_type_0_item_data.to_dict()
                tool_calls.append(tool_calls_type_0_item)

        else:
            tool_calls = self.tool_calls

        iterations: list[dict[str, Any]] | None | Unset
        if isinstance(self.iterations, Unset):
            iterations = UNSET
        elif isinstance(self.iterations, list):
            iterations = []
            for iterations_type_0_item_data in self.iterations:
                iterations_type_0_item = iterations_type_0_item_data.to_dict()
                iterations.append(iterations_type_0_item)

        else:
            iterations = self.iterations

        response_blocks: list[dict[str, Any]] | None | Unset
        if isinstance(self.response_blocks, Unset):
            response_blocks = UNSET
        elif isinstance(self.response_blocks, list):
            response_blocks = []
            for response_blocks_type_0_item_data in self.response_blocks:
                response_blocks_type_0_item = response_blocks_type_0_item_data.to_dict()
                response_blocks.append(response_blocks_type_0_item)

        else:
            response_blocks = self.response_blocks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "created_at": created_at,
                "thread_id": thread_id,
                "role": role,
                "content": content,
            }
        )
        if attachments is not UNSET:
            field_dict["attachments"] = attachments
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if tool_calls is not UNSET:
            field_dict["tool_calls"] = tool_calls
        if iterations is not UNSET:
            field_dict["iterations"] = iterations
        if response_blocks is not UNSET:
            field_dict["response_blocks"] = response_blocks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message_response_attachments_item import (
            MessageResponseAttachmentsItem,
        )
        from ..models.message_response_iterations_type_0_item import (
            MessageResponseIterationsType0Item,
        )
        from ..models.message_response_metadata import MessageResponseMetadata
        from ..models.message_response_response_blocks_type_0_item import (
            MessageResponseResponseBlocksType0Item,
        )
        from ..models.message_response_tool_calls_type_0_item import (
            MessageResponseToolCallsType0Item,
        )

        d = dict(src_dict)
        id = d.pop("id")

        created_at = isoparse(d.pop("created_at"))

        thread_id = d.pop("thread_id")

        role = MessageResponseRole(d.pop("role"))

        content = d.pop("content")

        _attachments = d.pop("attachments", UNSET)
        attachments: list[MessageResponseAttachmentsItem] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = MessageResponseAttachmentsItem.from_dict(
                    attachments_item_data
                )

                attachments.append(attachments_item)

        _metadata = d.pop("metadata", UNSET)
        metadata: MessageResponseMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = MessageResponseMetadata.from_dict(_metadata)

        def _parse_tool_calls(
            data: object,
        ) -> list[MessageResponseToolCallsType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tool_calls_type_0 = []
                _tool_calls_type_0 = data
                for tool_calls_type_0_item_data in _tool_calls_type_0:
                    tool_calls_type_0_item = (
                        MessageResponseToolCallsType0Item.from_dict(
                            tool_calls_type_0_item_data
                        )
                    )

                    tool_calls_type_0.append(tool_calls_type_0_item)

                return tool_calls_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[MessageResponseToolCallsType0Item] | None | Unset, data)

        tool_calls = _parse_tool_calls(d.pop("tool_calls", UNSET))

        def _parse_iterations(
            data: object,
        ) -> list[MessageResponseIterationsType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                iterations_type_0 = []
                _iterations_type_0 = data
                for iterations_type_0_item_data in _iterations_type_0:
                    iterations_type_0_item = (
                        MessageResponseIterationsType0Item.from_dict(
                            iterations_type_0_item_data
                        )
                    )

                    iterations_type_0.append(iterations_type_0_item)

                return iterations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[MessageResponseIterationsType0Item] | None | Unset, data)

        iterations = _parse_iterations(d.pop("iterations", UNSET))

        def _parse_response_blocks(
            data: object,
        ) -> list[MessageResponseResponseBlocksType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                response_blocks_type_0 = []
                _response_blocks_type_0 = data
                for response_blocks_type_0_item_data in _response_blocks_type_0:
                    response_blocks_type_0_item = (
                        MessageResponseResponseBlocksType0Item.from_dict(
                            response_blocks_type_0_item_data
                        )
                    )

                    response_blocks_type_0.append(response_blocks_type_0_item)

                return response_blocks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                list[MessageResponseResponseBlocksType0Item] | None | Unset, data
            )

        response_blocks = _parse_response_blocks(d.pop("response_blocks", UNSET))

        message_response = cls(
            id=id,
            created_at=created_at,
            thread_id=thread_id,
            role=role,
            content=content,
            attachments=attachments,
            metadata=metadata,
            tool_calls=tool_calls,
            iterations=iterations,
            response_blocks=response_blocks,
        )

        message_response.additional_properties = d
        return message_response

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
