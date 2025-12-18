from dataclasses import dataclass

from vllm.outputs import CompletionOutput as BaseCompletionOutput
from vllm.v1.outputs import (
    SamplerOutput as BaseSamplerOutput,
    LogprobsLists,
    LogprobsTensors,
    ModelRunnerOutput as BaseModelRunnerOutput,
)
from vllm.logprobs import SampleLogprobs
from vllm.v1.engine import (
    EngineCoreOutput as BaseEngineCoreOutput,
    EngineCoreOutputs as BaseEngineCoreOutputs,
)


@dataclass
class CompletionOutput(BaseCompletionOutput):
  power_logprobs: list[SampleLogprobs] | None = None


@dataclass
class SamplerOutput(BaseSamplerOutput):
  power_logprobs_tensors: LogprobsTensors | None


@dataclass
class ModelRunnerOutput(BaseModelRunnerOutput):
  power_logprobs: LogprobsLists | None = None


class EngineCoreOutput(BaseEngineCoreOutput):
  new_power_logprobs: LogprobsLists | None = None


class EngineCoreOutputs(BaseEngineCoreOutputs):
  outputs: list[EngineCoreOutput] = []


EMPTY_MODEL_RUNNER_OUTPUT = ModelRunnerOutput(
    req_ids=[],
    req_id_to_index={},
    sampled_token_ids=[],
    logprobs=None,
    power_logprobs=None,
    prompt_logprobs_dict={},
    pooler_output=[],
    num_nans_in_logits=None,
)
