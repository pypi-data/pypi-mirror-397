from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.reasoning_config_schema_effort import ReasoningConfigSchemaEffort
from ..models.reasoning_config_schema_summary import ReasoningConfigSchemaSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReasoningConfigSchema")


@_attrs_define
class ReasoningConfigSchema:
    """Reasoning configuration schema.

    Attributes:
        effort (ReasoningConfigSchemaEffort | Unset): Reasoning effort: off, low, medium, high, maximum Default:
            ReasoningConfigSchemaEffort.MEDIUM.
        summary (ReasoningConfigSchemaSummary | Unset): Summary level: off (no formatting), auto, concise, detailed.
            Note: Claude ignores this field. Default: ReasoningConfigSchemaSummary.AUTO.
    """

    effort: ReasoningConfigSchemaEffort | Unset = ReasoningConfigSchemaEffort.MEDIUM
    summary: ReasoningConfigSchemaSummary | Unset = ReasoningConfigSchemaSummary.AUTO
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        effort: str | Unset = UNSET
        if not isinstance(self.effort, Unset):
            effort = self.effort.value

        summary: str | Unset = UNSET
        if not isinstance(self.summary, Unset):
            summary = self.summary.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if effort is not UNSET:
            field_dict["effort"] = effort
        if summary is not UNSET:
            field_dict["summary"] = summary

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _effort = d.pop("effort", UNSET)
        effort: ReasoningConfigSchemaEffort | Unset
        if isinstance(_effort, Unset):
            effort = UNSET
        else:
            effort = ReasoningConfigSchemaEffort(_effort)

        _summary = d.pop("summary", UNSET)
        summary: ReasoningConfigSchemaSummary | Unset
        if isinstance(_summary, Unset):
            summary = UNSET
        else:
            summary = ReasoningConfigSchemaSummary(_summary)

        reasoning_config_schema = cls(
            effort=effort,
            summary=summary,
        )

        reasoning_config_schema.additional_properties = d
        return reasoning_config_schema

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
