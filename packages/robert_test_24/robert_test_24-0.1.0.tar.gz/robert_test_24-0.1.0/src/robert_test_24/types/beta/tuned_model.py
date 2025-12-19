# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .tuning_snapshot import TuningSnapshot

__all__ = [
    "TunedModel",
    "TuningTask",
    "TuningTaskTrainingData",
    "TuningTaskTrainingDataExamples",
    "TuningTaskTrainingDataExamplesExample",
    "TuningTaskHyperparameters",
    "TunedModelSource",
]


class TuningTaskTrainingDataExamplesExample(BaseModel):
    """A single example for tuning."""

    output: str
    """Required. The expected model output."""

    text_input: Optional[str] = FieldInfo(alias="textInput", default=None)
    """Optional. Text model input."""


class TuningTaskTrainingDataExamples(BaseModel):
    """A set of tuning examples. Can be training or validation data."""

    examples: Optional[List[TuningTaskTrainingDataExamplesExample]] = None
    """The examples.

    Example input can be for text or discuss, but all examples in a set must be of
    the same type.
    """


class TuningTaskTrainingData(BaseModel):
    """Dataset for training or validation."""

    examples: Optional[TuningTaskTrainingDataExamples] = None
    """A set of tuning examples. Can be training or validation data."""


class TuningTaskHyperparameters(BaseModel):
    """Hyperparameters controlling the tuning process.

    Read more at
    https://ai.google.dev/docs/model_tuning_guidance
    """

    batch_size: Optional[int] = FieldInfo(alias="batchSize", default=None)
    """Immutable.

    The batch size hyperparameter for tuning. If not set, a default of 4 or 16 will
    be used based on the number of training examples.
    """

    epoch_count: Optional[int] = FieldInfo(alias="epochCount", default=None)
    """Immutable.

    The number of training epochs. An epoch is one pass through the training data.
    If not set, a default of 5 will be used.
    """

    learning_rate: Optional[float] = FieldInfo(alias="learningRate", default=None)
    """Optional.

    Immutable. The learning rate hyperparameter for tuning. If not set, a default of
    0.001 or 0.0002 will be calculated based on the number of training examples.
    """

    learning_rate_multiplier: Optional[float] = FieldInfo(alias="learningRateMultiplier", default=None)
    """Optional.

    Immutable. The learning rate multiplier is used to calculate a final
    learning_rate based on the default (recommended) value. Actual learning rate :=
    learning_rate_multiplier \\** default learning rate Default learning rate is
    dependent on base model and dataset size. If not set, a default of 1.0 will be
    used.
    """


class TuningTask(BaseModel):
    """Tuning tasks that create tuned models."""

    complete_time: Optional[datetime] = FieldInfo(alias="completeTime", default=None)
    """Output only. The timestamp when tuning this model completed."""

    hyperparameters: Optional[TuningTaskHyperparameters] = None
    """Hyperparameters controlling the tuning process.

    Read more at https://ai.google.dev/docs/model_tuning_guidance
    """

    snapshots: Optional[List[TuningSnapshot]] = None
    """Output only. Metrics collected during tuning."""

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)
    """Output only. The timestamp when tuning this model started."""


class TunedModelSource(BaseModel):
    """Tuned model as a source for training a new model."""

    base_model: Optional[str] = FieldInfo(alias="baseModel", default=None)
    """Output only.

    The name of the base `Model` this `TunedModel` was tuned from. Example:
    `models/gemini-1.5-flash-001`
    """

    tuned_model: Optional[str] = FieldInfo(alias="tunedModel", default=None)
    """Immutable.

    The name of the `TunedModel` to use as the starting point for training the new
    model. Example: `tunedModels/my-tuned-model`
    """


class TunedModel(BaseModel):
    """A fine-tuned model created using ModelService.CreateTunedModel."""

    tuning_task: TuningTask = FieldInfo(alias="tuningTask")
    """Tuning tasks that create tuned models."""

    base_model: Optional[str] = FieldInfo(alias="baseModel", default=None)
    """Immutable.

    The name of the `Model` to tune. Example: `models/gemini-1.5-flash-001`
    """

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Output only. The timestamp when this model was created."""

    description: Optional[str] = None
    """Optional. A short description of this model."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Optional.

    The name to display for this model in user interfaces. The display name must be
    up to 40 characters including spaces.
    """

    name: Optional[str] = None
    """Output only.

    The tuned model name. A unique name will be generated on create. Example:
    `tunedModels/az2mb0bpw6i` If display_name is set on create, the id portion of
    the name will be set by concatenating the words of the display_name with hyphens
    and adding a random portion for uniqueness.

    Example:

    - display_name = `Sentence Translator`
    - name = `tunedModels/sentence-translator-u3b7m`
    """

    reader_project_numbers: Optional[List[str]] = FieldInfo(alias="readerProjectNumbers", default=None)
    """Optional. List of project numbers that have read access to the tuned model."""

    state: Optional[Literal["STATE_UNSPECIFIED", "CREATING", "ACTIVE", "FAILED"]] = None
    """Output only. The state of the tuned model."""

    temperature: Optional[float] = None
    """Optional. Controls the randomness of the output.

    Values can range over `[0.0,1.0]`, inclusive. A value closer to `1.0` will
    produce responses that are more varied, while a value closer to `0.0` will
    typically result in less surprising responses from the model.

    This value specifies default to be the one used by the base model while creating
    the model.
    """

    top_k: Optional[int] = FieldInfo(alias="topK", default=None)
    """Optional. For Top-k sampling.

    Top-k sampling considers the set of `top_k` most probable tokens. This value
    specifies default to be used by the backend while making the call to the model.

    This value specifies default to be the one used by the base model while creating
    the model.
    """

    top_p: Optional[float] = FieldInfo(alias="topP", default=None)
    """Optional. For Nucleus sampling.

    Nucleus sampling considers the smallest set of tokens whose probability sum is
    at least `top_p`.

    This value specifies default to be the one used by the base model while creating
    the model.
    """

    tuned_model_source: Optional[TunedModelSource] = FieldInfo(alias="tunedModelSource", default=None)
    """Tuned model as a source for training a new model."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """Output only. The timestamp when this model was updated."""
