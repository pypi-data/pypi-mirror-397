from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="VectorStoreFileResponse")


@_attrs_define
class VectorStoreFileResponse:
    """Schema for vector store file response.

    Attributes:
        id (str): Unique identifier for the file association
        vector_store_id (str): ID of the vector store
        file_id (str): ID of the file
        added_at (datetime.datetime): Timestamp when the file was added
        processing_status (str): Processing status: pending, processing, completed, failed
        chunk_count (int): Number of chunks created from this file
        added_by (None | str | Unset): User ID who added the file (if added by user)
        added_by_api_key_id (None | str | Unset): API key ID that added the file (if added by API key)
        processing_started_at (datetime.datetime | None | Unset): When processing started
        processing_completed_at (datetime.datetime | None | Unset): When processing completed
        error_message (None | str | Unset): Error message if processing failed
        embedding_model (None | str | Unset): Embedding model used for processing
        file_name (None | str | Unset): Original filename
        file_size (int | None | Unset): File size in bytes
        mime_type (None | str | Unset): File MIME type
        estimated_completion_seconds (int | None | Unset): Estimated seconds until processing completes (only for
            pending/processing status)
    """

    id: str
    vector_store_id: str
    file_id: str
    added_at: datetime.datetime
    processing_status: str
    chunk_count: int
    added_by: None | str | Unset = UNSET
    added_by_api_key_id: None | str | Unset = UNSET
    processing_started_at: datetime.datetime | None | Unset = UNSET
    processing_completed_at: datetime.datetime | None | Unset = UNSET
    error_message: None | str | Unset = UNSET
    embedding_model: None | str | Unset = UNSET
    file_name: None | str | Unset = UNSET
    file_size: int | None | Unset = UNSET
    mime_type: None | str | Unset = UNSET
    estimated_completion_seconds: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        vector_store_id = self.vector_store_id

        file_id = self.file_id

        added_at = self.added_at.isoformat()

        processing_status = self.processing_status

        chunk_count = self.chunk_count

        added_by: None | str | Unset
        if isinstance(self.added_by, Unset):
            added_by = UNSET
        else:
            added_by = self.added_by

        added_by_api_key_id: None | str | Unset
        if isinstance(self.added_by_api_key_id, Unset):
            added_by_api_key_id = UNSET
        else:
            added_by_api_key_id = self.added_by_api_key_id

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

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        embedding_model: None | str | Unset
        if isinstance(self.embedding_model, Unset):
            embedding_model = UNSET
        else:
            embedding_model = self.embedding_model

        file_name: None | str | Unset
        if isinstance(self.file_name, Unset):
            file_name = UNSET
        else:
            file_name = self.file_name

        file_size: int | None | Unset
        if isinstance(self.file_size, Unset):
            file_size = UNSET
        else:
            file_size = self.file_size

        mime_type: None | str | Unset
        if isinstance(self.mime_type, Unset):
            mime_type = UNSET
        else:
            mime_type = self.mime_type

        estimated_completion_seconds: int | None | Unset
        if isinstance(self.estimated_completion_seconds, Unset):
            estimated_completion_seconds = UNSET
        else:
            estimated_completion_seconds = self.estimated_completion_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "vector_store_id": vector_store_id,
                "file_id": file_id,
                "added_at": added_at,
                "processing_status": processing_status,
                "chunk_count": chunk_count,
            }
        )
        if added_by is not UNSET:
            field_dict["added_by"] = added_by
        if added_by_api_key_id is not UNSET:
            field_dict["added_by_api_key_id"] = added_by_api_key_id
        if processing_started_at is not UNSET:
            field_dict["processing_started_at"] = processing_started_at
        if processing_completed_at is not UNSET:
            field_dict["processing_completed_at"] = processing_completed_at
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if embedding_model is not UNSET:
            field_dict["embedding_model"] = embedding_model
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
        if file_size is not UNSET:
            field_dict["file_size"] = file_size
        if mime_type is not UNSET:
            field_dict["mime_type"] = mime_type
        if estimated_completion_seconds is not UNSET:
            field_dict["estimated_completion_seconds"] = estimated_completion_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        vector_store_id = d.pop("vector_store_id")

        file_id = d.pop("file_id")

        added_at = isoparse(d.pop("added_at"))

        processing_status = d.pop("processing_status")

        chunk_count = d.pop("chunk_count")

        def _parse_added_by(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        added_by = _parse_added_by(d.pop("added_by", UNSET))

        def _parse_added_by_api_key_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        added_by_api_key_id = _parse_added_by_api_key_id(
            d.pop("added_by_api_key_id", UNSET)
        )

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

        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        def _parse_embedding_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        embedding_model = _parse_embedding_model(d.pop("embedding_model", UNSET))

        def _parse_file_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file_name = _parse_file_name(d.pop("file_name", UNSET))

        def _parse_file_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        file_size = _parse_file_size(d.pop("file_size", UNSET))

        def _parse_mime_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mime_type = _parse_mime_type(d.pop("mime_type", UNSET))

        def _parse_estimated_completion_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        estimated_completion_seconds = _parse_estimated_completion_seconds(
            d.pop("estimated_completion_seconds", UNSET)
        )

        vector_store_file_response = cls(
            id=id,
            vector_store_id=vector_store_id,
            file_id=file_id,
            added_at=added_at,
            processing_status=processing_status,
            chunk_count=chunk_count,
            added_by=added_by,
            added_by_api_key_id=added_by_api_key_id,
            processing_started_at=processing_started_at,
            processing_completed_at=processing_completed_at,
            error_message=error_message,
            embedding_model=embedding_model,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            estimated_completion_seconds=estimated_completion_seconds,
        )

        vector_store_file_response.additional_properties = d
        return vector_store_file_response

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
