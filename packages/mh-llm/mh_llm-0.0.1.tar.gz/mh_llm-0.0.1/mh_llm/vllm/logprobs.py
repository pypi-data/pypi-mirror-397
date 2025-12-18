import itertools
from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial

from vllm.logger import init_logger
from vllm.logprobs import SampleLogprobs
from vllm.transformers_utils.detokenizer_utils import (
    AnyTokenizer,
    convert_ids_list_to_tokens,
)
from vllm.v1.engine import EngineCoreRequest
from vllm.v1.outputs import LogprobsLists

from vllm.v1.engine.logprobs import LogprobsProcessor as BaseLogprobsProcessor

from .outputs import EngineCoreOutput

logger = init_logger(__name__)

NONES = itertools.repeat(None)


@dataclass
class LogprobsProcessor(BaseLogprobsProcessor):
  power_logprobs: SampleLogprobs | None = None

  @classmethod
  def from_new_request(
      cls,
      tokenizer: AnyTokenizer | None,
      request: EngineCoreRequest,
  ) -> "LogprobsProcessor":
    num_logprobs = request.sampling_params.logprobs
    cls = partial(
        cls,
        power_logprobs=(None if num_logprobs is None else []),
    )
    return BaseLogprobsProcessor.from_new_request.__func__(
        cls,
        tokenizer,
        request,
    )

  def _update_sample_logprobs(
      self,
      logprobs_lists: LogprobsLists,
      power_logprobs_lists: LogprobsLists,
  ) -> None:
    """Update with sample logprobs from EngineCore.

    Outer lists are only of len > 1 if EngineCore made
    >1 tokens in prior step (e.g. in spec decoding).

    Args:
      logprobs_lists: the lists of logprob tokens, logprobs, and ranks.
      power_logprobs_lists: the lists of power logprob tokens, logprobs, and ranks.

    """

    assert self.num_logprobs is not None
    assert self.logprobs is not None
    assert self.cumulative_logprob is not None

    token_ids_lst, logprobs_lst, ranks_lst = logprobs_lists
    _, power_logprobs_lst, _ = power_logprobs_lists

    for rank, logprobs, power_logprobs, token_ids in zip(
        ranks_lst,
        logprobs_lst,
        power_logprobs_lst,
        token_ids_lst,
    ):
      # Detokenize (non-incrementally).
      decoded_tokens = NONES if self.tokenizer is None else convert_ids_list_to_tokens(
          self.tokenizer,
          token_ids,
      )

      # Sampler puts the sampled logprob in first.
      sampled_token_logprob = logprobs[0]
      self.cumulative_logprob += sampled_token_logprob

      # Update with the Logprob dictionary for this pos.
      self.logprobs.append(
          self._make_logprob_dict(
              logprobs,
              token_ids,
              decoded_tokens,
              rank,
              self.num_logprobs,
          ))
      self.power_logprobs.append(
          self._make_logprob_dict(
              power_logprobs,
              token_ids,
              decoded_tokens,
              rank,
              self.num_logprobs,
          ))

  def update_from_output(self, output: EngineCoreOutput) -> None:
    if output.new_logprobs is not None:
      self._update_sample_logprobs(
          output.new_logprobs,
          output.new_power_logprobs,
      )
    if output.new_prompt_logprobs_tensors is not None:
      self._update_prompt_logprobs(output.new_prompt_logprobs_tensors)
