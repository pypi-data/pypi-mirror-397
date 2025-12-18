from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.reasoning_config_effort import ReasoningConfigEffort
from ..models.reasoning_config_summary_type_0 import ReasoningConfigSummaryType0
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReasoningConfig")


@_attrs_define
class ReasoningConfig:
    """Reasoning configuration for models that support extended thinking.

    Unified configuration that works across reasoning-capable models
    (OpenAI O-series, Anthropic Claude extended thinking).

        Attributes:
            effort (ReasoningConfigEffort | Unset): Controls computational effort for reasoning. Higher effort produces more
                thorough analysis but increases response time and token usage. The API automatically maps effort levels to
                provider-specific parameters. Default: ReasoningConfigEffort.MEDIUM.
            summary (None | ReasoningConfigSummaryType0 | Unset): Controls reasoning summary formatting. 'off': raw
                reasoning (no formatting), 'auto': model decides, 'concise': brief overview, 'detailed': comprehensive
                explanation. Note: Claude ignores this field (no summary support). Use 'off' to explicitly disable formatting.
    """

    effort: ReasoningConfigEffort | Unset = ReasoningConfigEffort.MEDIUM
    summary: None | ReasoningConfigSummaryType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        effort: str | Unset = UNSET
        if not isinstance(self.effort, Unset):
            effort = self.effort.value

        summary: None | str | Unset
        if isinstance(self.summary, Unset):
            summary = UNSET
        elif isinstance(self.summary, ReasoningConfigSummaryType0):
            summary = self.summary.value
        else:
            summary = self.summary

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
        effort: ReasoningConfigEffort | Unset
        if isinstance(_effort, Unset):
            effort = UNSET
        else:
            effort = ReasoningConfigEffort(_effort)

        def _parse_summary(data: object) -> None | ReasoningConfigSummaryType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                summary_type_0 = ReasoningConfigSummaryType0(data)

                return summary_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReasoningConfigSummaryType0 | Unset, data)

        summary = _parse_summary(d.pop("summary", UNSET))

        reasoning_config = cls(
            effort=effort,
            summary=summary,
        )

        reasoning_config.additional_properties = d
        return reasoning_config

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
