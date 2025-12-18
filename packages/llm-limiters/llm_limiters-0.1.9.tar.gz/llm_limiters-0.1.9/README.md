
# llm-limiters

A lightweight, provider-aware rate-limiting library for **LLM text, image, and live (streaming) models**, supporting **Gemini and OpenAI** with tier-based quotas, fallbacks, and custom overrides.

Designed for:
- API gateways
- Backend services
- Agent systems
- Multi-model routing with hard quota enforcement

---

## Features

- Tier-based rate limiting (`free`, `tier1`, `tier2`, …)
- Gemini and OpenAI support
- Text, Image, and Live (WebSocket) limiters
- RPM / TPM / RPD enforcement
- Automatic cooldown on quota and 429 errors
- Model-priority fallback
- Custom per-model overrides
- Thread-safe (sync and async)

---

## Installation

```bash
pip install llm-limiters
```

## Quick Start

### Import

```python
from llm_limiters import RateLimiter, LiveRateLimiter, ImageRateLimiter
```

## Text Model Rate Limiting (Gemini + OpenAI)

### Create a limiter

```python
limiter = RateLimiter(tier="free")
```

### Use with model fallback

```python
@limiter.limit([
    "gemini-2.5-flash",
    "gpt-4o-mini"
])
def generate_text(prompt: str, model_name: str):
    return client.generate(
        model=model_name,
        prompt=prompt
    )
```

- Enforces RPM, TPM, and RPD
- Falls back to the next model when limits are reached
- Applies cooldowns automatically on rate-limit errors

## Image Generation Rate Limiting

### Supports

- Gemini Image / Imagen models
- OpenAI gpt-image-1, gpt-image-1-mini

> Image generation requires billing (no free tier).

### Create an image limiter

```python
image_limiter = ImageRateLimiter(tier="tier1")
```

### Use with priority routing

```python
@image_limiter.limit([
    "gpt-image-1-mini",
    "gpt-image-1",
    "gemini-2.5-flash-preview-image",
    "imagen-4.0-fast-generate"
])
def generate_image(prompt: str, model_name: str):
    if model_name.startswith("gpt-image"):
        return openai.images.generate(
            model=model_name,
            prompt=prompt
        )
    else:
        return gemini.images.generate(
            model=model_name,
            prompt=prompt
        )
```

- RPM enforced for all image models
- TPM enforced for OpenAI image models
- RPD enforced for Gemini / Imagen models
- Automatic cooldown on quota errors

## Audio / TTS Rate Limiting

Supports **OpenAI and Gemini audio models**, including text-to-speech and native audio generation.

### Supported Models

**OpenAI**
- `tts-1`
- `tts-1-hd`
- `gpt-4o-mini-tts`

**Gemini**
- `gemini-2.5-flash-native-audio`
- `gemini-2.5-flash-preview-tts`
- `gemini-2.5-pro-preview-tts`

### Create an audio limiter

```python
from llm_limiters.audio import AudioRateLimiter

audio_limiter = AudioRateLimiter(tier="tier1")
```

### Use with model fallback (Gemini + OpenAI)

```python
@audio_limiter.limit([
    "gemini-2.5-flash-native-audio",
    "gpt-4o-mini-tts",
    "gemini-2.5-flash-preview-tts",
    "tts-1"
])
def generate_audio(text: str, model_name: str):
    if model_name.startswith("gemini"):
        return gemini.audio.generate(
            model=model_name,
            input=text
        )
    else:
        return openai.audio.speech.create(
            model=model_name,
            input=text,
            voice="alloy"
        )
```

### Enforced Limits
- RPM for all audio models
- TPM for token-based TTS models (e.g. gpt-4o-mini-tts)
- RPD where applicable (e.g. free-tier models)
- Automatic cooldown on provider rate-limit errors

## Live / Streaming Rate Limiter (Async)

### Designed for:

- WebSockets
- Audio and real-time Gemini Live models

### Create a live limiter

```python
live_limiter = LiveRateLimiter(tier="free")
```

### Check availability before starting a session

```python
allowed, reason = await live_limiter.check_availability(
    "gemini-2.0-flash-live-001"
)

if not allowed:
    raise Exception(reason)
```

### Track usage

```python
await live_limiter.acquire_session(model)
await live_limiter.record_token_usage(model, token_count)
```

### Trigger cooldown on provider rate-limit

```python
await live_limiter.trigger_cooldown(model, wait_seconds=60)
```

## Custom Limits and Overrides

Custom limits can override tier defaults or add new models.

### Override a single model

```python
limiter = ImageRateLimiter(
    tier="tier2",
    custom_limits={
        "gpt-image-1": {
            "rpm": 100,
            "tpm": 500_000,
            "rpd": 0
        }
    }
)
```

### Add a custom or internal model

```python
limiter = ImageRateLimiter(
    tier="tier1",
    custom_limits={
        "internal-image-model": {
            "rpm": 20,
            "tpm": 0,
            "rpd": 100
        }
    }
)
```

Custom limits always take precedence over built-in tiers.

## Error Handling

```python
from llm_limiters import RateLimitExceededError, ModelNotFoundError
```

- RateLimitExceededError — all models in the priority list are exhausted
- ModelNotFoundError — requested model is not configured

## Built-In Limits

Built-in limits are defined in constants.py and include:

- Gemini text models
- OpenAI text models
- Gemini Live models
- Gemini Image / Imagen models
- OpenAI image models

Tier-2 and higher image limits are intentionally empty until discovered and overridden.

## License

MIT License
Copyright (c) 2025 Nagomi Jayamani