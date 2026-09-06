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
| **`GET /v1/dashboard/billing/subscription`** | ✅ | 🔴 **无** | account/user-balance |
| **`GET /v1/dashboard/billing/usage`** | ✅ | 🔴 **无** | account/token-balance |
| **`GET /v1/dashboard/billing/balance`** | ✅ | 🔴 **无** | account/token-balance |
| `POST /v1/images/generations` · `/v1/images/edits` · `/v1/edits` | ✅ | 🟡 只在 [同步与异步](../cn/docs/sync-async.mdx) 列了一行，**没有 API 参考页** | images/*/generation |
| `POST /v1/completions`（legacy 补全） | ✅ | 🟡 无（可能是有意不宣传） | 无 |
| 图片上传 | ❓ 未在路由里找到 | 无 | uploads/images |

**优先级判断**：`dashboard/billing` 三个端点是**开发者自助查余额和用量**的唯一途径，
既已实现又零依赖，是当前最划算的一块补白。`/v1/images/*` 那条同步图像线要先确认
是否对外开放（有没有模型组真的走 `RelayFormatOpenAIImage`），确认了再决定写不写——
现在文档主线是"图像走 `/v1/tasks`"，两条路并存会让人不知道该用哪条。

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
| **flow-music（Lyria 3.5，14 个端点：music / cover / extend / replace / stems / lyrics / video-clip / upload / download）** | 🔴 **整条产品线没有** |

`flow-music` 是 APIMart 音频侧比我们多出来的一整块。本地后台音频组 7 个也全部 0 承接，
同样等上架再说。

---

## 四、结论

1. **能立刻做的只有一件**：补 `GET /v1/dashboard/billing/*` 三个端点的文档（余额 / 用量 / 订阅）。
2. **要先确认再决定的一件**：`/v1/images/generations` 这条同步图像线是否对外开放。
3. 其余都是**模型上架的下游**——视频、音频两条线在本地后台一个承接都没有，
   在上架之前写任何东西都是猜。按 SOP 一组一组来。
