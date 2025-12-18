from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_pricing import ModelPricing
    from ..models.model_response_benchmark_scores_type_0 import (
        ModelResponseBenchmarkScoresType0,
    )
    from ..models.model_response_performance_ratings_type_0 import (
        ModelResponsePerformanceRatingsType0,
    )


T = TypeVar("T", bound="ModelResponse")


@_attrs_define
class ModelResponse:
    """Response schema for model catalog entries.

    Attributes:
        id (str): Model ID with mdl_ prefix
        key (str): Stable internal slug
        name (str): Display name (maps to title)
        is_visible_in_ui (bool): Whether model is shown in UI selectors
        is_deprecated (bool): Whether model is deprecated (computed from is_active)
        availability_status (str): Availability status: 'general_availability' or 'coming_soon'
        description (None | str | Unset): Model description
        provider (None | str | Unset): Provider slug
        capabilities (list[str] | None | Unset): Flattened list of capability strings
        context_window (int | None | Unset): Maximum context tokens (maps to model_context_limit)
        pricing (ModelPricing | None | Unset): Pricing information
        release_date (datetime.datetime | None | Unset): Model release date (when include_details=true)
        recommended_for (list[str] | None | Unset): Recommended use cases (when include_details=true)
        model_version (None | str | Unset): Model version identifier
        training_data_cutoff (datetime.datetime | None | Unset): Training data cutoff date
        added_to_aitronos_date (datetime.datetime | None | Unset): Date when model was added to Aitronos
        use_cases (None | str | Unset): Detailed use case descriptions
        strengths (None | str | Unset): Model strengths and advantages
        limitations (None | str | Unset): Model limitations and constraints
        performance_ratings (ModelResponsePerformanceRatingsType0 | None | Unset): Performance ratings across different
            dimensions
        benchmark_scores (ModelResponseBenchmarkScoresType0 | None | Unset): Benchmark test scores
        documentation_url (None | str | Unset): Link to Aitronos model documentation
        provider_docs_url (None | str | Unset): Link to provider's model documentation
        badge (None | str | Unset): UI badge identifier (e.g., 'recommended')
    """

    id: str
    key: str
    name: str
    is_visible_in_ui: bool
    is_deprecated: bool
    availability_status: str
    description: None | str | Unset = UNSET
    provider: None | str | Unset = UNSET
    capabilities: list[str] | None | Unset = UNSET
    context_window: int | None | Unset = UNSET
    pricing: ModelPricing | None | Unset = UNSET
    release_date: datetime.datetime | None | Unset = UNSET
    recommended_for: list[str] | None | Unset = UNSET
    model_version: None | str | Unset = UNSET
    training_data_cutoff: datetime.datetime | None | Unset = UNSET
    added_to_aitronos_date: datetime.datetime | None | Unset = UNSET
    use_cases: None | str | Unset = UNSET
    strengths: None | str | Unset = UNSET
    limitations: None | str | Unset = UNSET
    performance_ratings: ModelResponsePerformanceRatingsType0 | None | Unset = UNSET
    benchmark_scores: ModelResponseBenchmarkScoresType0 | None | Unset = UNSET
    documentation_url: None | str | Unset = UNSET
    provider_docs_url: None | str | Unset = UNSET
    badge: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_pricing import ModelPricing
        from ..models.model_response_benchmark_scores_type_0 import (
            ModelResponseBenchmarkScoresType0,
        )
        from ..models.model_response_performance_ratings_type_0 import (
            ModelResponsePerformanceRatingsType0,
        )

        id = self.id

        key = self.key

        name = self.name

        is_visible_in_ui = self.is_visible_in_ui

        is_deprecated = self.is_deprecated

        availability_status = self.availability_status

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        provider: None | str | Unset
        if isinstance(self.provider, Unset):
            provider = UNSET
        else:
            provider = self.provider

        capabilities: list[str] | None | Unset
        if isinstance(self.capabilities, Unset):
            capabilities = UNSET
        elif isinstance(self.capabilities, list):
            capabilities = self.capabilities

        else:
            capabilities = self.capabilities

        context_window: int | None | Unset
        if isinstance(self.context_window, Unset):
            context_window = UNSET
        else:
            context_window = self.context_window

        pricing: dict[str, Any] | None | Unset
        if isinstance(self.pricing, Unset):
            pricing = UNSET
        elif isinstance(self.pricing, ModelPricing):
            pricing = self.pricing.to_dict()
        else:
            pricing = self.pricing

        release_date: None | str | Unset
        if isinstance(self.release_date, Unset):
            release_date = UNSET
        elif isinstance(self.release_date, datetime.datetime):
            release_date = self.release_date.isoformat()
        else:
            release_date = self.release_date

        recommended_for: list[str] | None | Unset
        if isinstance(self.recommended_for, Unset):
            recommended_for = UNSET
        elif isinstance(self.recommended_for, list):
            recommended_for = self.recommended_for

        else:
            recommended_for = self.recommended_for

        model_version: None | str | Unset
        if isinstance(self.model_version, Unset):
            model_version = UNSET
        else:
            model_version = self.model_version

        training_data_cutoff: None | str | Unset
        if isinstance(self.training_data_cutoff, Unset):
            training_data_cutoff = UNSET
        elif isinstance(self.training_data_cutoff, datetime.datetime):
            training_data_cutoff = self.training_data_cutoff.isoformat()
        else:
            training_data_cutoff = self.training_data_cutoff

        added_to_aitronos_date: None | str | Unset
        if isinstance(self.added_to_aitronos_date, Unset):
            added_to_aitronos_date = UNSET
        elif isinstance(self.added_to_aitronos_date, datetime.datetime):
            added_to_aitronos_date = self.added_to_aitronos_date.isoformat()
        else:
            added_to_aitronos_date = self.added_to_aitronos_date

        use_cases: None | str | Unset
        if isinstance(self.use_cases, Unset):
            use_cases = UNSET
        else:
            use_cases = self.use_cases

        strengths: None | str | Unset
        if isinstance(self.strengths, Unset):
            strengths = UNSET
        else:
            strengths = self.strengths

        limitations: None | str | Unset
        if isinstance(self.limitations, Unset):
            limitations = UNSET
        else:
            limitations = self.limitations

        performance_ratings: dict[str, Any] | None | Unset
        if isinstance(self.performance_ratings, Unset):
            performance_ratings = UNSET
        elif isinstance(self.performance_ratings, ModelResponsePerformanceRatingsType0):
            performance_ratings = self.performance_ratings.to_dict()
        else:
            performance_ratings = self.performance_ratings

        benchmark_scores: dict[str, Any] | None | Unset
        if isinstance(self.benchmark_scores, Unset):
            benchmark_scores = UNSET
        elif isinstance(self.benchmark_scores, ModelResponseBenchmarkScoresType0):
            benchmark_scores = self.benchmark_scores.to_dict()
        else:
            benchmark_scores = self.benchmark_scores

        documentation_url: None | str | Unset
        if isinstance(self.documentation_url, Unset):
            documentation_url = UNSET
        else:
            documentation_url = self.documentation_url

        provider_docs_url: None | str | Unset
        if isinstance(self.provider_docs_url, Unset):
            provider_docs_url = UNSET
        else:
            provider_docs_url = self.provider_docs_url

        badge: None | str | Unset
        if isinstance(self.badge, Unset):
            badge = UNSET
        else:
            badge = self.badge

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "key": key,
                "name": name,
                "is_visible_in_ui": is_visible_in_ui,
                "is_deprecated": is_deprecated,
                "availability_status": availability_status,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if provider is not UNSET:
            field_dict["provider"] = provider
        if capabilities is not UNSET:
            field_dict["capabilities"] = capabilities
        if context_window is not UNSET:
            field_dict["context_window"] = context_window
        if pricing is not UNSET:
            field_dict["pricing"] = pricing
        if release_date is not UNSET:
            field_dict["release_date"] = release_date
        if recommended_for is not UNSET:
            field_dict["recommended_for"] = recommended_for
        if model_version is not UNSET:
            field_dict["model_version"] = model_version
        if training_data_cutoff is not UNSET:
            field_dict["training_data_cutoff"] = training_data_cutoff
        if added_to_aitronos_date is not UNSET:
            field_dict["added_to_aitronos_date"] = added_to_aitronos_date
        if use_cases is not UNSET:
            field_dict["use_cases"] = use_cases
        if strengths is not UNSET:
            field_dict["strengths"] = strengths
        if limitations is not UNSET:
            field_dict["limitations"] = limitations
        if performance_ratings is not UNSET:
            field_dict["performance_ratings"] = performance_ratings
        if benchmark_scores is not UNSET:
            field_dict["benchmark_scores"] = benchmark_scores
        if documentation_url is not UNSET:
            field_dict["documentation_url"] = documentation_url
        if provider_docs_url is not UNSET:
            field_dict["provider_docs_url"] = provider_docs_url
        if badge is not UNSET:
            field_dict["badge"] = badge

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_pricing import ModelPricing
        from ..models.model_response_benchmark_scores_type_0 import (
            ModelResponseBenchmarkScoresType0,
        )
        from ..models.model_response_performance_ratings_type_0 import (
            ModelResponsePerformanceRatingsType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        key = d.pop("key")

        name = d.pop("name")

        is_visible_in_ui = d.pop("is_visible_in_ui")

        is_deprecated = d.pop("is_deprecated")

        availability_status = d.pop("availability_status")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_provider(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider = _parse_provider(d.pop("provider", UNSET))

        def _parse_capabilities(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                capabilities_type_0 = cast(list[str], data)

                return capabilities_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        capabilities = _parse_capabilities(d.pop("capabilities", UNSET))

        def _parse_context_window(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        context_window = _parse_context_window(d.pop("context_window", UNSET))

        def _parse_pricing(data: object) -> ModelPricing | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                pricing_type_0 = ModelPricing.from_dict(data)

                return pricing_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelPricing | None | Unset, data)

        pricing = _parse_pricing(d.pop("pricing", UNSET))

        def _parse_release_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                release_date_type_0 = isoparse(data)

                return release_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        release_date = _parse_release_date(d.pop("release_date", UNSET))

        def _parse_recommended_for(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                recommended_for_type_0 = cast(list[str], data)

                return recommended_for_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        recommended_for = _parse_recommended_for(d.pop("recommended_for", UNSET))

        def _parse_model_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model_version = _parse_model_version(d.pop("model_version", UNSET))

        def _parse_training_data_cutoff(
            data: object,
        ) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                training_data_cutoff_type_0 = isoparse(data)

                return training_data_cutoff_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        training_data_cutoff = _parse_training_data_cutoff(
            d.pop("training_data_cutoff", UNSET)
        )

        def _parse_added_to_aitronos_date(
            data: object,
        ) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                added_to_aitronos_date_type_0 = isoparse(data)

                return added_to_aitronos_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        added_to_aitronos_date = _parse_added_to_aitronos_date(
            d.pop("added_to_aitronos_date", UNSET)
        )

        def _parse_use_cases(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        use_cases = _parse_use_cases(d.pop("use_cases", UNSET))

        def _parse_strengths(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        strengths = _parse_strengths(d.pop("strengths", UNSET))

        def _parse_limitations(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        limitations = _parse_limitations(d.pop("limitations", UNSET))

        def _parse_performance_ratings(
            data: object,
        ) -> ModelResponsePerformanceRatingsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                performance_ratings_type_0 = (
                    ModelResponsePerformanceRatingsType0.from_dict(data)
                )

                return performance_ratings_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelResponsePerformanceRatingsType0 | None | Unset, data)

        performance_ratings = _parse_performance_ratings(
            d.pop("performance_ratings", UNSET)
        )

        def _parse_benchmark_scores(
            data: object,
        ) -> ModelResponseBenchmarkScoresType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                benchmark_scores_type_0 = ModelResponseBenchmarkScoresType0.from_dict(
                    data
                )

                return benchmark_scores_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelResponseBenchmarkScoresType0 | None | Unset, data)

        benchmark_scores = _parse_benchmark_scores(d.pop("benchmark_scores", UNSET))

        def _parse_documentation_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        documentation_url = _parse_documentation_url(d.pop("documentation_url", UNSET))

        def _parse_provider_docs_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_docs_url = _parse_provider_docs_url(d.pop("provider_docs_url", UNSET))

        def _parse_badge(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        badge = _parse_badge(d.pop("badge", UNSET))

        model_response = cls(
            id=id,
            key=key,
            name=name,
            is_visible_in_ui=is_visible_in_ui,
            is_deprecated=is_deprecated,
            availability_status=availability_status,
            description=description,
            provider=provider,
            capabilities=capabilities,
            context_window=context_window,
            pricing=pricing,
            release_date=release_date,
            recommended_for=recommended_for,
            model_version=model_version,
            training_data_cutoff=training_data_cutoff,
            added_to_aitronos_date=added_to_aitronos_date,
            use_cases=use_cases,
            strengths=strengths,
            limitations=limitations,
            performance_ratings=performance_ratings,
            benchmark_scores=benchmark_scores,
            documentation_url=documentation_url,
            provider_docs_url=provider_docs_url,
            badge=badge,
        )

        model_response.additional_properties = d
        return model_response

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
