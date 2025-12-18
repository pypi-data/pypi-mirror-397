from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ModelCompatibilityResponse")


@_attrs_define
class ModelCompatibilityResponse:
    """Model type compatibility configuration.

    Attributes:
        text (bool): Compatible with text-only models
        vision (bool): Compatible with vision-capable models
        voice (bool): Compatible with voice models
        multimodal (bool): Compatible with multimodal models
    """

    text: bool
    vision: bool
    voice: bool
    multimodal: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        vision = self.vision

        voice = self.voice

        multimodal = self.multimodal

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "text": text,
                "vision": vision,
                "voice": voice,
                "multimodal": multimodal,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        text = d.pop("text")

        vision = d.pop("vision")

        voice = d.pop("voice")

        multimodal = d.pop("multimodal")

        model_compatibility_response = cls(
            text=text,
            vision=vision,
            voice=voice,
            multimodal=multimodal,
        )

        model_compatibility_response.additional_properties = d
        return model_compatibility_response

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
