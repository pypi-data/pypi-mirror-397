# flake8: noqa: E402 — we want to use deprecation warning before import due to possible import errors

__all__ = [
    'DEFAULT_AMP_OPTIMIZE', 'DEFAULT_ASYNC_REQUESTS_SIZE', 'DEFAULT_CPU_BATCH_SIZE', 'DEFAULT_GPU_BATCH_SIZE',
    'DEFAULT_GPU_OOM_TIMEOUT', 'DEFAULT_GPU_UTILIZATION_LIMIT', 'DEFAULT_GPU_OOM_REPEAT_LIMIT', 'DEFAULT_MAX_LENGTH',
    'get_bert_example_length', 'get_bert_max_word_subtokens', 'get_amp_optimize', 'get_async_requests_size',
    'get_cpu_batch_size', 'get_gpu_batch_size', 'get_gpu_oom_timeout', 'get_gpu_utilization_limit',
    'get_gpu_oom_repeat_limit', 'get_max_length'
]

import warnings

warnings.warn(
    f"`{__name__}` module was moved to `tie_ml_utils.env`",
    DeprecationWarning,
    stacklevel=2
)

from tie_ml_utils.env import DEFAULT_AMP_OPTIMIZE, DEFAULT_ASYNC_REQUESTS_SIZE, DEFAULT_CPU_BATCH_SIZE, DEFAULT_GPU_BATCH_SIZE, \
    DEFAULT_GPU_OOM_REPEAT_LIMIT, DEFAULT_GPU_OOM_TIMEOUT, DEFAULT_GPU_UTILIZATION_LIMIT, DEFAULT_MAX_LENGTH, get_amp_optimize, \
    get_async_requests_size, get_bert_example_length, get_bert_max_word_subtokens, get_cpu_batch_size, get_gpu_batch_size, \
    get_gpu_oom_repeat_limit, get_gpu_oom_timeout, get_gpu_utilization_limit, get_max_length
