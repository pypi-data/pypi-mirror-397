# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .files import (
    FilesResource,
    AsyncFilesResource,
    FilesResourceWithRawResponse,
    AsyncFilesResourceWithRawResponse,
    FilesResourceWithStreamingResponse,
    AsyncFilesResourceWithStreamingResponse,
)
from .batches import (
    BatchesResource,
    AsyncBatchesResource,
    BatchesResourceWithRawResponse,
    AsyncBatchesResourceWithRawResponse,
    BatchesResourceWithStreamingResponse,
    AsyncBatchesResourceWithStreamingResponse,
)
from .dynamic import (
    DynamicResource,
    AsyncDynamicResource,
    DynamicResourceWithRawResponse,
    AsyncDynamicResourceWithRawResponse,
    DynamicResourceWithStreamingResponse,
    AsyncDynamicResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .models.models import (
    ModelsResource,
    AsyncModelsResource,
    ModelsResourceWithRawResponse,
    AsyncModelsResourceWithRawResponse,
    ModelsResourceWithStreamingResponse,
    AsyncModelsResourceWithStreamingResponse,
)
from .cached_contents import (
    CachedContentsResource,
    AsyncCachedContentsResource,
    CachedContentsResourceWithRawResponse,
    AsyncCachedContentsResourceWithRawResponse,
    CachedContentsResourceWithStreamingResponse,
    AsyncCachedContentsResourceWithStreamingResponse,
)
from .corpora.corpora import (
    CorporaResource,
    AsyncCorporaResource,
    CorporaResourceWithRawResponse,
    AsyncCorporaResourceWithRawResponse,
    CorporaResourceWithStreamingResponse,
    AsyncCorporaResourceWithStreamingResponse,
)
from .generated_files import (
    GeneratedFilesResource,
    AsyncGeneratedFilesResource,
    GeneratedFilesResourceWithRawResponse,
    AsyncGeneratedFilesResourceWithRawResponse,
    GeneratedFilesResourceWithStreamingResponse,
    AsyncGeneratedFilesResourceWithStreamingResponse,
)
from .rag_stores.rag_stores import (
    RagStoresResource,
    AsyncRagStoresResource,
    RagStoresResourceWithRawResponse,
    AsyncRagStoresResourceWithRawResponse,
    RagStoresResourceWithStreamingResponse,
    AsyncRagStoresResourceWithStreamingResponse,
)
from .tuned_models.tuned_models import (
    TunedModelsResource,
    AsyncTunedModelsResource,
    TunedModelsResourceWithRawResponse,
    AsyncTunedModelsResourceWithRawResponse,
    TunedModelsResourceWithStreamingResponse,
    AsyncTunedModelsResourceWithStreamingResponse,
)

__all__ = ["BetaResource", "AsyncBetaResource"]


class BetaResource(SyncAPIResource):
    @cached_property
    def models(self) -> ModelsResource:
        return ModelsResource(self._client)

    @cached_property
    def cached_contents(self) -> CachedContentsResource:
        return CachedContentsResource(self._client)

    @cached_property
    def rag_stores(self) -> RagStoresResource:
        return RagStoresResource(self._client)

    @cached_property
    def tuned_models(self) -> TunedModelsResource:
        return TunedModelsResource(self._client)

    @cached_property
    def corpora(self) -> CorporaResource:
        return CorporaResource(self._client)

    @cached_property
    def generated_files(self) -> GeneratedFilesResource:
        return GeneratedFilesResource(self._client)

    @cached_property
    def files(self) -> FilesResource:
        return FilesResource(self._client)

    @cached_property
    def batches(self) -> BatchesResource:
        return BatchesResource(self._client)

    @cached_property
    def dynamic(self) -> DynamicResource:
        return DynamicResource(self._client)

    @cached_property
    def with_raw_response(self) -> BetaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return BetaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BetaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return BetaResourceWithStreamingResponse(self)


class AsyncBetaResource(AsyncAPIResource):
    @cached_property
    def models(self) -> AsyncModelsResource:
        return AsyncModelsResource(self._client)

    @cached_property
    def cached_contents(self) -> AsyncCachedContentsResource:
        return AsyncCachedContentsResource(self._client)

    @cached_property
    def rag_stores(self) -> AsyncRagStoresResource:
        return AsyncRagStoresResource(self._client)

    @cached_property
    def tuned_models(self) -> AsyncTunedModelsResource:
        return AsyncTunedModelsResource(self._client)

    @cached_property
    def corpora(self) -> AsyncCorporaResource:
        return AsyncCorporaResource(self._client)

    @cached_property
    def generated_files(self) -> AsyncGeneratedFilesResource:
        return AsyncGeneratedFilesResource(self._client)

    @cached_property
    def files(self) -> AsyncFilesResource:
        return AsyncFilesResource(self._client)

    @cached_property
    def batches(self) -> AsyncBatchesResource:
        return AsyncBatchesResource(self._client)

    @cached_property
    def dynamic(self) -> AsyncDynamicResource:
        return AsyncDynamicResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBetaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBetaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBetaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncBetaResourceWithStreamingResponse(self)


class BetaResourceWithRawResponse:
    def __init__(self, beta: BetaResource) -> None:
        self._beta = beta

    @cached_property
    def models(self) -> ModelsResourceWithRawResponse:
        return ModelsResourceWithRawResponse(self._beta.models)

    @cached_property
    def cached_contents(self) -> CachedContentsResourceWithRawResponse:
        return CachedContentsResourceWithRawResponse(self._beta.cached_contents)

    @cached_property
    def rag_stores(self) -> RagStoresResourceWithRawResponse:
        return RagStoresResourceWithRawResponse(self._beta.rag_stores)

    @cached_property
    def tuned_models(self) -> TunedModelsResourceWithRawResponse:
        return TunedModelsResourceWithRawResponse(self._beta.tuned_models)

    @cached_property
    def corpora(self) -> CorporaResourceWithRawResponse:
        return CorporaResourceWithRawResponse(self._beta.corpora)

    @cached_property
    def generated_files(self) -> GeneratedFilesResourceWithRawResponse:
        return GeneratedFilesResourceWithRawResponse(self._beta.generated_files)

    @cached_property
    def files(self) -> FilesResourceWithRawResponse:
        return FilesResourceWithRawResponse(self._beta.files)

    @cached_property
    def batches(self) -> BatchesResourceWithRawResponse:
        return BatchesResourceWithRawResponse(self._beta.batches)

    @cached_property
    def dynamic(self) -> DynamicResourceWithRawResponse:
        return DynamicResourceWithRawResponse(self._beta.dynamic)


class AsyncBetaResourceWithRawResponse:
    def __init__(self, beta: AsyncBetaResource) -> None:
        self._beta = beta

    @cached_property
    def models(self) -> AsyncModelsResourceWithRawResponse:
        return AsyncModelsResourceWithRawResponse(self._beta.models)

    @cached_property
    def cached_contents(self) -> AsyncCachedContentsResourceWithRawResponse:
        return AsyncCachedContentsResourceWithRawResponse(self._beta.cached_contents)

    @cached_property
    def rag_stores(self) -> AsyncRagStoresResourceWithRawResponse:
        return AsyncRagStoresResourceWithRawResponse(self._beta.rag_stores)

    @cached_property
    def tuned_models(self) -> AsyncTunedModelsResourceWithRawResponse:
        return AsyncTunedModelsResourceWithRawResponse(self._beta.tuned_models)

    @cached_property
    def corpora(self) -> AsyncCorporaResourceWithRawResponse:
        return AsyncCorporaResourceWithRawResponse(self._beta.corpora)

    @cached_property
    def generated_files(self) -> AsyncGeneratedFilesResourceWithRawResponse:
        return AsyncGeneratedFilesResourceWithRawResponse(self._beta.generated_files)

    @cached_property
    def files(self) -> AsyncFilesResourceWithRawResponse:
        return AsyncFilesResourceWithRawResponse(self._beta.files)

    @cached_property
    def batches(self) -> AsyncBatchesResourceWithRawResponse:
        return AsyncBatchesResourceWithRawResponse(self._beta.batches)

    @cached_property
    def dynamic(self) -> AsyncDynamicResourceWithRawResponse:
        return AsyncDynamicResourceWithRawResponse(self._beta.dynamic)


class BetaResourceWithStreamingResponse:
    def __init__(self, beta: BetaResource) -> None:
        self._beta = beta

    @cached_property
    def models(self) -> ModelsResourceWithStreamingResponse:
        return ModelsResourceWithStreamingResponse(self._beta.models)

    @cached_property
    def cached_contents(self) -> CachedContentsResourceWithStreamingResponse:
        return CachedContentsResourceWithStreamingResponse(self._beta.cached_contents)

    @cached_property
    def rag_stores(self) -> RagStoresResourceWithStreamingResponse:
        return RagStoresResourceWithStreamingResponse(self._beta.rag_stores)

    @cached_property
    def tuned_models(self) -> TunedModelsResourceWithStreamingResponse:
        return TunedModelsResourceWithStreamingResponse(self._beta.tuned_models)

    @cached_property
    def corpora(self) -> CorporaResourceWithStreamingResponse:
        return CorporaResourceWithStreamingResponse(self._beta.corpora)

    @cached_property
    def generated_files(self) -> GeneratedFilesResourceWithStreamingResponse:
        return GeneratedFilesResourceWithStreamingResponse(self._beta.generated_files)

    @cached_property
    def files(self) -> FilesResourceWithStreamingResponse:
        return FilesResourceWithStreamingResponse(self._beta.files)

    @cached_property
    def batches(self) -> BatchesResourceWithStreamingResponse:
        return BatchesResourceWithStreamingResponse(self._beta.batches)

    @cached_property
    def dynamic(self) -> DynamicResourceWithStreamingResponse:
        return DynamicResourceWithStreamingResponse(self._beta.dynamic)


class AsyncBetaResourceWithStreamingResponse:
    def __init__(self, beta: AsyncBetaResource) -> None:
        self._beta = beta

    @cached_property
    def models(self) -> AsyncModelsResourceWithStreamingResponse:
        return AsyncModelsResourceWithStreamingResponse(self._beta.models)

    @cached_property
    def cached_contents(self) -> AsyncCachedContentsResourceWithStreamingResponse:
        return AsyncCachedContentsResourceWithStreamingResponse(self._beta.cached_contents)

    @cached_property
    def rag_stores(self) -> AsyncRagStoresResourceWithStreamingResponse:
        return AsyncRagStoresResourceWithStreamingResponse(self._beta.rag_stores)

    @cached_property
    def tuned_models(self) -> AsyncTunedModelsResourceWithStreamingResponse:
        return AsyncTunedModelsResourceWithStreamingResponse(self._beta.tuned_models)

    @cached_property
    def corpora(self) -> AsyncCorporaResourceWithStreamingResponse:
        return AsyncCorporaResourceWithStreamingResponse(self._beta.corpora)

    @cached_property
    def generated_files(self) -> AsyncGeneratedFilesResourceWithStreamingResponse:
        return AsyncGeneratedFilesResourceWithStreamingResponse(self._beta.generated_files)

    @cached_property
    def files(self) -> AsyncFilesResourceWithStreamingResponse:
        return AsyncFilesResourceWithStreamingResponse(self._beta.files)

    @cached_property
    def batches(self) -> AsyncBatchesResourceWithStreamingResponse:
        return AsyncBatchesResourceWithStreamingResponse(self._beta.batches)

    @cached_property
    def dynamic(self) -> AsyncDynamicResourceWithStreamingResponse:
        return AsyncDynamicResourceWithStreamingResponse(self._beta.dynamic)
