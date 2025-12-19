# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .mcqa_environment import McqaEnvironment
from .workbench_environment import WorkbenchEnvironment
from .comp_coding_environment import CompCodingEnvironment
from .library_judge_math_environment import LibraryJudgeMathEnvironment
from .multiverse_math_hard_environment import MultiverseMathHardEnvironment
from .instruction_following_environment import InstructionFollowingEnvironment

__all__ = ["GrpoParameters", "Environment"]

Environment: TypeAlias = Annotated[
    Union[
        McqaEnvironment,
        WorkbenchEnvironment,
        MultiverseMathHardEnvironment,
        LibraryJudgeMathEnvironment,
        InstructionFollowingEnvironment,
        CompCodingEnvironment,
    ],
    PropertyInfo(discriminator="name"),
]


class GrpoParameters(BaseModel):
    environment: Environment
    """
    Task specific environment configuration defining the training context including
    dataset specification and reward function.
    """

    generation_batch_size: Optional[int] = None
    """Batch size for generation during rollouts.

    Controls how many sequences are generated in parallel.
    """

    generation_pipeline_parallel_size: Optional[int] = None
    """
    Number of GPUs to use for pipeline parallelism during generation, splitting
    model layers across devices (inter-layer parallelism).
    """

    generation_temperature: Optional[float] = None
    """Sampling temperature for generation.

    Higher values (e.g., 1.0) increase randomness, lower values (e.g., 0.1) make
    output more deterministic. Temperature of 0 is equivalent to greedy sampling
    (always selecting the most likely token).
    """

    generation_top_k: Optional[int] = None
    """Top-k sampling parameter.

    Only the k most likely tokens are considered at each step. None means no top-k
    filtering is applied. Typically used with values like 50 to balance diversity
    and quality.
    """

    generation_top_p: Optional[float] = None
    """Nucleus sampling parameter (top-p).

    Only tokens with cumulative probability >= top_p are considered. 1.0 means no
    filtering; lower values (e.g., 0.9) increase quality by filtering unlikely
    tokens.
    """

    logprob_chunk_size: Optional[int] = None
    """Chunk size for processing logprobs in distributed settings.

    Larger values improve efficiency but require more memory. Used for chunked
    distributed operations during loss computation.
    """

    max_grad_norm: Optional[float] = None
    """Maximum gradient norm for gradient clipping during training.

    Prevents exploding gradients by scaling down gradients that exceed this
    threshold. Lower this value (e.g., 0.5) if you observe training instability, NaN
    losses, or erratic loss spikes. Increase it (e.g., 5.0) if training seems overly
    conservative or progress is too slow. Typical values range from 0.5 to 5.0.
    """

    normalize_rewards: Optional[bool] = None
    """
    Normalize advantages by dividing by their standard deviation across responses to
    each prompt. Default is True for improved training stability and consistent
    gradient magnitudes regardless of reward scale variations. This prevents prompts
    with high reward variance from dominating updates. Disable (False) only if: (1)
    rewards are already well-scaled and consistent, (2) you want to preserve reward
    magnitude information where higher-value tasks should have stronger learning
    signals, or (3) using very few generations per prompt (<4) where standard
    deviation estimates are noisy. Recommended: keep enabled for most use cases.
    """

    num_generations_per_prompt: Optional[int] = None
    """Number of responses to generate for each prompt.

    Used to compute the advantage baseline by comparing multiple responses to the
    same prompt. Higher values (e.g., 4-8) provide better advantage estimates but
    increase computational cost. Typical range: 4-16.
    """

    num_prompts_per_step: Optional[int] = None
    """Number of unique prompts to process per training step.

    This controls the batch size for sampling prompts from the dataset. Total
    samples per step = num_prompts_per_step \\** num_generations_per_prompt. Increase
    for better gradient estimates and training stability (at the cost of memory).
    Typical values: 8-64 depending on available GPU memory.
    """

    overlong_filtering: Optional[bool] = None
    """
    Exclude truncated sequences (those that hit max_total_sequence_length without
    producing end-of-text) from loss computation. Truncated samples still contribute
    to advantage baseline calculations but don't receive gradient updates. Enable
    (True) for long-form tasks like mathematical proofs or extended reasoning where
    correct answers may legitimately exceed length limits and shouldn't be penalized
    for incompleteness. Default is False to maintain standard GRPO behavior where
    the model learns to complete responses within sequence limits, which is
    appropriate for most tasks and production systems with length constraints.
    """

    ratio_clip_c: Optional[float] = None
    """
    Dual-clipping parameter that adds extra protection against large policy updates
    when rewards are negative. Must be greater than 1 (typically 3). Set to None to
    disable. This helps prevent the policy from changing too aggressively on
    poor-performing samples.
    """

    ratio_clip_max: Optional[float] = None
    """Upper bound for clipping the policy update ratio in GRPO loss.

    Limits how much the policy can change per update, preventing instability.
    Standard value: 0.2 (clips to [0.8, 1.2]). Usually set equal to ratio_clip_min
    (symmetric clipping), but can differ for asymmetric clipping strategies where
    you want to limit increases differently than decreases.
    """

    ratio_clip_min: Optional[float] = None
    """Lower bound for clipping the policy update ratio in GRPO loss.

    Limits how much the policy can change per update, preventing instability. The
    policy ratio is clipped to stay within [1-epsilon, 1+epsilon]. Standard value:
    0.2 (clips to [0.8, 1.2]). Lower values (e.g., 0.1) make training more
    conservative; higher values (e.g., 0.3) allow larger updates. Typically set
    equal to ratio_clip_max for symmetric clipping.
    """

    ref_policy_kl_penalty: Optional[float] = None
    """
    KL divergence penalty coefficient (β) that controls how strongly the trained
    policy is penalized for deviating from the reference policy. Higher values
    (e.g., 0.05-0.1) encourage the policy to stay closer to the reference (more
    conservative learning), while lower values (e.g., 0.001-0.01) allow more freedom
    to explore user-preferred behavior. Typical range: 0.001-0.1. Also known as
    'beta' in the original GRPO paper and 'kl_penalty_coefficient' in some
    implementations.
    """

    token_level_loss: Optional[bool] = None
    """Whether to compute loss at token level (True) or sequence level (False).

    Token-level averages over all tokens; sequence-level averages per-sequence
    losses. Sequence-level is used for GSPO-style training.
    """

    use_importance_sampling_correction: Optional[bool] = None
    """
    Correct for numerical differences between the inference backend (used for
    generation) and training framework (used for learning). This accounts for
    precision differences, backend variations, etc. that can cause the same model to
    produce slightly different probabilities. Recommended for async GRPO and when
    using FP8 inference.
    """

    use_on_policy_kl_approximation: Optional[bool] = None
    """
    Use importance-weighted KL divergence estimation between current and reference
    policies. This provides a more accurate, always-positive estimate of how much
    the policy has changed by accounting for the difference between the policy used
    for sampling and the current policy being trained. Enable when you need precise
    KL tracking. Default: False for efficiency.
    """

    use_rloo: Optional[bool] = None
    """
    Use leave-one-out baseline (Reinforcement, Leave One Out) for computing
    advantages. When True, each sample's baseline excludes its own reward, providing
    an unbiased estimate of expected reward. Default is True as it's theoretically
    correct and works well with typical num_generations_per_prompt values (4-8).
    Disable (False) for: (1) very few generations per prompt (≤3) where
    leave-one-out baselines become too noisy, (2) faster training by avoiding
    per-sample baseline computation, or (3) replicating original GRPO paper. The
    tradeoff: True gives unbiased but higher variance estimates; False gives biased
    but lower variance, which can improve stability with small generation counts.
    """
