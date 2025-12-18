from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CountryResponse")


@_attrs_define
class CountryResponse:
    """Response schema for country data.

    Attributes:
        id (str): Country ID with country_ prefix
        code (str): ISO 3166-1 alpha-2 code (e.g., US, CH)
        code_alpha3 (str): ISO 3166-1 alpha-3 code (e.g., USA, CHE)
        name (str): Official country name
        is_active (bool): Whether country is active
        order (int): Display order
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        native_name (None | str | Unset): Country name in native language
        phone_code (None | str | Unset): International dialing code (e.g., +1, +41)
        currency_code (None | str | Unset): ISO 4217 currency code (e.g., USD, CHF)
        currency_name (None | str | Unset): Currency name
        currency_symbol (None | str | Unset): Currency symbol (e.g., $, CHF)
        flag_emoji (None | str | Unset): Flag emoji (e.g., 🇺🇸, 🇨🇭)
        region (None | str | Unset): Geographic region (e.g., Americas, Europe)
        subregion (None | str | Unset): Geographic subregion
        latitude (float | None | Unset): Country center latitude
        longitude (float | None | Unset): Country center longitude
    """

    id: str
    code: str
    code_alpha3: str
    name: str
    is_active: bool
    order: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    native_name: None | str | Unset = UNSET
    phone_code: None | str | Unset = UNSET
    currency_code: None | str | Unset = UNSET
    currency_name: None | str | Unset = UNSET
    currency_symbol: None | str | Unset = UNSET
    flag_emoji: None | str | Unset = UNSET
    region: None | str | Unset = UNSET
    subregion: None | str | Unset = UNSET
    latitude: float | None | Unset = UNSET
    longitude: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        code = self.code

        code_alpha3 = self.code_alpha3

        name = self.name

        is_active = self.is_active

        order = self.order

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        native_name: None | str | Unset
        if isinstance(self.native_name, Unset):
            native_name = UNSET
        else:
            native_name = self.native_name

        phone_code: None | str | Unset
        if isinstance(self.phone_code, Unset):
            phone_code = UNSET
        else:
            phone_code = self.phone_code

        currency_code: None | str | Unset
        if isinstance(self.currency_code, Unset):
            currency_code = UNSET
        else:
            currency_code = self.currency_code

        currency_name: None | str | Unset
        if isinstance(self.currency_name, Unset):
            currency_name = UNSET
        else:
            currency_name = self.currency_name

        currency_symbol: None | str | Unset
        if isinstance(self.currency_symbol, Unset):
            currency_symbol = UNSET
        else:
            currency_symbol = self.currency_symbol

        flag_emoji: None | str | Unset
        if isinstance(self.flag_emoji, Unset):
            flag_emoji = UNSET
        else:
            flag_emoji = self.flag_emoji

        region: None | str | Unset
        if isinstance(self.region, Unset):
            region = UNSET
        else:
            region = self.region

        subregion: None | str | Unset
        if isinstance(self.subregion, Unset):
            subregion = UNSET
        else:
            subregion = self.subregion

        latitude: float | None | Unset
        if isinstance(self.latitude, Unset):
            latitude = UNSET
        else:
            latitude = self.latitude

        longitude: float | None | Unset
        if isinstance(self.longitude, Unset):
            longitude = UNSET
        else:
            longitude = self.longitude

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "code": code,
                "code_alpha3": code_alpha3,
                "name": name,
                "is_active": is_active,
                "order": order,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if native_name is not UNSET:
            field_dict["native_name"] = native_name
        if phone_code is not UNSET:
            field_dict["phone_code"] = phone_code
        if currency_code is not UNSET:
            field_dict["currency_code"] = currency_code
        if currency_name is not UNSET:
            field_dict["currency_name"] = currency_name
        if currency_symbol is not UNSET:
            field_dict["currency_symbol"] = currency_symbol
        if flag_emoji is not UNSET:
            field_dict["flag_emoji"] = flag_emoji
        if region is not UNSET:
            field_dict["region"] = region
        if subregion is not UNSET:
            field_dict["subregion"] = subregion
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        code = d.pop("code")

        code_alpha3 = d.pop("code_alpha3")

        name = d.pop("name")

        is_active = d.pop("is_active")

        order = d.pop("order")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_native_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        native_name = _parse_native_name(d.pop("native_name", UNSET))

        def _parse_phone_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        phone_code = _parse_phone_code(d.pop("phone_code", UNSET))

        def _parse_currency_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        currency_code = _parse_currency_code(d.pop("currency_code", UNSET))

        def _parse_currency_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        currency_name = _parse_currency_name(d.pop("currency_name", UNSET))

        def _parse_currency_symbol(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        currency_symbol = _parse_currency_symbol(d.pop("currency_symbol", UNSET))

        def _parse_flag_emoji(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        flag_emoji = _parse_flag_emoji(d.pop("flag_emoji", UNSET))

        def _parse_region(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        region = _parse_region(d.pop("region", UNSET))

        def _parse_subregion(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        subregion = _parse_subregion(d.pop("subregion", UNSET))

        def _parse_latitude(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        latitude = _parse_latitude(d.pop("latitude", UNSET))

        def _parse_longitude(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        longitude = _parse_longitude(d.pop("longitude", UNSET))

        country_response = cls(
            id=id,
            code=code,
            code_alpha3=code_alpha3,
            name=name,
            is_active=is_active,
            order=order,
            created_at=created_at,
            updated_at=updated_at,
            native_name=native_name,
            phone_code=phone_code,
            currency_code=currency_code,
            currency_name=currency_name,
            currency_symbol=currency_symbol,
            flag_emoji=flag_emoji,
            region=region,
            subregion=subregion,
            latitude=latitude,
            longitude=longitude,
        )

        country_response.additional_properties = d
        return country_response

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
