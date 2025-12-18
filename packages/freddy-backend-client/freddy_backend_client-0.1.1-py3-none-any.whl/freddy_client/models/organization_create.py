from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationCreate")


@_attrs_define
class OrganizationCreate:
    """Schema for creating a new organization.

    Attributes:
        name (str): Organization name
        type_ (str): Organization type (Work, Personal, School)
        description (None | str | Unset): Organization description
        website (None | str | Unset): Website URL
        industry (None | str | Unset): Industry
        company_size (None | str | Unset): Company size range
        logo_image (None | str | Unset): Base64 encoded logo
        use_system_provider_keys (bool | Unset): Whether to use system-wide AI provider keys Default: True.
        domains (list[str] | None | Unset): Email domains for automatic member access (e.g., ['company.com'])
    """

    name: str
    type_: str
    description: None | str | Unset = UNSET
    website: None | str | Unset = UNSET
    industry: None | str | Unset = UNSET
    company_size: None | str | Unset = UNSET
    logo_image: None | str | Unset = UNSET
    use_system_provider_keys: bool | Unset = True
    domains: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

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

        use_system_provider_keys = self.use_system_provider_keys

        domains: list[str] | None | Unset
        if isinstance(self.domains, Unset):
            domains = UNSET
        elif isinstance(self.domains, list):
            domains = self.domains

        else:
            domains = self.domains

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
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
        if use_system_provider_keys is not UNSET:
            field_dict["use_system_provider_keys"] = use_system_provider_keys
        if domains is not UNSET:
            field_dict["domains"] = domains

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        type_ = d.pop("type")

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

        use_system_provider_keys = d.pop("use_system_provider_keys", UNSET)

        def _parse_domains(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                domains_type_0 = cast(list[str], data)

                return domains_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        domains = _parse_domains(d.pop("domains", UNSET))

        organization_create = cls(
            name=name,
            type_=type_,
            description=description,
            website=website,
            industry=industry,
            company_size=company_size,
            logo_image=logo_image,
            use_system_provider_keys=use_system_provider_keys,
            domains=domains,
        )

        organization_create.additional_properties = d
        return organization_create

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
