# APIMart 能力对照与文档缺口（2026-09-06）

> 口径：左边是 APIMart 文档目录（`https://docs.apimart.ai/sitemap.xml` 全量），
> 右边是我们的文档现状。**"缺"只代表我们文档没写，不代表后台没有**——
> 模型是否真的能调，一律以模型组（`enable` + `active_route_count`）为准。
> 用途：给上架排期做参照，不是待办清单。

---

## 一、结构上不抄 APIMart 的地方

APIMart 直接代理各家原生端点，一个 action 就是一个 URL，所以 `midjourney/` 有 17 页、
`audios/suno/` 有 30 页。**我们的媒体类统一走 `POST /v1/tasks`，action 是请求字段不是端点**，
一个模型组的多个 action 写在同一页的 action 表里。

抄 APIMart 要抄**能力覆盖**，不要抄**页面切分**。

同理，APIMart 20 多个家族只有 `audios/suno` 一个 overview；我们的 overview 承担的是
"同家族多个 model ID 之间怎么选"，是他们没有的职责——建不建按 SOP §2.2 判。

---

## 二、平台级接口（不依赖模型上架，可以立刻补）

按 `router/relay-router.go` 的实际路由核对：

| 端点 | 网关 | 我们的文档 | APIMart 对应 |
|---|---|---|---|
| `POST /v1/chat/completions` · `/v1/responses` · `/v1/messages` · `/v1beta/models/*` | ✅ | ✅ 文本四页 | texts/* |
| `POST /v1/tasks` · `GET /v1/tasks/{id}` · `POST /v1/tasks/{id}/cancel` | ✅ | ✅ 任务三页 | tasks/status · tasks/webhook |
| `POST /v1/embeddings` · `/v1/rerank` · `/v1/moderations` | ✅ | ✅ 工具三页 | moderations/* |
| `POST /v1/audio/speech` · `/transcriptions` · `/translations` | ✅ | ✅ 音频三页 | audios/tts · whisper-1 |
| `GET /v1/dashboard/billing/balance` | ✅ | ✅ [查询余额](../cn/api-reference/account/balance.mdx)（主推） | account/token-balance |
| `GET /v1/dashboard/billing/usage` | ✅ | ✅ [查询已用量](../cn/api-reference/account/usage.mdx) | account/token-balance |
| `GET /v1/dashboard/billing/subscription` | ✅ | ✅ [查询总额度](../cn/api-reference/account/subscription.mdx) | account/user-balance |
| `POST /v1/images/generations` · `/v1/images/edits` · `/v1/edits` | ✅ **对外开放**（供 OpenAI SDK 使用，2026-09-06 Kaiho 确认） | 🟡 已在[图像生成概述](../cn/api-reference/image/overview.mdx)加「两条调用路径」对照；**完整参考页待定，见 §五** | images/*/generation |
| `POST /v1/completions`（legacy 补全） | ✅ | 🟡 无（可能是有意不宣传） | 无 |
| 图片上传 | ❓ 未在路由里找到 | 无 | uploads/images |

`dashboard/billing` 三个端点已于 2026-09-06 补齐，放在 API 参考的新分组
**「账户与用量」**（跟随全库一端点一页的惯例，三页；`balance` 为主推，
另外两个是 OpenAI 兼容形状，供既有额度查询工具对接）。

---

## 三、模型家族对照

### 图像

| APIMart | 我们的文档 | 备注 |
|---|---|---|
| gpt-image-1 · gpt-image-2（generation + official） | ✅ [GPT Image 系列](../cn/api-reference/image/gpt-image/overview.mdx) | 我们已上架 `gpt-image-2` 两条线；`gpt-image-1` / `gpt-image-1.5` 后台已配承接但未启用 |
| gemini-2.5-flash · gemini-3-pro · gemini-3.1-flash(+lite) | ✅ Gemini Image 系列 | |
| seedream-4 · 4.5 · 5-0-pro · 5-lite | ✅ Seedream 系列 | |
| qwen-image · qwen-image-3.0 | ✅ Qwen Image 系列 | |
| wan2.7-image | ✅ Wan Image 系列 | |
| z-image-turbo | ✅ Z.ai Image | |
| flux-2 · flux-kontext | ✅ FLUX 系列 | |
| grok-imagine · **grok-imagine-2.0-ext**（含 layer-region-edit 分层区域编辑） | 🟡 Grok Imagine 系列 | **`layer-region-edit` 这个 action 我们有没有，要对模型组的 `supported_actions`** |
| midjourney（17 页含 best-practices / workflow） | ✅ Midjourney（单页 + action 表） | 结构差异见 §一；他们的 best-practices / workflow 是指南内容，我们没有对应物 |
| imagen-4.0-apimart | ⚪ 已下架 | 见 changelog 2026-09-03 |

### 视频

APIMart 25 个家族：doubao · flux-3-video · gemini-omni-1.1-flash · gemini-omni-flash-preview ·
grok-imagine · happyhorse-1.0/1.1 · kling-3.0-turbo · kling-v2-6(+motion-control) · kling-v3 ·
kling-v3-omni · kling-video-o1 · minimax-h3(+context-ir/max/regeneration) · minimax-hailuo(+2.3) ·
omni-flash-ext · pixverse-v6 · seedance-1-5-pro · seedance-2-0(+private-avatar) · seedance-2-5 ·
skyreels-v4 · sora-2 · veo3(+official/remix) · vidu-q3(+pro) · wan2.5 · wan2.6(+i2v-flash) ·
wan2.7(+r2v/videoedit) · wan3.0-video

我们已有 14 页覆盖了 Kling / Veo / Seedance / Hailuo / MiniMax H3 / Sora / Vidu / Wan /
SkyReels / PixVerse / HappyHorse / Omni / Grok Imagine Video。

**看起来没有对应页的**：`flux-3-video` · `wan3.0-video` · `doubao`（可能已并进 Seedance 页）·
`seedance-2-5` · `kling-3.0-turbo`（可能已在 Kling 页内）· `minimax-h3` 的
`context-ir` / `regeneration` 子能力 · `seedance-2-0/private-avatar` · `wan2.7/r2v` /
`videoedit`。

⚠️ **本地后台的视频模型组 49 个全部 `active_route_count = 0`**，所以现在无从核对，
也不该动视频文档。等视频线开始上架时逐组对。

### 音频

| APIMart | 我们的文档 |
|---|---|
| suno（30 个 action + overview） | ✅ Suno 音乐生成（单页） |
| tts · whisper-1 | ✅ TTS · 语音识别与翻译 |
| **flow-music（Lyria 3.5，14 个端点：music / cover / extend / replace / stems / lyrics / video-clip / upload / download）** | ⏳ **音乐模型尚未接入**（2026-09-06 Kaiho），接入后再写 |

`flow-music` 是 APIMart 音频侧比我们多出来的一整块，我们**还没接入**。本地后台音频组
7 个也全部 0 承接，等接入后按 SOP 走一遍。

---

## 五、`/v1/images/*` 同步端点：不写参考页（2026-09-06 Kaiho 拍）

**已确认（读 `router/relay-router.go` · `relay/image_handler.go` · `service/quota.go`）**

- 端点开放，走 `middleware.Distribute()` → 模型组 → 渠道，与任务接口同一套路由。
- **计费同源**：`postConsumeQuota` 见到 `WavePriceConfig` 就转 `service.PostWaveConsumeQuota`，
  用的是同一份模型组 `price_config`。不存在"这条路不计费"或"另一套价"。
- **不做模型组能力校验**：`relay/helper/valid_request.go` 的 `GetAndValidOpenAIImageRequest`
  只有 `dall-e-2` / `dall-e-3` / `gpt-image-1` 三个硬编码分支，没有调用
  `supported_actions` / `aspect_ratios` / `resolutions` / `qualities` / `max_image_inputs` /
  `constraints` 的任何校验。任务接口那套预扣前拒绝在这条路上不生效。

**决定：不写完整参考页。** 理由是后续会提供官方 SDK（对标 fal 的做法），新接入一律走
自家 SDK + 任务接口，OpenAI 兼容端点只作为存量项目的迁移过渡，没必要按参考页的规格维护
一套参数表——何况参数映射还有下面这些说不清的地方。

[图像生成概述](../cn/api-reference/image/overview.mdx) 里保留了一张**四行对照表**
（返回方式 / 请求形状 / 能力校验 / 适合谁），够 OpenAI SDK 用户判断该不该走这条路，
也把"不做能力校验"这个风险讲清楚了。

**留给后端的三个问题**（不影响文档，但影响这条路的可用性）：

1. `dto.ImageRequest` 里只有 `size` 和 `aspect_ratio`，**没有 `resolution` 字段**——
   `gpt-image-2` 的 `1k` / `2k` / `4k` 档在同步端点怎么指定？这直接决定计费落在哪一档。
2. DTO 里没有 `mask_url`，`/v1/images/edits` 的 multipart 分支也只取 `prompt` / `model` /
   `n` / `quality` / `size` / `image` / `watermark`——掩码重绘在这条路上是不是根本没有入口？
3. 不做模型组能力校验是有意为之还是欠账？

## 四、结论

1. ✅ **已做**：`GET /v1/dashboard/billing/*` 三个端点 →「账户与用量」三页。
2. ⛔ **明确不做**：`/v1/images/*` 同步端点的参考页，见 §五（后续走自家 SDK）。
3. ⏳ **等接入**：音乐（flow-music / Lyria 3.5）。
4. 其余都是**模型上架的下游**——视频、音频在本地后台一个承接都没有，
   在上架之前写任何东西都是猜。按 SOP 一组一组来。
