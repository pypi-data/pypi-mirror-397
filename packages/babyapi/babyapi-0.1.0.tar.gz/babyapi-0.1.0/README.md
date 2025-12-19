![BabyAPI banner](https://api.babyapi.org/images/banner.png)

# BabyAPI (Python SDK)

A tiny Python client for **BabyAPI** — an **OpenAI-compatible** API for hosted open-weight models.

> Minimal surface area. Calm defaults. You bring an API key — we handle the GPUs.

**Endpoints**
- OpenAI-compatible:
  - `POST /v1/chat/completions`
  - `POST /v1/completions`
- BabyAPI convenience:
  - `POST /infer` (simple text-in, text-out)

---

## Install

```bash
pip install babyapi
```

---

## Quick start (the easy path): `client.baby.infer(...)`

If you just want **text in → text out**, start here.

```py
import os
from babyapi import BabyAPI

client = BabyAPI(
    api_key=os.getenv("BABYAPI_API_KEY"),
    default_model="mistral",  # so you can call baby.infer("...") without specifying model
)

out = client.baby.infer(
    {
        "prompt": "Write a 1-line release note title for BabyAPI.",
        "maxTokens": 40,
        "temperature": 0.5,
    }
)

print(out["output"])
print(out.get("usage"))
```

You can also pass a raw string:

```py
out = client.baby.infer("Explain BabyAPI in one sentence.")
print(out["output"])
```

### Supported options (aliases accepted)

You can pass options directly **or** inside `"options": {...}`:

- `max_tokens` / `maxTokens`
- `temperature`
- `top_p` / `topP`
- `top_k` / `topK`
- `stop`
- `presence_penalty` / `presencePenalty`
- `frequency_penalty` / `frequencyPenalty`

Example with aliases + nested `options`:

```py
out = client.baby.infer(
    {
        "model": "mistral",
        "prompt": "Give 3 calm API principles.",
        "options": {"topP": 0.9, "max_tokens": 80},
    }
)
print(out["output"])
```

---

## One method for both OpenAI endpoints: `client.infer(...)`

If you want “do the right thing” with OpenAI-style payloads:

- If you pass `messages` → routes to **chat completions**
- If you pass `prompt` → routes to **completions**

```py
chat_res = client.infer(
    {
        "model": "mistral",
        "messages": [{"role": "user", "content": "One-line slogan for BabyAPI?"}],
    }
)
print(chat_res["choices"][0]["message"]["content"])

comp_res = client.infer(
    model="mistral",
    prompt="Give 3 product names for a tiny LLM SDK.",
    max_tokens=60,
)
print(comp_res["choices"][0]["text"])
```

---

## OpenAI-compatible: Chat Completions

```py
res = client.chat.completions.create(
    model="mixtral",
    messages=[
        {"role": "system", "content": "You are concise."},
        {"role": "user", "content": "Give me 3 tagline ideas for a tiny LLM API."},
    ],
    temperature=0.7,
)

print(res["choices"][0]["message"]["content"])
```

---

## OpenAI-compatible: Completions

```py
res = client.completions.create(
    model="mistral",
    prompt="Write a friendly release note opener for BabyAPI.",
    max_tokens=120,
    temperature=0.7,
)

print(res["choices"][0]["text"])
```

---

## Streaming (SSE)

`.stream(...)` yields `SSEEvent` objects:
- `event.done` → `True` when the stream is finished (`[DONE]`)
- `event.data` → parsed JSON when possible (otherwise `None`)
- `event.raw` → raw `data:` payload string

### Streaming: chat

```py
import os
from babyapi import BabyAPI

client = BabyAPI(api_key=os.getenv("BABYAPI_API_KEY"))

for event in client.chat.completions.stream(
    model="mistral",
    messages=[{"role": "user", "content": "Write a short poem about servers."}],
):
    if event.done:
        break

    delta = (event.data or {}).get("choices", [{}])[0].get("delta", {})
    chunk = delta.get("content")
    if chunk:
        print(chunk, end="", flush=True)

print()
```

### Streaming: completions

```py
for event in client.completions.stream(
    model="mistral",
    prompt="List 5 calm API-building tips.",
):
    if event.done:
        break

    text = (event.data or {}).get("choices", [{}])[0].get("text")
    if text:
        print(text, end="", flush=True)

print()
```

> Note: like many SDKs, streaming requests are not retried. If you want retries for streams, wrap your call at the application level.

---

## Multimodal (vision) examples (OpenAI-style)

If the model you select supports vision, you can send images using OpenAI-style message content.

### Vision: non-streaming

```py
res = client.chat.completions.create(
    model="pixtral",  # or another vision-capable model you expose
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe the image in 2 sentences. Then list 3 objects you see."},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://api.babyapi.org/images/banner.png"},
                },
            ],
        }
    ],
)

print(res["choices"][0]["message"]["content"])
```

### Vision: streaming

```py
for event in client.chat.completions.stream(
    model="pixtral",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is this image trying to communicate?"},
                {"type": "image_url", "image_url": {"url": "https://api.babyapi.org/images/banner.png"}},
            ],
        }
    ],
):
    if event.done:
        break

    delta = (event.data or {}).get("choices", [{}])[0].get("delta", {})
    chunk = delta.get("content")
    if chunk:
        print(chunk, end="", flush=True)

print()
```

> Image support depends on the model you choose. If the model is text-only, the API may reject image inputs.

---

## Configuration

```py
import os
from babyapi import BabyAPI

client = BabyAPI(
    api_key=os.getenv("BABYAPI_API_KEY"),          # required (or BABY_API_KEY)
    base_url=os.getenv("BABYAPI_BASE_URL"),        # optional (default: https://api.babyapi.org)
    timeout_s=60.0,                                # JSON requests only
    max_retries=2,                                 # retry transient failures
    retry_base_delay_s=0.25,                       # exponential backoff base
    default_model="mistral",                       # used by client.baby.infer when model omitted
    default_headers={"x-app": "my-sideproject"},   # extra headers for every request
)
```

Environment variables supported:
- `BABYAPI_API_KEY` (or `BABY_API_KEY`)
- `BABYAPI_BASE_URL`
- `BABYAPI_DEFAULT_MODEL`

---

## Per-call overrides (RequestOptions)

Every `.create(...)` / `.stream(...)` accepts `request_options`.

```py
import os
from babyapi import BabyAPI, RequestOptions

client = BabyAPI(api_key=os.getenv("BABYAPI_API_KEY"))

res = client.chat.completions.create(
    request_options=RequestOptions(
        timeout_s=30.0,
        max_retries=0,
        headers={"x-trace": "abc123"},
    ),
    model="mistral",
    messages=[{"role": "user", "content": "Hello."}],
)
```

You can also pass a plain dict:

```py
res = client.chat.completions.create(
    request_options={"timeout_s": 10.0, "headers": {"x-app": "demo"}},
    model="mistral",
    messages=[{"role": "user", "content": "Hi again."}],
)
```

---

## Timeouts & cancellation

- JSON requests use `timeout_s` (default: 60s).
- Streaming requests default to **no timeout** (infinite), matching common SSE usage.
  - If you want a stream timeout, pass `request_options={"timeout_s": 30.0}`.
- To stop a stream early, `break` your loop.

---

## Errors

SDK errors raise `BabyAPIError` when possible.

```py
import os
from babyapi import BabyAPI, BabyAPIError

client = BabyAPI(api_key=os.getenv("BABYAPI_API_KEY"))

try:
    client.chat.completions.create(model="mistral", messages=[])
except BabyAPIError as err:
    print(
        {
            "message": err.message,
            "status": err.status,
            "code": err.code,
            "type": err.type,
            "request_id": err.request_id,
        }
    )
```

---

## Context manager / cleanup

The client maintains an `httpx.Client`. Use it as a context manager to ensure clean shutdown:

```py
import os
from babyapi import BabyAPI

with BabyAPI(api_key=os.getenv("BABYAPI_API_KEY")) as client:
    res = client.completions.create(model="mistral", prompt="Ping")
    print(res["choices"][0]["text"])
```

---

## License

MIT.
