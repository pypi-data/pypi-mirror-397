# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from . import beta
from .. import _compat

# Rebuild cyclical models only after all modules are imported.
# This ensures that, when building the deferred (due to cyclical references) model schema,
# Pydantic can resolve the necessary references.
# See: https://github.com/pydantic/pydantic/issues/11250 for more context.
if _compat.PYDANTIC_V1:
    beta.generate_content_request.GenerateContentRequest.update_forward_refs()  # type: ignore
    beta.schema.Schema.update_forward_refs()  # type: ignore
    beta.cached_content.CachedContent.update_forward_refs()  # type: ignore
    beta.tool.Tool.update_forward_refs()  # type: ignore
    beta.cached_content_list_response.CachedContentListResponse.update_forward_refs()  # type: ignore
    beta.generate_content_batch.GenerateContentBatch.update_forward_refs()  # type: ignore
else:
    beta.generate_content_request.GenerateContentRequest.model_rebuild(_parent_namespace_depth=0)
    beta.schema.Schema.model_rebuild(_parent_namespace_depth=0)
    beta.cached_content.CachedContent.model_rebuild(_parent_namespace_depth=0)
    beta.tool.Tool.model_rebuild(_parent_namespace_depth=0)
    beta.cached_content_list_response.CachedContentListResponse.model_rebuild(_parent_namespace_depth=0)
    beta.generate_content_batch.GenerateContentBatch.model_rebuild(_parent_namespace_depth=0)
