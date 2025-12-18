from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SystemToolSchema")


@_attrs_define
class SystemToolSchema:
    """System tool configuration schema.

    Attributes:
        mode (str | Unset): Tool mode: on, off, auto Default: 'auto'.
        sources (bool | None | Unset): Include sources
        outputs (bool | None | Unset): Include outputs
        results (bool | None | Unset): Include results
        image_url (bool | None | Unset): Include image URLs
        provider (None | str | Unset): Provider
    """

    mode: str | Unset = "auto"
    sources: bool | None | Unset = UNSET
    outputs: bool | None | Unset = UNSET
    results: bool | None | Unset = UNSET
    image_url: bool | None | Unset = UNSET
    provider: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode

        sources: bool | None | Unset
        if isinstance(self.sources, Unset):
            sources = UNSET
        else:
            sources = self.sources

        outputs: bool | None | Unset
        if isinstance(self.outputs, Unset):
            outputs = UNSET
        else:
            outputs = self.outputs

        results: bool | None | Unset
        if isinstance(self.results, Unset):
            results = UNSET
        else:
            results = self.results

        image_url: bool | None | Unset
        if isinstance(self.image_url, Unset):
            image_url = UNSET
        else:
            image_url = self.image_url

        provider: None | str | Unset
        if isinstance(self.provider, Unset):
            provider = UNSET
        else:
            provider = self.provider

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mode is not UNSET:
            field_dict["mode"] = mode
        if sources is not UNSET:
            field_dict["sources"] = sources
        if outputs is not UNSET:
            field_dict["outputs"] = outputs
        if results is not UNSET:
            field_dict["results"] = results
        if image_url is not UNSET:
            field_dict["image_url"] = image_url
        if provider is not UNSET:
            field_dict["provider"] = provider

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        mode = d.pop("mode", UNSET)

        def _parse_sources(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        sources = _parse_sources(d.pop("sources", UNSET))

        def _parse_outputs(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        outputs = _parse_outputs(d.pop("outputs", UNSET))

        def _parse_results(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        results = _parse_results(d.pop("results", UNSET))

        def _parse_image_url(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        image_url = _parse_image_url(d.pop("image_url", UNSET))

        def _parse_provider(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider = _parse_provider(d.pop("provider", UNSET))

        system_tool_schema = cls(
            mode=mode,
            sources=sources,
            outputs=outputs,
            results=results,
            image_url=image_url,
            provider=provider,
        )

        system_tool_schema.additional_properties = d
        return system_tool_schema

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
