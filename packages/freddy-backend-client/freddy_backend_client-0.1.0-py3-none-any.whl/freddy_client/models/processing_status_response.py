from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProcessingStatusResponse")


@_attrs_define
class ProcessingStatusResponse:
    """Response schema for file processing status.

    Attributes:
        vector_store_file_id (str): VectorStoreFile ID (vsf_ prefix)
        file_id (str): File ID (file_ prefix)
        vector_store_id (str): Vector store ID
        status (str): Processing status: pending, processing, completed, failed
        added_at (datetime.datetime): When file was added to vector store
        chunk_count (int | Unset): Number of chunks created Default: 0.
        embedding_model (None | str | Unset): Embedding model used
        error_message (None | str | Unset): Error details if failed
        processing_started_at (datetime.datetime | None | Unset): When processing started
        processing_completed_at (datetime.datetime | None | Unset): When processing completed
    """

    vector_store_file_id: str
    file_id: str
    vector_store_id: str
    status: str
    added_at: datetime.datetime
    chunk_count: int | Unset = 0
    embedding_model: None | str | Unset = UNSET
    error_message: None | str | Unset = UNSET
    processing_started_at: datetime.datetime | None | Unset = UNSET
    processing_completed_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vector_store_file_id = self.vector_store_file_id

        file_id = self.file_id

        vector_store_id = self.vector_store_id

        status = self.status

        added_at = self.added_at.isoformat()

        chunk_count = self.chunk_count

        embedding_model: None | str | Unset
        if isinstance(self.embedding_model, Unset):
            embedding_model = UNSET
        else:
            embedding_model = self.embedding_model

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        processing_started_at: None | str | Unset
        if isinstance(self.processing_started_at, Unset):
            processing_started_at = UNSET
        elif isinstance(self.processing_started_at, datetime.datetime):
            processing_started_at = self.processing_started_at.isoformat()
        else:
            processing_started_at = self.processing_started_at

        processing_completed_at: None | str | Unset
        if isinstance(self.processing_completed_at, Unset):
            processing_completed_at = UNSET
        elif isinstance(self.processing_completed_at, datetime.datetime):
            processing_completed_at = self.processing_completed_at.isoformat()
        else:
            processing_completed_at = self.processing_completed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "vector_store_file_id": vector_store_file_id,
                "file_id": file_id,
                "vector_store_id": vector_store_id,
                "status": status,
                "added_at": added_at,
            }
        )
        if chunk_count is not UNSET:
            field_dict["chunk_count"] = chunk_count
        if embedding_model is not UNSET:
            field_dict["embedding_model"] = embedding_model
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if processing_started_at is not UNSET:
            field_dict["processing_started_at"] = processing_started_at
        if processing_completed_at is not UNSET:
            field_dict["processing_completed_at"] = processing_completed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        vector_store_file_id = d.pop("vector_store_file_id")

        file_id = d.pop("file_id")

        vector_store_id = d.pop("vector_store_id")

        status = d.pop("status")

        added_at = isoparse(d.pop("added_at"))

        chunk_count = d.pop("chunk_count", UNSET)

        def _parse_embedding_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        embedding_model = _parse_embedding_model(d.pop("embedding_model", UNSET))

        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        def _parse_processing_started_at(
            data: object,
        ) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                processing_started_at_type_0 = isoparse(data)

                return processing_started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        processing_started_at = _parse_processing_started_at(
            d.pop("processing_started_at", UNSET)
        )

        def _parse_processing_completed_at(
            data: object,
        ) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                processing_completed_at_type_0 = isoparse(data)

                return processing_completed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        processing_completed_at = _parse_processing_completed_at(
            d.pop("processing_completed_at", UNSET)
        )

        processing_status_response = cls(
            vector_store_file_id=vector_store_file_id,
            file_id=file_id,
            vector_store_id=vector_store_id,
            status=status,
            added_at=added_at,
            chunk_count=chunk_count,
            embedding_model=embedding_model,
            error_message=error_message,
            processing_started_at=processing_started_at,
            processing_completed_at=processing_completed_at,
        )

        processing_status_response.additional_properties = d
        return processing_status_response

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
