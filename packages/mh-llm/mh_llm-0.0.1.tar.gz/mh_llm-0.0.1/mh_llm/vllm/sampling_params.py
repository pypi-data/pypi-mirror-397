from vllm.sampling_params import SamplingParams as BaseSamplingParams

from .utils import patch as mh_patch


class SamplingParams(BaseSamplingParams):
  """Sampling parameters with MH LLM extensions.

  Extends vLLM's SamplingParams to add MH LLM specific parameters.
  """

  alpha: float = 1.0
  """Controls the sharpening of the power distribution."""

  @staticmethod
  def from_optional(
      alpha: float | None = None,
      **kwargs,
  ) -> "SamplingParams":
    """Create SamplingParams from optional parameters.

    Args:
      alpha: Controls the sharpening of the power distribution.
      **kwargs: Other SamplingParams parameters.
    """
    if alpha is not None:
      kwargs["alpha"] = alpha

    with mh_patch({'module': 'vllm.sampling_params', 'class': SamplingParams}):
      params = SamplingParams.from_optional(**kwargs)

    params.alpha = alpha = 1.0 if alpha is None else alpha
    return params

  def _verify_args(self) -> None:
    """Verify the arguments."""
    super()._verify_args()
    if self.alpha < 0.0:
      raise ValueError(f'alpha must be >= 0.0, got {self.alpha}')

  def __repr__(self) -> str:
    return (f"SamplingParams(n={self.n}, "
            f"presence_penalty={self.presence_penalty}, "
            f"frequency_penalty={self.frequency_penalty}, "
            f"repetition_penalty={self.repetition_penalty}, "
            f"temperature={self.temperature}, "
            f"alpha={self.alpha}, "
            f"top_p={self.top_p}, "
            f"top_k={self.top_k}, "
            f"min_p={self.min_p}, "
            f"seed={self.seed}, "
            f"stop={self.stop}, "
            f"stop_token_ids={self.stop_token_ids}, "
            f"bad_words={self.bad_words}, "
            f"include_stop_str_in_output={self.include_stop_str_in_output}, "
            f"ignore_eos={self.ignore_eos}, "
            f"max_tokens={self.max_tokens}, "
            f"min_tokens={self.min_tokens}, "
            f"logprobs={self.logprobs}, "
            f"prompt_logprobs={self.prompt_logprobs}, "
            f"skip_special_tokens={self.skip_special_tokens}, "
            "spaces_between_special_tokens="
            f"{self.spaces_between_special_tokens}, "
            f"truncate_prompt_tokens={self.truncate_prompt_tokens}, "
            f"structured_outputs={self.structured_outputs}, "
            f"extra_args={self.extra_args})")
