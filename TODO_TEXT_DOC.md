# 文本类文档 · 核对记录与移交清单（2026-09-06）

文本类已收敛完毕。真相源是**模型组**，不是任何一份手写清单：

- 公开目录 `GET /v1/models`（无需 Key）—— 模型 ID、`tags`、`price_config`
- 管理端 `GET /admin/waveapi/model-groups`（后台会话）—— `capabilities`
  （`supported_protocols` / `streaming` / `tool_calling` / `structured_output` /
  `input_token_limit` / `output_token_limit`）

77 个启用文本组已逐项比对，文档与模型组**零差异**。模型上下架后重新导出即可，不要手改表。

---

## 一、已结案的核对项

### 模型 ID 写法（2026-09-06 Kaiho 拍：Anthropic 保持连字符）

后台模型组里 Anthropic 全系 ID 是连字符、展示名是点号：`Claude Opus 4.8` / `claude-opus-4-8`、
`Claude Fable 5.1` / `claude-fable-5-1`。点号形式在网关里不存在——`GET /v1/models/claude-opus-4.8`
返回 `model_not_found`。

**这不是不一致，是"每家跟随各自官方写法"**：OpenAI 官方是 `gpt-5.6`、Google 是 `gemini-3.6`、
Qwen 是 `qwen3.8`（点号），而 Anthropic 官方本来就是连字符（网关渠道层能解析出
`claude-sonnet-4-5-20250929`、`claude-opus-4-1-20250805`，全是上游原样）。**决定：不改**，
改 ID 是破坏性变更，且改了反而与 Anthropic 官方文档对不上。

### 模型集合

已下架、文档不写：`gpt-4o` `gpt-4o-mini` `gpt-5.2-codex` `gpt-5.1-codex-max` `gemini-2.5-flash`
`gemini-3.1-flash-lite-preview` `kimi-k2.5`（后台是"停用"组，`GET /v1/models` 不列，
但 `GET /v1/models/{id}` 仍能解析到停用组——以列表为准）。

已上架、文档已收：`gpt-6-astra` `gpt-5-pro` `o3-pro` `gemini-3.8-flash` `deepseek-v3.1-terminus`
`grok-4.20-0309-*` `mimo-v2.5-pro` `step-3.7-flash` 等 10 个。

### 长上下文阈值

Grok 全系 `input_tier_threshold = 199999`（达到 200,000 切档），Gemini 两个 Pro 是 `200000`
（超过 200,000 才切档）——**差一个 token 是真的**。MiniMax M3 为纯两项计价，没有 512K 分档。

### 协议归属（`supported_protocols`）

- 只走 Responses：`gpt-5-pro` `gpt-5.2-pro` `gpt-5.4-pro` `gpt-5.3-codex` `o3-pro`（且这五个
  `tool_calling` / `structured_output` 均为 false）
- 走 Gemini 原生的八个：`gemini-2.5-flash-lite` `gemini-2.5-pro` `gemini-3-flash-preview`
  `gemini-3.1-pro-preview` `gemini-3.5-flash` `gemini-3.6-flash` `gemini-3.7-flash`
  `gemini-3.8-flash`（`gemini-3.5-flash-lite` 只走 Chat）
- 走 Claude 原生 Messages 的只有两个：`claude-sonnet-5` `claude-opus-5`

### 显式缓存放行范围

依据 `service/text_billing_capabilities.go` 的 `validateTextBillingExtras`：
`cache_control` 在**两项计价组、全部 `gemini-*`、`qwen3.8-max`** 上预扣前拒绝，其余放行。
真正用得上的是配了 `cache_write_1h` 的四个：`claude-opus-5` `claude-sonnet-5`
`claude-fable-5` `claude-fable-5-1`。`provider/claude/adaptor.go` 确认 `anthropic-beta`
头原样透传，1 小时 TTL 链路通。

⚠️ **仍缺一次实测**：缓存命中与 TTL 写入没做过验收，文档里保留了"先小请求核对再放量"的提示。
探测脚本在 `~/Echo/Claude outputs/waveapi-探测-缓存与多模态-20260906.sh`（跑 1/2/3 即可）。

---

## 二、移交给专人处理（非文档，本次只记录不动）

### T1 · 文本视觉能力缺一个声明位 🔴

`service/wave_capabilities.go` 的 `Capabilities` 里有 `streaming` / `tool_calling` /
`structured_output` / `supported_protocols` / `input_token_limit`，还有 `max_image_inputs`——
但 `max_image_inputs` 是**图像生成组的参考图张数**，不是文本模型能不能吃图。

结果是**文本视觉能力在系统里没有真相源**：模型组没字段、`/v1/models` 的 tags 没有、
网关也不校验。实际行为是"不拦截"，请求原样打到上游，预扣走 `service/token_counter.go`
那套图像 token 估算。

**建议**：加 `vision *bool`，语义与 `tool_calling` / `structured_output` 完全同款
（nil 未知 / false 预扣前拒 / true 放行），逐模型验收后回填。在那之前文档一律写"未开放"。

### T2 · `/api/public/*` 是内部投影，文档里被当成开发者接口 🔴

`router/api-router.go` 里整个 `/public` 组挂 `middleware.VinEndAuth()`，注释写明是
"前端安全投影，VinEnd HMAC 调用后转发开发者站"。实打 `POST /waveapi/public/quote`
返回 `401 缺少管理鉴权 token (HMAC 或 Bearer)`。

文本类的两处引用已删。**剩余三处待改**（媒体批）：
`cn|en/api-reference/video/overview.mdx`、`cn|en/changelog/pricing.mdx` ×2。
要么改成"控制台估价"，要么删。

### T3 · changelog 里留着从未生效的模型 ID

`cn|en/changelog/models.mdx` 有 `gpt-5-codex` `gpt-5.1-codex` `gpt-5.1-codex-max`
`gpt-5.2-codex` `kimi-k2.5` `gemini-3.1-flash-lite-preview` `claude-opus-4.8`
`claude-opus-4.5-20251101` 等条目——这些 ID 在模型组里**从来不存在**（点号形式）
或**已下架**。changelog 是历史记录可以保留事件，但写错的 ID 会被当成可调用模型抄走。
建议：统一为模型组 ID，或在该页顶部加一句"历史条目中的模型 ID 以当前模型目录为准"。

### T4 · 已撤回的误报（存档，不用查）

先前怀疑"两项计价的 Claude 走原生 `/v1/messages`，`system[].cache_control` 绕过拒绝导致
计费漏损"。**不成立**：两项计价的 Claude 组没有声明 `anthropic_messages` 协议，
`validateDeclaredTextProtocol` 会在更早一步拒掉；声明了原生协议的只有
`claude-sonnet-5` / `claude-opus-5`，而这两个本来就允许显式缓存。

---

## 三、其他遗留

- `cn/index.mdx` / `en/index.mdx` 三条死链：`api-reference/image/gpt4o-image`、
  `api-reference/task/get-status`、`api-reference/video/veo3`（媒体类，本批暂停）。
- overview 的表由脚本从模型组导出生成，生成脚本尚在本机 `~/work/`，未入仓。
  长期应放进仓内 `tools/`，模型上下架后重跑。
- 文本页 URL 已统一 `https://www.qingbo.dev/v1`。若要留一处本地联调地址，
  建议只写在 `guides/quickstart.mdx`。
