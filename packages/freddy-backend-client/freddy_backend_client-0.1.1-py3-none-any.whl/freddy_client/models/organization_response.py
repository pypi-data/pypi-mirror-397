from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationResponse")


@_attrs_define
class OrganizationResponse:
    """Schema for organization response.

    Attributes:
        id (str):
        name (str):
        type_ (str):
        is_active (bool):
        api_usage_limit (float):
        total_usage_limit (float):
        storage_free_bytes_allowance (int):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        description (None | str | Unset):
        website (None | str | Unset):
        industry (None | str | Unset):
        company_size (None | str | Unset):
        logo_image (None | str | Unset):
        image_url (None | str | Unset):
        owner_id (None | str | Unset):
        pricing_tier_id (None | str | Unset):
        users_added_from_domains (int | None | Unset): Number of users automatically added based on email domains
    """

    id: str
    name: str
    type_: str
    is_active: bool
    api_usage_limit: float
    total_usage_limit: float
    storage_free_bytes_allowance: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: None | str | Unset = UNSET
    website: None | str | Unset = UNSET
    industry: None | str | Unset = UNSET
    company_size: None | str | Unset = UNSET
    logo_image: None | str | Unset = UNSET
    image_url: None | str | Unset = UNSET
    owner_id: None | str | Unset = UNSET
    pricing_tier_id: None | str | Unset = UNSET
    users_added_from_domains: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        type_ = self.type_

        is_active = self.is_active

        api_usage_limit = self.api_usage_limit

        total_usage_limit = self.total_usage_limit

        storage_free_bytes_allowance = self.storage_free_bytes_allowance

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

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

        owner_id: None | str | Unset
        if isinstance(self.owner_id, Unset):
            owner_id = UNSET
        else:
            owner_id = self.owner_id

        pricing_tier_id: None | str | Unset
        if isinstance(self.pricing_tier_id, Unset):
            pricing_tier_id = UNSET
        else:
            pricing_tier_id = self.pricing_tier_id

        users_added_from_domains: int | None | Unset
        if isinstance(self.users_added_from_domains, Unset):
            users_added_from_domains = UNSET
        else:
            users_added_from_domains = self.users_added_from_domains

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "type": type_,
                "is_active": is_active,
                "api_usage_limit": api_usage_limit,
                "total_usage_limit": total_usage_limit,
                "storage_free_bytes_allowance": storage_free_bytes_allowance,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
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
        if owner_id is not UNSET:
            field_dict["owner_id"] = owner_id
        if pricing_tier_id is not UNSET:
            field_dict["pricing_tier_id"] = pricing_tier_id
        if users_added_from_domains is not UNSET:
            field_dict["users_added_from_domains"] = users_added_from_domains

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        type_ = d.pop("type")

        is_active = d.pop("is_active")

        api_usage_limit = d.pop("api_usage_limit")

        total_usage_limit = d.pop("total_usage_limit")

        storage_free_bytes_allowance = d.pop("storage_free_bytes_allowance")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

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

        def _parse_owner_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        owner_id = _parse_owner_id(d.pop("owner_id", UNSET))

        def _parse_pricing_tier_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pricing_tier_id = _parse_pricing_tier_id(d.pop("pricing_tier_id", UNSET))

        def _parse_users_added_from_domains(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        users_added_from_domains = _parse_users_added_from_domains(
            d.pop("users_added_from_domains", UNSET)
        )

        organization_response = cls(
            id=id,
            name=name,
            type_=type_,
            is_active=is_active,
            api_usage_limit=api_usage_limit,
            total_usage_limit=total_usage_limit,
            storage_free_bytes_allowance=storage_free_bytes_allowance,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            website=website,
            industry=industry,
            company_size=company_size,
            logo_image=logo_image,
            image_url=image_url,
            owner_id=owner_id,
            pricing_tier_id=pricing_tier_id,
            users_added_from_domains=users_added_from_domains,
        )

        organization_response.additional_properties = d
        return organization_response

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
