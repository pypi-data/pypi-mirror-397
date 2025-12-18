from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationUpdate")


@_attrs_define
class OrganizationUpdate:
    """Schema for updating an organization.

    Attributes:
        name (None | str | Unset):
        description (None | str | Unset):
        website (None | str | Unset):
        industry (None | str | Unset):
        company_size (None | str | Unset):
        logo_image (None | str | Unset):
        image_url (None | str | Unset):
        is_active (bool | None | Unset):
        api_usage_limit (float | None | Unset): API spending limit in CHF
        api_key_usage_limit (float | None | Unset): Monthly spending limit for all API keys combined (CHF)
    """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    website: None | str | Unset = UNSET
    industry: None | str | Unset = UNSET
    company_size: None | str | Unset = UNSET
    logo_image: None | str | Unset = UNSET
    image_url: None | str | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    api_usage_limit: float | None | Unset = UNSET
    api_key_usage_limit: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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

        website: None | str | Unset
        if isinstance(self.website, Unset):
            website = UNSET
        else:
            website = self.website

        industry: None | str | Unset
        if isinstance(self.industry, Unset):
            industry = UNSET
        else:
            industry = self.industry

        company_size: None | str | Unset
        if isinstance(self.company_size, Unset):
            company_size = UNSET
        else:
            company_size = self.company_size

        logo_image: None | str | Unset
        if isinstance(self.logo_image, Unset):
            logo_image = UNSET
        else:
            logo_image = self.logo_image

        image_url: None | str | Unset
        if isinstance(self.image_url, Unset):
            image_url = UNSET
        else:
            image_url = self.image_url

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        api_usage_limit: float | None | Unset
        if isinstance(self.api_usage_limit, Unset):
            api_usage_limit = UNSET
        else:
            api_usage_limit = self.api_usage_limit

        api_key_usage_limit: float | None | Unset
        if isinstance(self.api_key_usage_limit, Unset):
            api_key_usage_limit = UNSET
        else:
            api_key_usage_limit = self.api_key_usage_limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if website is not UNSET:
            field_dict["website"] = website
        if industry is not UNSET:
            field_dict["industry"] = industry
        if company_size is not UNSET:
            field_dict["company_size"] = company_size
        if logo_image is not UNSET:
            field_dict["logo_image"] = logo_image
        if image_url is not UNSET:
            field_dict["image_url"] = image_url
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if api_usage_limit is not UNSET:
            field_dict["api_usage_limit"] = api_usage_limit
        if api_key_usage_limit is not UNSET:
            field_dict["api_key_usage_limit"] = api_key_usage_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        def _parse_website(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        website = _parse_website(d.pop("website", UNSET))

        def _parse_industry(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        industry = _parse_industry(d.pop("industry", UNSET))

        def _parse_company_size(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        company_size = _parse_company_size(d.pop("company_size", UNSET))

        def _parse_logo_image(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        logo_image = _parse_logo_image(d.pop("logo_image", UNSET))

        def _parse_image_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        image_url = _parse_image_url(d.pop("image_url", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_api_usage_limit(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        api_usage_limit = _parse_api_usage_limit(d.pop("api_usage_limit", UNSET))

        def _parse_api_key_usage_limit(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        api_key_usage_limit = _parse_api_key_usage_limit(
            d.pop("api_key_usage_limit", UNSET)
        )

        organization_update = cls(
            name=name,
            description=description,
            website=website,
            industry=industry,
            company_size=company_size,
            logo_image=logo_image,
            image_url=image_url,
            is_active=is_active,
            api_usage_limit=api_usage_limit,
            api_key_usage_limit=api_key_usage_limit,
        )

        organization_update.additional_properties = d
        return organization_update

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
