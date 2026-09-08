---
title: "Text Models Overview"
description: "The catalog of every text model: what each supports, how it is billed, and where to call it"
---

All text models are served through the OpenAI-compatible Chat Completions endpoint: switch models by changing `model`, with no per-vendor URLs or keys. This page lists every model ID, what it supports and how it is billed, grouped by vendor.

## Entry points

<CardGroup cols={2}>
  <Card title="Chat Completions" icon="comments" href="/en/api-reference/text/general-chat">
    `POST /v1/chat/completions`. The default entry; every model on this page is called here, except the Responses-only models.
  </Card>
  <Card title="Responses" icon="layer-group" href="/en/api-reference/text/openai-multimodal">
    `POST /v1/responses`. GPT Pro / Codex / o3-pro models accept only this entry.
  </Card>
  <Card title="Claude Messages" icon="message" href="/en/api-reference/text/claude-messages">
    `POST /v1/messages`. Native envelope kept for apps already built on the Anthropic SDK.
  </Card>
  <Card title="Gemini native" icon="google" href="/en/api-reference/text/gemini-native">
    `POST /v1beta/models/{model}:generateContent`. Native envelope kept for existing Gemini clients.
  </Card>
</CardGroup>

New integrations should use Chat Completions. The native entries exist for compatibility with existing clients and expose no extra capability. All entries authenticate with a WaveAPI key (Chat / Responses via `Authorization: Bearer`, Messages via `x-api-key`, Gemini native via `x-goog-api-key`); an ecosystem login token is not a model key — see [Authentication](/en/docs/authentication).

## Billing rules

Per-model rates are in `price_config` on `GET /v1/models` and in the console's Model Market. What a specific call cost is the `usage.cost` field on the response.

These rules apply to every text model. Model-specific differences are in the vendor tables and the model notes below them.

- **Where rates come from**: 10% off the official list price or equal to it, never above; Batch, Flex and Priority prices are not used. For the actual numbers, read `price_config` from `GET /v1/models`.
- **Total input includes cache**: `prompt_tokens` is total input; reported cache-hit / cache-write tokens are billed at their cache rates, the rest at the ordinary input rate. Cache tokens are part of the total, never an amount added on top.
- **Reasoning is inside output**: `completion_tokens` already includes `completion_tokens_details.reasoning_tokens`; reasoning is billed once at the output rate.
- **Two-rate models**: models billed as input + output have no cache rate; any cache statistics in the response are charged at the ordinary input rate, and explicit `cache_control` returns 400.
- **Long-context tiers**: a tiered model picks its tier from **total input (cache included)**; once the threshold is reached the whole request — input, cache and output — moves to the higher rate, not just the excess. Thresholds and how the exact boundary value is treated are stated per vendor.
- **Time-of-day pricing**: DeepSeek V4 is priced by the UTC slot at request start; see the DeepSeek section.
- **Quota conversion**: the line items are summed and converted to an integer quota at **500,000 quota = 1 USD**; a request with positive usage that rounds below 1 quota is charged 1, then the account group multiplier is applied and the result truncated. `usage.cost` in the response is that integer quota, **not dollars**.

All rates are in USD per 1 million tokens:

```text
ordinary input tokens = prompt_tokens - cached_tokens - cache_write_tokens
cost (USD) = ( ordinary input tokens × input rate
             + cached_tokens × cache-read rate
             + cache_write_tokens × cache-write rate
             + completion_tokens × output rate ) / 1,000,000
quota      = cost (USD) × 500,000, truncated, minimum 1
```

The final charge is the text ledger entry in the console billing records. The states mean:

| Ledger state | Meaning |
|---|---|
| `reserved` | Credit is held, result not yet confirmed; the held amount is not the final charge |
| `pricing_pending` | Usage received, cost under review; the credit stays held |
| `settlement_pending` / `refund_pending` | Waiting for settlement or refund to complete |
| `settled` / `refunded` | Charge or refund completed; reconcile against the final ledger amount |

<Warning>
A missing final `usage`, a dropped connection or a response without a cost field **does not make the call free**. Check the existing usage record in the console before resubmitting; never retry automatically on that basis.
</Warning>

## Caching

Caching is graded per model by which cache rates that model has configured. Cache reads and writes
**replace** the matching ordinary input charge at their own rate; they are not added on top.

| Grade | Test | Models |
|---|---|---|
| No cache discount | `cache_billing: "input_output"` | every other model in the catalog; any cache statistics in the response bill at the ordinary input rate |
| Cache read only | has `cache_read` | `gpt-5.5` `gpt-5.4` `grok-4.6` `gemini-3.6-flash` `gemini-3.7-flash` `gemini-3.8-flash` `kimi-k3` `qwen3.8-max` |
| Cache read + write | also `cache_write` | `gpt-5.6-luna` `gpt-5.6-terra` `gpt-5.6-sol` `gpt-6-astra` |
| Cache read + 5-min write + 1-hour write | also `cache_write_1h` | `claude-opus-5` `claude-sonnet-5` `claude-fable-5` `claude-fable-5-1` |
| Time-of-day cache rate | `cache_read` inside each `text_schedule` window | `deepseek-v4-pro` `deepseek-v4-flash` |

### Automatic vs explicit caching

**Automatic caching** is decided upstream and needs no parameters from you: hit tokens appear in
`usage.prompt_tokens_details.cached_tokens` and bill at that model's cache-read rate. Hits are never guaranteed, so cost estimates should not assume one.

**Explicit caching** marks a reusable prefix with `cache_control`. It is allowed per model:

| Models | Explicit `cache_control` |
|---|---|
| `claude-opus-5` `claude-sonnet-5` `claude-fable-5` `claude-fable-5-1` | ✅ Allowed; all three cache rates configured (read / 5-minute write / 1-hour write) |
| every `gemini-*`, and `qwen3.8-max` | ❌ Automatic caching only; sending `cache_control` returns 400 |
| two-rate models | ❌ No cache billing; sending `cache_control` returns 400 |
| everything else (`gpt-5.4/5.5/5.6-*`, `gpt-6-astra`, `grok-4.6`, `kimi-k3`, `deepseek-v4-*`) | Upstream caches automatically; `cache_control` is neither needed nor used |

Unsupported requests return `400` and are not billed.

<Note>
On first integration, send a small request and check that the cache line items in your console usage record look as expected before scaling up.
</Note>

### Writing a Claude explicit cache request

On the OpenAI-compatible endpoint, `content` **must be an array of content blocks**. A string
`content` cannot carry `cache_control`; the marker is ignored and the whole prefix bills as ordinary input.

```json
{
  "model": "claude-sonnet-5",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "Put the long prefix you want to reuse here...",
          "cache_control": {"type": "ephemeral"}
        }
      ]
    },
    {"role": "user", "content": "Answer using the content above."}
  ]
}
```

The native [Messages endpoint](/en/api-reference/text/claude-messages) takes the same shape with the
prefix in the `system` array. `ttl` defaults to 5 minutes; for the 1-hour tier send
`"cache_control": {"type": "ephemeral", "ttl": "1h"}` together with the
`anthropic-beta: extended-cache-ttl-2025-04-11` header — the gateway forwards that header upstream as-is.

### Hit conditions and reading usage

- **Prefix length** — usually at least ~1,024 tokens; shorter prefixes create no cache.
- **Byte-identical prefix** — any difference in text, spaces, newlines or content-block order misses.
- **Reuse within the TTL** — 5 minutes or 1 hour, counted from the most recent hit.

In Chat responses the hit count is `usage.prompt_tokens_details.cached_tokens`. Native Messages reports
`cache_read_input_tokens` and `cache_creation_input_tokens` instead, and its `input_tokens` **excludes**
both — total input is the sum of the three (whereas Chat's `prompt_tokens` already includes them).
Written tokens bill at the cache-write rate, which is higher than ordinary input, so explicit caching suits prefixes that are stable and reused within the TTL.

## Not supported

The following return `400` and are not billed:

- **Vendor built-in tools** — any entry in `tools` whose type is not `function` or `custom` (hosted web search, hosted execution, and similar). Client-executed function tools are not in this group and work normally.
- **`web_search_options`**.
- **`service_tier`** set to anything other than `standard` / `default`.
- **Explicit caching** — see the allow-list above.

Each model serves only the protocols it supports (Chat / Responses / Claude Messages / Gemini native). Sending a request to a protocol a model does not serve, or sending `tools`, `tool_choice` or `response_format` to a model that does not support them, also returns `400`. The protocols and capabilities each model supports are in the catalog below.

## Model catalog

<Note>
**How to read the tables**: every model supports non-streaming and streaming text output, so those are not given a column. In the JSON / Tools column the left mark is JSON Schema structured output and the right one is function calling — **the platform returns the function name and arguments; your application runs the tool**. `✓` means supported, `—` means not supported. The Billing column names which dimensions a model is billed on; for rates see [Catalog API](#catalog-api). A model with a long-context tier picks its tier from **total input** (cache included) and switches the whole request once the threshold is reached; the thresholds are in the model notes under each table. Model notes also carry each model's input and output limits and any model-specific restrictions; a limit is the maximum the endpoint accepts, and input and output cannot both be maxed out at once.
</Note>

{{CATALOG}}
## Catalog API

Live availability, price configuration and capability flags come from the catalog API:

```bash
curl https://www.qingbo.dev/v1/models \
  -H "Authorization: Bearer $WAVE_API_KEY"
```

Single model: `GET /v1/models/{model}`. The `price_config` it returns is where this page's tables come from: `input` / `output` are the base rates, `cache_read` / `cache_write` / `cache_write_1h` show how far caching is opened up for that model, `input_tier_threshold` with the `*_above_price` fields is the long-context tier, and `cache_billing: "input_output"` means input and output are the only two rates.

The catalog returns every text model currently live. A model that does not appear in the response cannot be called.
