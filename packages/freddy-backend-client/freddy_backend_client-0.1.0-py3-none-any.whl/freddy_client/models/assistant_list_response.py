from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.assistant_response import AssistantResponse
    from ..models.assistant_standard_response import AssistantStandardResponse
    from ..models.assistant_summary_response import AssistantSummaryResponse
    from ..models.filters_applied_schema import FiltersAppliedSchema
    from ..models.pagination_schema import PaginationSchema
    from ..models.user_context_schema import UserContextSchema


T = TypeVar("T", bound="AssistantListResponse")


@_attrs_define
class AssistantListResponse:
    """Response schema for assistant list.

    Attributes:
        assistants (list[AssistantResponse | AssistantStandardResponse | AssistantSummaryResponse]): List of assistants
        total (int): Total number of assistants
        pagination (PaginationSchema): Pagination information schema.
        filters_applied (FiltersAppliedSchema): Applied filters schema.
        user_context (UserContextSchema): User context schema.
        organization_id (None | str | Unset): Organization ID
    """

    assistants: list[
        AssistantResponse | AssistantStandardResponse | AssistantSummaryResponse
    ]
    total: int
    pagination: PaginationSchema
    filters_applied: FiltersAppliedSchema
    user_context: UserContextSchema
    organization_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.assistant_standard_response import AssistantStandardResponse
        from ..models.assistant_summary_response import AssistantSummaryResponse

        assistants = []
        for assistants_item_data in self.assistants:
            assistants_item: dict[str, Any]
            if isinstance(assistants_item_data, AssistantSummaryResponse):
                assistants_item = assistants_item_data.to_dict()
            elif isinstance(assistants_item_data, AssistantStandardResponse):
                assistants_item = assistants_item_data.to_dict()
            else:
                assistants_item = assistants_item_data.to_dict()

            assistants.append(assistants_item)

        total = self.total

        pagination = self.pagination.to_dict()

        filters_applied = self.filters_applied.to_dict()

        user_context = self.user_context.to_dict()

        organization_id: None | str | Unset
        if isinstance(self.organization_id, Unset):
            organization_id = UNSET
        else:
            organization_id = self.organization_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assistants": assistants,
                "total": total,
                "pagination": pagination,
                "filters_applied": filters_applied,
                "user_context": user_context,
            }
        )
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.assistant_response import AssistantResponse
        from ..models.assistant_standard_response import AssistantStandardResponse
        from ..models.assistant_summary_response import AssistantSummaryResponse
        from ..models.filters_applied_schema import FiltersAppliedSchema
        from ..models.pagination_schema import PaginationSchema
        from ..models.user_context_schema import UserContextSchema

        d = dict(src_dict)
        assistants = []
        _assistants = d.pop("assistants")
        for assistants_item_data in _assistants:

            def _parse_assistants_item(
                data: object,
            ) -> (
                AssistantResponse | AssistantStandardResponse | AssistantSummaryResponse
            ):
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    assistants_item_type_0 = AssistantSummaryResponse.from_dict(data)

                    return assistants_item_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    assistants_item_type_1 = AssistantStandardResponse.from_dict(data)

                    return assistants_item_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                assistants_item_type_2 = AssistantResponse.from_dict(data)

                return assistants_item_type_2

            assistants_item = _parse_assistants_item(assistants_item_data)

            assistants.append(assistants_item)

        total = d.pop("total")

        pagination = PaginationSchema.from_dict(d.pop("pagination"))

        filters_applied = FiltersAppliedSchema.from_dict(d.pop("filters_applied"))

        user_context = UserContextSchema.from_dict(d.pop("user_context"))

        def _parse_organization_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        organization_id = _parse_organization_id(d.pop("organization_id", UNSET))

        assistant_list_response = cls(
            assistants=assistants,
            total=total,
            pagination=pagination,
            filters_applied=filters_applied,
            user_context=user_context,
            organization_id=organization_id,
        )

        assistant_list_response.additional_properties = d
        return assistant_list_response

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
