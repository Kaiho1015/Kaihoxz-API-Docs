# APIMart 能力对照与文档缺口（2026-09-06）

> 口径：左边是 APIMart 文档目录（`https://docs.apimart.ai/sitemap.xml` 全量），
> 右边是我们的文档现状。**"缺"只代表我们文档没写，不代表后台没有**——
> 模型是否真的能调，一律以模型组（`enable` + `active_route_count`）为准。
> 用途：给上架排期做参照，不是待办清单。

---

## 〇、结构上跟 APIMart / fal 一致的地方：文档不列单价

两家都不在文档里写每模型价格：

- **APIMart**：`images/gpt-image-2/generation` 这类模型页**零价格数字**；唯一叫 `pricing`
  的页（`texts/qwen3.8-max/pricing`）是**定价 API 参考**（怎么读 `data.pricing`、
  `rates` 与 `effective_rates` 的区别），同样没有金额。
- **fal**：`model-apis/pricing` 只讲计费机制，原文「Prices vary by model and may change.
  Check the model's page or the pricing page for current rates.」全页唯一数字是 API
  响应示例里的 `"unit_price": 0.025`。每模型价格在**模型库和定价页**。

2026-09-06 起我们对齐这条：API 参考页只写计费维度与口径，单价指向 `GET /v1/models`
与控制台；`changelog/pricing` 作为带日期的调价事件记录保留数字。详见 SOP 纪律 3。

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
| gemini-2.5-flash · gemini-3-pro · gemini-3.1-flash(+lite) | ✅ [Nano Banana 经济版](../cn/api-reference/image/gemini/nano-banana-rev.mdx) —— 2026-09-06 上架三个 `-rev` 档并重写；三个官方档已配承接未启用，上架后单独成页 | |
| seedream-4 · 4.5 · 5-0-pro · 5-lite | 🟡 Seedream 系列（存量页，**待重写**：`seedream-5.0-pro` 已于 2026-09-06 上架） | |
| qwen-image · qwen-image-3.0 | ✅ Qwen Image 系列 | |
| wan2.7-image | ✅ Wan Image 系列 | |
| z-image-turbo | ✅ Z.ai Image | |
| flux-2 · flux-kontext | ✅ FLUX 系列 | |
| grok-imagine · **grok-imagine-2.0-ext**（含 layer-region-edit 分层区域编辑） | 🟡 Grok Imagine 系列（存量页，**待重写**：`grok-imagine-image-2.0` 与 `-rev` 已于 2026-09-06 上架） | `layer-region-edit` 这个 action 我们有没有，重写时对 `supported_actions` |
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

2026-09-08 更新：视频线已按目录全量上架并逐组核对（见 `媒体批文档规则-20260908.md`），上表的「看起来没有对应页的」已全部有页：`flux-3-video` → FLUX 3 Video；`wan3.0-video` → 万相 Wan 系列；`seedance-2-5` → Seedance 系列；`kling-3.0-turbo` → Kling 系列；`minimax-h3` 的 `regeneration` → MiniMax H3（`context-ir`、`h3-max` 未上架）；`doubao` 即 Seedance；`seedance-2-0/private-avatar` 未上架；`wan2.7/r2v`、`videoedit` → 万相 Wan 系列；`gemini-omni-*` → Omni 视频系列。

### 音频

| APIMart | 我们的文档 |
|---|---|
| suno（30 个 action + overview） | ✅ Suno 音乐生成（单页） |
| tts · whisper-1 | ✅ TTS · 语音识别与翻译 |
| **flow-music（Lyria 3.5，14 个端点：music / cover / extend / replace / stems / lyrics / video-clip / upload / download）** | ✅ Flow Music 音乐生成（2026-09-08 上架，`generate` / `lyrics` 两个动作；其余端点目录未声明） |

2026-09-08 更新：音频组已全部核对并上架（Suno / Flow Music / gpt-4o-mini-tts / whisper-1 / gpt-4o-transcribe / gpt-4o-mini-transcribe），`tts-1` / `tts-1-hd` 停用。

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

## 六、存量页待清的内部黑话

2026-09-06 按 SOP §7 清了一遍**我重写过的页面**。以下**存量页**还带着同类措辞，
各自重写时一并处理，现在不动：

- `task/submit.mdx` —— 「预扣」两处（其中一处解释 `reserved_quota` 响应字段，改词要连字段说明一起看）
- `video/kling.mdx` · `veo.mdx` · `wan.mdx` · `hailuo.mdx` · `vidu.mdx` · `minimax-h3.mdx`
  —— 「缺少时提交即被拒，不预扣」共 8 处
- `video/veo.mdx` —— 「渠道」用作档位区分（官方直连 / 标准接入），这个是产品概念不是黑话，
  但措辞可以统一成「线路」，与 GPT Image 的「官方线路 / 逆向线路」对齐
- `image/grok-imagine.mdx` · `midjourney.mdx` —— 「备用渠道」「同一渠道」各一处

## 七、校对轮记下的待确认项（2026-09-06 第二轮）

按 SOP §7 逐页校对文本五页与 GPT Image 组时新发现的，都不是文案问题，**留给做修改的人核**：

1. **Responses 页的 `temperature` / `max_tokens` 是不是真能传。**
   `cn|en/api-reference/text/openai-multimodal.mdx` 的「请求参数」里列了这两个字段
   （存量内容，不是本轮加的）。但这五个模型（`gpt-5-pro` / `gpt-5.2-pro` /
   `gpt-5.4-pro` / `gpt-5.3-codex` / `o3-pro`）都是思考模型，OpenAI 官方对
   `temperature` 是拒绝的；`max_tokens` 在 Responses 协议里也不是有效字段
   （对应字段是 `max_output_tokens`，页面里另有一条）。
   需要照模型组的 `supported_common_params` 核一遍，多余的删掉。

2. **Responses 上的 `reasoning: {effort}` 有没有放行。**
   文本总览写了 GPT-5 及之后用 `reasoning_effort` 选推理档位，那是 Chat 的字段名；
   Responses 协议对应的是 `reasoning` 对象。目前 openai-multimodal 的参数表里两个都没有，
   本轮写「使用示例」时因此避开了这个字段。确认后补进参数表。

3. **文本模型的图像输入没有能力位。**（与前文重复记一次，因为这轮又撞上了）
   `claude-messages.mdx` 开头原先写「支持文本、图像等多模态内容」，正文却写
   「本接口不支持多轮工具流程与图像输入」，自相矛盾，本轮按正文改了。
   `general-chat.mdx` 的 `content` 字段原写「支持字符串或多模态内容数组」，
   同样无从校验，本轮改成中性的「字符串，或内容块数组」。
   模型组补上 `vision *bool` 之后，这两处才能写准。

4. **`cn|en/index.mdx` 六个失效链接本轮修了三对**（`image/gpt4o-image`、`video/veo3`、
   `task/get-status` → 各自的 overview / status），卡片文案里的 `gpt-4o` 也换成了在架模型。
   这页整体仍是存量结构，重写首页时一并处理。

5. **存量视频页仍带「本页不列单价 —— 价格会随上游调整，写在文档里迟早和实际对不上」**
   共 10 处。这句解释的是我们的决定而不是产品事实，按 SOP §7 应当只留前半句。
   等各组重写时删。

## 四、结论

1. ✅ **已做**：`GET /v1/dashboard/billing/*` 三个端点 →「账户与用量」三页。
2. ⛔ **明确不做**：`/v1/images/*` 同步端点的参考页，见 §五（后续走自家 SDK）。
3. ⏳ **等接入**：音乐（flow-music / Lyria 3.5）。
4. 其余都是**模型上架的下游**——视频、音频在本地后台一个承接都没有，
   在上架之前写任何东西都是猜。按 SOP 一组一组来。
