from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tool_capabilities_response import ToolCapabilitiesResponse


T = TypeVar("T", bound="SystemToolResponse")


@_attrs_define
class SystemToolResponse:
    """Response schema for system tool entries.

    Attributes:
        id (str): System tool ID with stool_ prefix
        name (str): Human-readable name for the tool
        category (str): Tool category: search, computation, generation, automation, analysis
        tool_key (str): Configuration key used in assistant toolConfigurations
        default_provider (str): Provider selection strategy: 'auto' or specific provider name
        is_preview (bool): Whether this tool is in preview/beta status
        created_at (int): Unix timestamp (seconds) when the tool was created
        updated_at (int): Unix timestamp (seconds) when the tool was last updated
        description (None | str | Unset): Detailed tool description
        capabilities (None | ToolCapabilitiesResponse | Unset): Tool capabilities and features
    """

    id: str
    name: str
    category: str
    tool_key: str
    default_provider: str
    is_preview: bool
    created_at: int
    updated_at: int
    description: None | str | Unset = UNSET
    capabilities: None | ToolCapabilitiesResponse | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.tool_capabilities_response import ToolCapabilitiesResponse

        id = self.id

        name = self.name

        category = self.category

        tool_key = self.tool_key

        default_provider = self.default_provider

        is_preview = self.is_preview

        created_at = self.created_at

        updated_at = self.updated_at

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        capabilities: dict[str, Any] | None | Unset
        if isinstance(self.capabilities, Unset):
            capabilities = UNSET
        elif isinstance(self.capabilities, ToolCapabilitiesResponse):
            capabilities = self.capabilities.to_dict()
        else:
            capabilities = self.capabilities

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "category": category,
                "toolKey": tool_key,
                "defaultProvider": default_provider,
                "isPreview": is_preview,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if capabilities is not UNSET:
            field_dict["capabilities"] = capabilities

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_capabilities_response import ToolCapabilitiesResponse

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        category = d.pop("category")

        tool_key = d.pop("toolKey")

        default_provider = d.pop("defaultProvider")

        is_preview = d.pop("isPreview")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_capabilities(
            data: object,
        ) -> None | ToolCapabilitiesResponse | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                capabilities_type_0 = ToolCapabilitiesResponse.from_dict(data)

                return capabilities_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ToolCapabilitiesResponse | Unset, data)

        capabilities = _parse_capabilities(d.pop("capabilities", UNSET))

        system_tool_response = cls(
            id=id,
            name=name,
            category=category,
            tool_key=tool_key,
            default_provider=default_provider,
            is_preview=is_preview,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            capabilities=capabilities,
        )

        system_tool_response.additional_properties = d
        return system_tool_response

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
