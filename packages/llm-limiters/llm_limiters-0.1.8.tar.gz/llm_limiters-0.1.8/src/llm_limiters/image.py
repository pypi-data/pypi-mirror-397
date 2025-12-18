# image_rate_limiter.py

import time
from collections import deque
from threading import Lock
from typing import Dict
from .constants import GEMINI_IMAGE_LIMITS, OPENAI_IMAGE_LIMITS
from .core import RateLimitExceededError, ModelNotFoundError


class ImageRateLimiter:
    def __init__(self, tier="tier1", custom_limits=None):
        if tier not in GEMINI_IMAGE_LIMITS and tier not in OPENAI_IMAGE_LIMITS:
            raise ValueError(f"Unknown tier '{tier}'")

        self.tier = tier

        self.limits = {
            **GEMINI_IMAGE_LIMITS.get(tier, {}),
            **OPENAI_IMAGE_LIMITS.get(tier, {}),
            **(custom_limits or {})
        }

        self._lock = Lock()
        self.request_logs = {m: deque() for m in self.limits}
        self.token_logs = {m: deque() for m in self.limits}
        self.model_cooldowns = {}

    def _prune(self, model: str, now: float):
        while self.request_logs[model] and now - self.request_logs[model][0] > 60:
            self.request_logs[model].popleft()
        while self.token_logs[model] and now - self.token_logs[model][0][0] > 60:
            self.token_logs[model].popleft()

    def _check(self, model: str):
        if model not in self.limits:
            raise ModelNotFoundError(model)

        with self._lock:
            now = time.time()
            self._prune(model, now)

            cfg = self.limits[model]

            # RPM
            if len(self.request_logs[model]) >= cfg["rpm"]:
                return False

            # TPM (OpenAI images)
            if cfg.get("tpm", 0) > 0:
                used_tokens = sum(t for _, t in self.token_logs[model])
                if used_tokens >= cfg["tpm"]:
                    return False

            # RPD (Gemini images)
            if cfg.get("rpd", 0) > 0:
                day_ago = now - 86400
                if sum(1 for ts in self.request_logs[model] if ts > day_ago) >= cfg["rpd"]:
                    return False

            return True


    def limit(self, model_priority):
        def decorator(fn):
            def wrapper(*args, **kwargs):
                now = time.time()

                for model in model_priority:

                    if model in self.model_cooldowns and now < self.model_cooldowns[model]:
                        continue

                    if not self._check(model):
                        continue

                    try:
                        kwargs["model_name"] = model
                        resp = fn(*args, **kwargs)

                        self.request_logs[model].append(now)
                        self.token_logs[model].append((now, 0))
                        return resp

                    except Exception as e:
                        msg = str(e)
                        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                            self.model_cooldowns[model] = time.time() + 30
                            continue
                        raise

                raise RateLimitExceededError("All image models exhausted")

            return wrapper
        return decorator
