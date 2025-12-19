# Beta

## Models

Types:

```python
from robert_test_24.types.beta import (
    AsyncBatchEmbedContentOperation,
    AsyncBatchEmbedContentRequest,
    Candidate,
    CitationMetadata,
    ContentEmbedding,
    ContentFilter,
    EmbedContentRequest,
    EmbedContentResponse,
    EmbedTextRequest,
    Embedding,
    GenerateContentRequest,
    GenerateContentResponse,
    HarmCategory,
    LogprobsResultCandidate,
    Message,
    MessagePrompt,
    ModalityTokenCount,
    Model,
    SafetyRating,
    SafetySetting,
    Schema,
    VoiceConfig,
    ModelListResponse,
    ModelBatchEmbedContentsResponse,
    ModelBatchEmbedTextResponse,
    ModelCountMessageTokensResponse,
    ModelCountTextTokensResponse,
    ModelCountTokensResponse,
    ModelEmbedTextResponse,
    ModelGenerateAnswerResponse,
    ModelGenerateMessageResponse,
    ModelPredictResponse,
    ModelPredictLongRunningResponse,
)
```

Methods:

- <code title="get /v1beta/models/{model}">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">retrieve</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model.py">Model</a></code>
- <code title="get /v1beta/models">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">list</a>(\*\*<a href="src/robert_test_24/types/beta/model_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_list_response.py">ModelListResponse</a></code>
- <code title="post /v1beta/models/{model}:asyncBatchEmbedContent">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">async_batch_embed_content</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_async_batch_embed_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/async_batch_embed_content_operation.py">AsyncBatchEmbedContentOperation</a></code>
- <code title="post /v1beta/models/{model}:batchEmbedContents">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">batch_embed_contents</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_batch_embed_contents_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_batch_embed_contents_response.py">ModelBatchEmbedContentsResponse</a></code>
- <code title="post /v1beta/models/{model}:batchEmbedText">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">batch_embed_text</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_batch_embed_text_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_batch_embed_text_response.py">ModelBatchEmbedTextResponse</a></code>
- <code title="post /v1beta/models/{model}:batchGenerateContent">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">batch_generate_content</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_batch_generate_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/batch_generate_content_operation.py">BatchGenerateContentOperation</a></code>
- <code title="post /v1beta/models/{model}:countMessageTokens">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">count_message_tokens</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_count_message_tokens_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_count_message_tokens_response.py">ModelCountMessageTokensResponse</a></code>
- <code title="post /v1beta/models/{model}:countTextTokens">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">count_text_tokens</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_count_text_tokens_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_count_text_tokens_response.py">ModelCountTextTokensResponse</a></code>
- <code title="post /v1beta/models/{model}:countTokens">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">count_tokens</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_count_tokens_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_count_tokens_response.py">ModelCountTokensResponse</a></code>
- <code title="post /v1beta/models/{model}:embedContent">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">embed_content</a>(path_model, \*\*<a href="src/robert_test_24/types/beta/model_embed_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/embed_content_response.py">EmbedContentResponse</a></code>
- <code title="post /v1beta/models/{model}:embedText">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">embed_text</a>(path_model, \*\*<a href="src/robert_test_24/types/beta/model_embed_text_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_embed_text_response.py">ModelEmbedTextResponse</a></code>
- <code title="post /v1beta/models/{model}:generateAnswer">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">generate_answer</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_generate_answer_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_generate_answer_response.py">ModelGenerateAnswerResponse</a></code>
- <code title="post /v1beta/models/{model}:generateContent">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">generate_content</a>(path_model, \*\*<a href="src/robert_test_24/types/beta/model_generate_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generate_content_response.py">GenerateContentResponse</a></code>
- <code title="post /v1beta/models/{model}:generateMessage">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">generate_message</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_generate_message_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_generate_message_response.py">ModelGenerateMessageResponse</a></code>
- <code title="post /v1beta/models/{model}:generateText">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">generate_text</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_generate_text_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generate_text.py">GenerateText</a></code>
- <code title="post /v1beta/models/{model}:predict">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">predict</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_predict_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_predict_response.py">ModelPredictResponse</a></code>
- <code title="post /v1beta/models/{model}:predictLongRunning">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">predict_long_running</a>(model, \*\*<a href="src/robert_test_24/types/beta/model_predict_long_running_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/model_predict_long_running_response.py">ModelPredictLongRunningResponse</a></code>
- <code title="post /v1beta/models/{model}:streamGenerateContent">client.beta.models.<a href="./src/robert_test_24/resources/beta/models/models.py">stream_generate_content</a>(path_model, \*\*<a href="src/robert_test_24/types/beta/model_stream_generate_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generate_content_response.py">GenerateContentResponse</a></code>

### Operations

Methods:

- <code title="get /v1beta/models/{model}/operations/{operation}">client.beta.models.operations.<a href="./src/robert_test_24/resources/beta/models/operations.py">retrieve</a>(operation, \*, model, \*\*<a href="src/robert_test_24/types/beta/models/operation_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/operation.py">Operation</a></code>
- <code title="get /v1beta/models/{model}/operations">client.beta.models.operations.<a href="./src/robert_test_24/resources/beta/models/operations.py">list</a>(model, \*\*<a href="src/robert_test_24/types/beta/models/operation_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/tuned_models/list_operations.py">ListOperations</a></code>

## CachedContents

Types:

```python
from robert_test_24.types.beta import (
    CachedContent,
    Content,
    Tool,
    ToolConfig,
    CachedContentListResponse,
)
```

Methods:

- <code title="post /v1beta/cachedContents">client.beta.cached_contents.<a href="./src/robert_test_24/resources/beta/cached_contents.py">create</a>(\*\*<a href="src/robert_test_24/types/beta/cached_content_create_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/cached_content.py">CachedContent</a></code>
- <code title="get /v1beta/cachedContents/{id}">client.beta.cached_contents.<a href="./src/robert_test_24/resources/beta/cached_contents.py">retrieve</a>(id, \*\*<a href="src/robert_test_24/types/beta/cached_content_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/cached_content.py">CachedContent</a></code>
- <code title="patch /v1beta/cachedContents/{id}">client.beta.cached_contents.<a href="./src/robert_test_24/resources/beta/cached_contents.py">update</a>(id, \*\*<a href="src/robert_test_24/types/beta/cached_content_update_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/cached_content.py">CachedContent</a></code>
- <code title="get /v1beta/cachedContents">client.beta.cached_contents.<a href="./src/robert_test_24/resources/beta/cached_contents.py">list</a>(\*\*<a href="src/robert_test_24/types/beta/cached_content_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/cached_content_list_response.py">CachedContentListResponse</a></code>
- <code title="delete /v1beta/cachedContents/{id}">client.beta.cached_contents.<a href="./src/robert_test_24/resources/beta/cached_contents.py">delete</a>(id, \*\*<a href="src/robert_test_24/types/beta/cached_content_delete_params.py">params</a>) -> object</code>

## RagStores

Types:

```python
from robert_test_24.types.beta import (
    BaseOperation,
    CustomMetadata,
    Operation,
    RagStore,
    RagStoreListResponse,
    RagStoreUploadToRagStoreResponse,
)
```

Methods:

- <code title="post /v1beta/ragStores">client.beta.rag_stores.<a href="./src/robert_test_24/resources/beta/rag_stores/rag_stores.py">create</a>(\*\*<a href="src/robert_test_24/types/beta/rag_store_create_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_store.py">RagStore</a></code>
- <code title="get /v1beta/ragStores/{ragStore}">client.beta.rag_stores.<a href="./src/robert_test_24/resources/beta/rag_stores/rag_stores.py">retrieve</a>(rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_store_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_store.py">RagStore</a></code>
- <code title="patch /v1beta/ragStores/{ragStore}">client.beta.rag_stores.<a href="./src/robert_test_24/resources/beta/rag_stores/rag_stores.py">update</a>(rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_store_update_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_store.py">RagStore</a></code>
- <code title="get /v1beta/ragStores">client.beta.rag_stores.<a href="./src/robert_test_24/resources/beta/rag_stores/rag_stores.py">list</a>(\*\*<a href="src/robert_test_24/types/beta/rag_store_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_store_list_response.py">RagStoreListResponse</a></code>
- <code title="delete /v1beta/ragStores/{ragStore}">client.beta.rag_stores.<a href="./src/robert_test_24/resources/beta/rag_stores/rag_stores.py">delete</a>(rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_store_delete_params.py">params</a>) -> object</code>
- <code title="get /v1beta/ragStores/{ragStore}/operations/{operation}">client.beta.rag_stores.<a href="./src/robert_test_24/resources/beta/rag_stores/rag_stores.py">get_operation_status</a>(operation, \*, rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_store_get_operation_status_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/operation.py">Operation</a></code>
- <code title="post /v1beta/ragStores/{ragStore}:uploadToRagStore">client.beta.rag_stores.<a href="./src/robert_test_24/resources/beta/rag_stores/rag_stores.py">upload_to_rag_store</a>(rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_store_upload_to_rag_store_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_store_upload_to_rag_store_response.py">RagStoreUploadToRagStoreResponse</a></code>

### Documents

Types:

```python
from robert_test_24.types.beta.rag_stores import (
    Document,
    DocumentListResponse,
    DocumentQueryResponse,
)
```

Methods:

- <code title="post /v1beta/ragStores/{ragStore}/documents">client.beta.rag_stores.documents.<a href="./src/robert_test_24/resources/beta/rag_stores/documents.py">create</a>(rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_stores/document_create_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_stores/document.py">Document</a></code>
- <code title="get /v1beta/ragStores/{ragStore}/documents/{document}">client.beta.rag_stores.documents.<a href="./src/robert_test_24/resources/beta/rag_stores/documents.py">retrieve</a>(document, \*, rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_stores/document_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_stores/document.py">Document</a></code>
- <code title="get /v1beta/ragStores/{ragStore}/documents">client.beta.rag_stores.documents.<a href="./src/robert_test_24/resources/beta/rag_stores/documents.py">list</a>(rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_stores/document_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_stores/document_list_response.py">DocumentListResponse</a></code>
- <code title="delete /v1beta/ragStores/{ragStore}/documents/{document}">client.beta.rag_stores.documents.<a href="./src/robert_test_24/resources/beta/rag_stores/documents.py">delete</a>(document, \*, rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_stores/document_delete_params.py">params</a>) -> object</code>
- <code title="post /v1beta/ragStores/{ragStore}/documents/{document}:query">client.beta.rag_stores.documents.<a href="./src/robert_test_24/resources/beta/rag_stores/documents.py">query</a>(document, \*, rag_store, \*\*<a href="src/robert_test_24/types/beta/rag_stores/document_query_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_stores/document_query_response.py">DocumentQueryResponse</a></code>

### Upload

Methods:

- <code title="get /v1beta/ragStores/{ragStoresId}/upload/operations/{operationsId}">client.beta.rag_stores.upload.<a href="./src/robert_test_24/resources/beta/rag_stores/upload.py">get_operation_status</a>(operations_id, \*, rag_stores_id, \*\*<a href="src/robert_test_24/types/beta/rag_stores/upload_get_operation_status_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/operation.py">Operation</a></code>

## TunedModels

Types:

```python
from robert_test_24.types.beta import (
    BatchGenerateContentOperation,
    BatchGenerateContentRequest,
    GenerateText,
    GenerateTextRequest,
    TextPrompt,
    TunedModel,
    TuningSnapshot,
    TunedModelCreateTunedModelResponse,
    TunedModelListTunedModelsResponse,
)
```

Methods:

- <code title="post /v1beta/tunedModels/{tunedModel}:asyncBatchEmbedContent">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">async_batch_embed_content</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_model_async_batch_embed_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/async_batch_embed_content_operation.py">AsyncBatchEmbedContentOperation</a></code>
- <code title="post /v1beta/tunedModels/{tunedModel}:batchGenerateContent">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">batch_generate_content</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_model_batch_generate_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/batch_generate_content_operation.py">BatchGenerateContentOperation</a></code>
- <code title="post /v1beta/tunedModels">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">create_tuned_model</a>(\*\*<a href="src/robert_test_24/types/beta/tuned_model_create_tuned_model_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/tuned_model_create_tuned_model_response.py">TunedModelCreateTunedModelResponse</a></code>
- <code title="delete /v1beta/tunedModels/{tunedModel}">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">delete_tuned_model</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_model_delete_tuned_model_params.py">params</a>) -> object</code>
- <code title="post /v1beta/tunedModels/{tunedModel}:generateContent">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">generate_content</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_model_generate_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generate_content_response.py">GenerateContentResponse</a></code>
- <code title="post /v1beta/tunedModels/{tunedModel}:generateText">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">generate_text</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_model_generate_text_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generate_text.py">GenerateText</a></code>
- <code title="get /v1beta/tunedModels">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">list_tuned_models</a>(\*\*<a href="src/robert_test_24/types/beta/tuned_model_list_tuned_models_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/tuned_model_list_tuned_models_response.py">TunedModelListTunedModelsResponse</a></code>
- <code title="get /v1beta/tunedModels/{tunedModel}">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">retrieve_tuned_model</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_model_retrieve_tuned_model_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/tuned_model.py">TunedModel</a></code>
- <code title="post /v1beta/tunedModels/{tunedModel}:streamGenerateContent">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">stream_generate_content</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_model_stream_generate_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generate_content_response.py">GenerateContentResponse</a></code>
- <code title="post /v1beta/tunedModels/{tunedModel}:transferOwnership">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">transfer_ownership</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_model_transfer_ownership_params.py">params</a>) -> object</code>
- <code title="patch /v1beta/tunedModels/{tunedModel}">client.beta.tuned_models.<a href="./src/robert_test_24/resources/beta/tuned_models/tuned_models.py">update_tuned_model</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_model_update_tuned_model_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/tuned_model.py">TunedModel</a></code>

### Operations

Types:

```python
from robert_test_24.types.beta.tuned_models import ListOperations
```

Methods:

- <code title="get /v1beta/tunedModels/{tunedModel}/operations">client.beta.tuned_models.operations.<a href="./src/robert_test_24/resources/beta/tuned_models/operations.py">list_operations</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_models/operation_list_operations_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/tuned_models/list_operations.py">ListOperations</a></code>
- <code title="get /v1beta/tunedModels/{tunedModel}/operations/{operation}">client.beta.tuned_models.operations.<a href="./src/robert_test_24/resources/beta/tuned_models/operations.py">retrieve_operation</a>(operation, \*, tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_models/operation_retrieve_operation_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/operation.py">Operation</a></code>

### Permissions

Methods:

- <code title="post /v1beta/tunedModels/{tunedModel}/permissions">client.beta.tuned_models.permissions.<a href="./src/robert_test_24/resources/beta/tuned_models/permissions.py">create_permission</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_models/permission_create_permission_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/permission.py">Permission</a></code>
- <code title="delete /v1beta/tunedModels/{tunedModel}/permissions/{permission}">client.beta.tuned_models.permissions.<a href="./src/robert_test_24/resources/beta/tuned_models/permissions.py">delete_permission</a>(permission, \*, tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_models/permission_delete_permission_params.py">params</a>) -> object</code>
- <code title="get /v1beta/tunedModels/{tunedModel}/permissions">client.beta.tuned_models.permissions.<a href="./src/robert_test_24/resources/beta/tuned_models/permissions.py">list_permissions</a>(tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_models/permission_list_permissions_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/list_permissions.py">ListPermissions</a></code>
- <code title="get /v1beta/tunedModels/{tunedModel}/permissions/{permission}">client.beta.tuned_models.permissions.<a href="./src/robert_test_24/resources/beta/tuned_models/permissions.py">retrieve_permission</a>(permission, \*, tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_models/permission_retrieve_permission_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/permission.py">Permission</a></code>
- <code title="patch /v1beta/tunedModels/{tunedModel}/permissions/{permission}">client.beta.tuned_models.permissions.<a href="./src/robert_test_24/resources/beta/tuned_models/permissions.py">update_permission</a>(permission, \*, tuned_model, \*\*<a href="src/robert_test_24/types/beta/tuned_models/permission_update_permission_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/permission.py">Permission</a></code>

## Corpora

Types:

```python
from robert_test_24.types.beta import (
    Corpus,
    MetadataFilter,
    RelevantChunk,
    CorporaListResponse,
    CorporaCorpusQueryResponse,
)
```

Methods:

- <code title="post /v1beta/corpora">client.beta.corpora.<a href="./src/robert_test_24/resources/beta/corpora/corpora.py">create</a>(\*\*<a href="src/robert_test_24/types/beta/corpora_create_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpus.py">Corpus</a></code>
- <code title="get /v1beta/corpora/{corpus}/operations/{operation}">client.beta.corpora.<a href="./src/robert_test_24/resources/beta/corpora/corpora.py">retrieve</a>(operation, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/operation.py">Operation</a></code>
- <code title="patch /v1beta/corpora/{corpus}">client.beta.corpora.<a href="./src/robert_test_24/resources/beta/corpora/corpora.py">update</a>(corpus, \*\*<a href="src/robert_test_24/types/beta/corpora_update_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpus.py">Corpus</a></code>
- <code title="get /v1beta/corpora">client.beta.corpora.<a href="./src/robert_test_24/resources/beta/corpora/corpora.py">list</a>(\*\*<a href="src/robert_test_24/types/beta/corpora_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora_list_response.py">CorporaListResponse</a></code>
- <code title="delete /v1beta/corpora/{corpus}">client.beta.corpora.<a href="./src/robert_test_24/resources/beta/corpora/corpora.py">delete</a>(corpus, \*\*<a href="src/robert_test_24/types/beta/corpora_delete_params.py">params</a>) -> object</code>
- <code title="post /v1beta/corpora/{corpus}:query">client.beta.corpora.<a href="./src/robert_test_24/resources/beta/corpora/corpora.py">corpus_query</a>(corpus, \*\*<a href="src/robert_test_24/types/beta/corpora_corpus_query_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora_corpus_query_response.py">CorporaCorpusQueryResponse</a></code>

### Permissions

Types:

```python
from robert_test_24.types.beta.corpora import ListPermissions, Permission
```

Methods:

- <code title="post /v1beta/corpora/{corpus}/permissions">client.beta.corpora.permissions.<a href="./src/robert_test_24/resources/beta/corpora/permissions.py">create</a>(corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/permission_create_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/permission.py">Permission</a></code>
- <code title="get /v1beta/corpora/{corpus}/permissions/{permission}">client.beta.corpora.permissions.<a href="./src/robert_test_24/resources/beta/corpora/permissions.py">retrieve</a>(permission, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/permission_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/permission.py">Permission</a></code>
- <code title="patch /v1beta/corpora/{corpus}/permissions/{permission}">client.beta.corpora.permissions.<a href="./src/robert_test_24/resources/beta/corpora/permissions.py">update</a>(permission, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/permission_update_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/permission.py">Permission</a></code>
- <code title="get /v1beta/corpora/{corpus}/permissions">client.beta.corpora.permissions.<a href="./src/robert_test_24/resources/beta/corpora/permissions.py">list</a>(corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/permission_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/list_permissions.py">ListPermissions</a></code>
- <code title="delete /v1beta/corpora/{corpus}/permissions/{permission}">client.beta.corpora.permissions.<a href="./src/robert_test_24/resources/beta/corpora/permissions.py">delete</a>(permission, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/permission_delete_params.py">params</a>) -> object</code>

### Documents

Types:

```python
from robert_test_24.types.beta.corpora import (
    DocumentChunksBatchCreateResponse,
    DocumentChunksBatchUpdateResponse,
)
```

Methods:

- <code title="patch /v1beta/corpora/{corpus}/documents/{document}">client.beta.corpora.documents.<a href="./src/robert_test_24/resources/beta/corpora/documents/documents.py">update</a>(document, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/document_update_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/rag_stores/document.py">Document</a></code>
- <code title="post /v1beta/corpora/{corpus}/documents/{document}/chunks:batchCreate">client.beta.corpora.documents.<a href="./src/robert_test_24/resources/beta/corpora/documents/documents.py">chunks_batch_create</a>(document, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/document_chunks_batch_create_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/document_chunks_batch_create_response.py">DocumentChunksBatchCreateResponse</a></code>
- <code title="post /v1beta/corpora/{corpus}/documents/{document}/chunks:batchDelete">client.beta.corpora.documents.<a href="./src/robert_test_24/resources/beta/corpora/documents/documents.py">chunks_batch_delete</a>(document, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/document_chunks_batch_delete_params.py">params</a>) -> object</code>
- <code title="post /v1beta/corpora/{corpus}/documents/{document}/chunks:batchUpdate">client.beta.corpora.documents.<a href="./src/robert_test_24/resources/beta/corpora/documents/documents.py">chunks_batch_update</a>(document, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/document_chunks_batch_update_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/document_chunks_batch_update_response.py">DocumentChunksBatchUpdateResponse</a></code>

#### Chunks

Types:

```python
from robert_test_24.types.beta.corpora.documents import Chunk, ChunkListResponse
```

Methods:

- <code title="post /v1beta/corpora/{corpus}/documents/{document}/chunks">client.beta.corpora.documents.chunks.<a href="./src/robert_test_24/resources/beta/corpora/documents/chunks.py">create</a>(document, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/documents/chunk_create_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/documents/chunk.py">Chunk</a></code>
- <code title="get /v1beta/corpora/{corpus}/documents/{document}/chunks/{chunk}">client.beta.corpora.documents.chunks.<a href="./src/robert_test_24/resources/beta/corpora/documents/chunks.py">retrieve</a>(chunk, \*, corpus, document, \*\*<a href="src/robert_test_24/types/beta/corpora/documents/chunk_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/documents/chunk.py">Chunk</a></code>
- <code title="patch /v1beta/corpora/{corpus}/documents/{document}/chunks/{chunk}">client.beta.corpora.documents.chunks.<a href="./src/robert_test_24/resources/beta/corpora/documents/chunks.py">update</a>(chunk, \*, corpus, document, \*\*<a href="src/robert_test_24/types/beta/corpora/documents/chunk_update_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/documents/chunk.py">Chunk</a></code>
- <code title="get /v1beta/corpora/{corpus}/documents/{document}/chunks">client.beta.corpora.documents.chunks.<a href="./src/robert_test_24/resources/beta/corpora/documents/chunks.py">list</a>(document, \*, corpus, \*\*<a href="src/robert_test_24/types/beta/corpora/documents/chunk_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/corpora/documents/chunk_list_response.py">ChunkListResponse</a></code>
- <code title="delete /v1beta/corpora/{corpus}/documents/{document}/chunks/{chunk}">client.beta.corpora.documents.chunks.<a href="./src/robert_test_24/resources/beta/corpora/documents/chunks.py">delete</a>(chunk, \*, corpus, document, \*\*<a href="src/robert_test_24/types/beta/corpora/documents/chunk_delete_params.py">params</a>) -> object</code>

## GeneratedFiles

Types:

```python
from robert_test_24.types.beta import GeneratedFile, GeneratedFileRetrieveGeneratedFilesResponse
```

Methods:

- <code title="get /v1beta/generatedFiles/{generatedFile}">client.beta.generated_files.<a href="./src/robert_test_24/resources/beta/generated_files.py">retrieve</a>(generated_file, \*\*<a href="src/robert_test_24/types/beta/generated_file_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generated_file.py">GeneratedFile</a></code>
- <code title="get /v1beta/generatedFiles">client.beta.generated_files.<a href="./src/robert_test_24/resources/beta/generated_files.py">retrieve_generated_files</a>(\*\*<a href="src/robert_test_24/types/beta/generated_file_retrieve_generated_files_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generated_file_retrieve_generated_files_response.py">GeneratedFileRetrieveGeneratedFilesResponse</a></code>

## Files

Types:

```python
from robert_test_24.types.beta import File, Status, FileCreateResponse, FileListResponse
```

Methods:

- <code title="post /v1beta/files">client.beta.files.<a href="./src/robert_test_24/resources/beta/files.py">create</a>(\*\*<a href="src/robert_test_24/types/beta/file_create_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/file_create_response.py">FileCreateResponse</a></code>
- <code title="get /v1beta/files/{file}">client.beta.files.<a href="./src/robert_test_24/resources/beta/files.py">retrieve</a>(file, \*\*<a href="src/robert_test_24/types/beta/file_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/file.py">File</a></code>
- <code title="get /v1beta/files">client.beta.files.<a href="./src/robert_test_24/resources/beta/files.py">list</a>(\*\*<a href="src/robert_test_24/types/beta/file_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/file_list_response.py">FileListResponse</a></code>
- <code title="delete /v1beta/files/{file}">client.beta.files.<a href="./src/robert_test_24/resources/beta/files.py">delete</a>(file, \*\*<a href="src/robert_test_24/types/beta/file_delete_params.py">params</a>) -> object</code>
- <code title="get /v1beta/files/{file}:download">client.beta.files.<a href="./src/robert_test_24/resources/beta/files.py">retrieve_file_download</a>(file, \*\*<a href="src/robert_test_24/types/beta/file_retrieve_file_download_params.py">params</a>) -> object</code>

## Batches

Types:

```python
from robert_test_24.types.beta import (
    BatchState,
    EmbedContentBatch,
    EmbedContentBatchOutput,
    GenerateContentBatch,
    GenerateContentBatchOutput,
)
```

Methods:

- <code title="get /v1beta/batches/{generateContentBatch}">client.beta.batches.<a href="./src/robert_test_24/resources/beta/batches.py">retrieve</a>(generate_content_batch, \*\*<a href="src/robert_test_24/types/beta/batch_retrieve_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/operation.py">Operation</a></code>
- <code title="get /v1beta/batches">client.beta.batches.<a href="./src/robert_test_24/resources/beta/batches.py">list</a>(\*\*<a href="src/robert_test_24/types/beta/batch_list_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/tuned_models/list_operations.py">ListOperations</a></code>
- <code title="delete /v1beta/batches/{generateContentBatch}">client.beta.batches.<a href="./src/robert_test_24/resources/beta/batches.py">delete</a>(generate_content_batch, \*\*<a href="src/robert_test_24/types/beta/batch_delete_params.py">params</a>) -> object</code>
- <code title="post /v1beta/batches/{generateContentBatch}:cancel">client.beta.batches.<a href="./src/robert_test_24/resources/beta/batches.py">generate_content_batch_cancel</a>(generate_content_batch, \*\*<a href="src/robert_test_24/types/beta/batch_generate_content_batch_cancel_params.py">params</a>) -> object</code>
- <code title="patch /v1beta/batches/{generateContentBatch}:updateEmbedContentBatch">client.beta.batches.<a href="./src/robert_test_24/resources/beta/batches.py">update_generate_content_batch_update_embed_content_batch</a>(generate_content_batch, \*\*<a href="src/robert_test_24/types/beta/batch_update_generate_content_batch_update_embed_content_batch_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/embed_content_batch.py">EmbedContentBatch</a></code>
- <code title="patch /v1beta/batches/{generateContentBatch}:updateGenerateContentBatch">client.beta.batches.<a href="./src/robert_test_24/resources/beta/batches.py">update_generate_content_batch_update_generate_content_batch</a>(generate_content_batch, \*\*<a href="src/robert_test_24/types/beta/batch_update_generate_content_batch_update_generate_content_batch_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generate_content_batch.py">GenerateContentBatch</a></code>

## Dynamic

Methods:

- <code title="post /v1beta/dynamic/{dynamicId}:generateContent">client.beta.dynamic.<a href="./src/robert_test_24/resources/beta/dynamic.py">dynamic_id_generate_content</a>(dynamic_id, \*\*<a href="src/robert_test_24/types/beta/dynamic_dynamic_id_generate_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generate_content_response.py">GenerateContentResponse</a></code>
- <code title="post /v1beta/dynamic/{dynamicId}:streamGenerateContent">client.beta.dynamic.<a href="./src/robert_test_24/resources/beta/dynamic.py">dynamic_id_stream_generate_content</a>(dynamic_id, \*\*<a href="src/robert_test_24/types/beta/dynamic_dynamic_id_stream_generate_content_params.py">params</a>) -> <a href="./src/robert_test_24/types/beta/generate_content_response.py">GenerateContentResponse</a></code>
