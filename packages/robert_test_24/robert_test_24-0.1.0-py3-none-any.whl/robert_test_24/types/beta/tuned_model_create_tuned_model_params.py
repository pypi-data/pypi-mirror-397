# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = [
    "TunedModelCreateTunedModelParams",
    "TuningTask",
    "TuningTaskTrainingData",
    "TuningTaskTrainingDataExamples",
    "TuningTaskTrainingDataExamplesExample",
    "TuningTaskHyperparameters",
    "api_empty",
    "TunedModelSource",
]


class TunedModelCreateTunedModelParams(TypedDict, total=False):
    tuning_task: Required[Annotated[TuningTask, PropertyInfo(alias="tuningTask")]]
    """Tuning tasks that create tuned models."""

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    tuned_model_id: Annotated[str, PropertyInfo(alias="tunedModelId")]
    """Optional.

    The unique id for the tuned model if specified. This value should be up to 40
    characters, the first character must be a letter, the last could be a letter or
    a number. The id must match the regular expression:
    `[a-z]([a-z0-9-]{0,38}[a-z0-9])?`.
    """

    base_model: Annotated[str, PropertyInfo(alias="baseModel")]
    """Immutable.

    The name of the `Model` to tune. Example: `models/gemini-1.5-flash-001`
    """

    description: str
    """Optional. A short description of this model."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Optional.

    The name to display for this model in user interfaces. The display name must be
    up to 40 characters including spaces.
    """

    reader_project_numbers: Annotated[SequenceNotStr[str], PropertyInfo(alias="readerProjectNumbers")]
    """Optional. List of project numbers that have read access to the tuned model."""

    temperature: float
    """Optional. Controls the randomness of the output.

    Values can range over `[0.0,1.0]`, inclusive. A value closer to `1.0` will
    produce responses that are more varied, while a value closer to `0.0` will
    typically result in less surprising responses from the model.

    This value specifies default to be the one used by the base model while creating
    the model.
    """

    top_k: Annotated[int, PropertyInfo(alias="topK")]
    """Optional. For Top-k sampling.

    Top-k sampling considers the set of `top_k` most probable tokens. This value
    specifies default to be used by the backend while making the call to the model.

    This value specifies default to be the one used by the base model while creating
    the model.
    """

    top_p: Annotated[float, PropertyInfo(alias="topP")]
    """Optional. For Nucleus sampling.

    Nucleus sampling considers the smallest set of tokens whose probability sum is
    at least `top_p`.

    This value specifies default to be the one used by the base model while creating
    the model.
    """

    tuned_model_source: Annotated[TunedModelSource, PropertyInfo(alias="tunedModelSource")]
    """Tuned model as a source for training a new model."""


class TuningTaskTrainingDataExamplesExample(TypedDict, total=False):
    """A single example for tuning."""

    output: Required[str]
    """Required. The expected model output."""

    text_input: Annotated[str, PropertyInfo(alias="textInput")]
    """Optional. Text model input."""


class TuningTaskTrainingDataExamples(TypedDict, total=False):
    """A set of tuning examples. Can be training or validation data."""

    examples: Iterable[TuningTaskTrainingDataExamplesExample]
    """The examples.

    Example input can be for text or discuss, but all examples in a set must be of
    the same type.
    """


class TuningTaskTrainingData(TypedDict, total=False):
    """Dataset for training or validation."""

    examples: TuningTaskTrainingDataExamples
    """A set of tuning examples. Can be training or validation data."""


class TuningTaskHyperparameters(TypedDict, total=False):
    """Hyperparameters controlling the tuning process.

    Read more at
    https://ai.google.dev/docs/model_tuning_guidance
    """

    batch_size: Annotated[int, PropertyInfo(alias="batchSize")]
    """Immutable.

    The batch size hyperparameter for tuning. If not set, a default of 4 or 16 will
    be used based on the number of training examples.
    """

    epoch_count: Annotated[int, PropertyInfo(alias="epochCount")]
    """Immutable.

    The number of training epochs. An epoch is one pass through the training data.
    If not set, a default of 5 will be used.
    """

    learning_rate: Annotated[float, PropertyInfo(alias="learningRate")]
    """Optional.

    Immutable. The learning rate hyperparameter for tuning. If not set, a default of
    0.001 or 0.0002 will be calculated based on the number of training examples.
    """

    learning_rate_multiplier: Annotated[float, PropertyInfo(alias="learningRateMultiplier")]
    """Optional.

    Immutable. The learning rate multiplier is used to calculate a final
    learning_rate based on the default (recommended) value. Actual learning rate :=
    learning_rate_multiplier \\** default learning rate Default learning rate is
    dependent on base model and dataset size. If not set, a default of 1.0 will be
    used.
    """


class TuningTask(TypedDict, total=False):
    """Tuning tasks that create tuned models."""

    training_data: Required[Annotated[TuningTaskTrainingData, PropertyInfo(alias="trainingData")]]
    """Dataset for training or validation."""

    hyperparameters: TuningTaskHyperparameters
    """Hyperparameters controlling the tuning process.

    Read more at https://ai.google.dev/docs/model_tuning_guidance
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""


class TunedModelSource(TypedDict, total=False):
    """Tuned model as a source for training a new model."""

    tuned_model: Annotated[str, PropertyInfo(alias="tunedModel")]
    """Immutable.

    The name of the `TunedModel` to use as the starting point for training the new
    model. Example: `tunedModels/my-tuned-model`
    """
