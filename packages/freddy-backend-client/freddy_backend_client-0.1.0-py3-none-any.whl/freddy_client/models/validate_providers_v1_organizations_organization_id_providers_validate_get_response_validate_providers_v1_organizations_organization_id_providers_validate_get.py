from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.provider_validation_response import ProviderValidationResponse


T = TypeVar(
    "T",
    bound="ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet",
)


@_attrs_define
class ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet:
    """ """

    additional_properties: dict[str, ProviderValidationResponse] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provider_validation_response import ProviderValidationResponse

        d = dict(src_dict)
        validate_providers_v1_organizations_organization_id_providers_validate_get_response_validate_providers_v1_organizations_organization_id_providers_validate_get = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = ProviderValidationResponse.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        validate_providers_v1_organizations_organization_id_providers_validate_get_response_validate_providers_v1_organizations_organization_id_providers_validate_get.additional_properties = additional_properties
        return validate_providers_v1_organizations_organization_id_providers_validate_get_response_validate_providers_v1_organizations_organization_id_providers_validate_get

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> ProviderValidationResponse:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: ProviderValidationResponse) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
