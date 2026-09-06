# 文本类文档 · 核对记录与待办（2026-09-06）

文本类已按「一入口一页 + `text/overview` 目录总览」收敛（提交 `53e1513`），
74 个单模型页原文保留在 WIP 快照 `375692f`。

## 0. 已用模型组目录核对（结案）

真相源 = 网关 `GET /v1/models`（本地 40081，公开、无需 Key），返回 77 个文本模型。
逐项比对 overview：**模型 ID、输入/输出价、缓存价、长上下文阈值、函数调用/结构化输出
能力位，零差异**。原 A/B/C 三项存疑全部结案：

- **模型 ID 用连字符**：目录里就是 `claude-opus-4-8` / `claude-sonnet-4-6` /
  `claude-haiku-4-5`，5.x 为 `claude-opus-5` / `claude-sonnet-5` / `claude-fable-5` /
  `claude-fable-5-1`。main 上 `general-chat.mdx` 的点号 + 日期写法
  （`claude-opus-4.8`、`claude-opus-4.5-20251101`）**是错的**，已随该清单删除。
- **集合差异**：`gpt-4o` / `gpt-4o-mini` / `gpt-5.2-codex` / `gpt-5.1-codex-max` /
  `gemini-2.5-flash` / `gemini-3.1-flash-lite-preview` / `kimi-k2.5` 已下架，目录里没有，
  文档不写。目录新增的 10 个（`gpt-6-astra`、`gpt-5-pro`、`o3-pro`、`gemini-3.8-flash`、
  `deepseek-v3.1-terminus`、`grok-4.20-0309-*`、`mimo-v2.5-pro`、`step-3.7-flash` 等）已收录。
- **分档阈值**：Grok 全系 `input_tier_threshold = 199999`（即达到 200,000 切档），
  Gemini 两个 Pro 是 `200000`（即超过 200,000 才切档）——**差一个 token 是真的**，不是笔误。
  MiniMax M3 目录里为纯两项计价，**没有** main 提过的 512K 分档。

后续模型上下架，以 `GET /v1/models` 为准重新生成 overview 的表，不要手改。

## A. 缓存：价格已分四档，行为待确认

目录 `price_config` 把缓存能力分得很清楚，**价格层面已足够写一节缓存文档**：

| 档 | 判据 | 型号 |
|---|---|---|
| 无缓存优惠 | `cache_billing: "input_output"` | 55 个 |
| 只有缓存读 | 有 `cache_read`，无 `cache_write` | `gpt-5.5` `gpt-5.4` `grok-4.6` `gemini-3.6/3.7/3.8-flash` `kimi-k3` `qwen3.8-max` |
| 缓存读 + 写 | 加 `cache_write` | `gpt-5.6-luna/terra/sol` `gpt-6-astra` |
| 缓存读 + 5 分钟写 + 1 小时写 | 再加 `cache_write_1h` | `claude-opus-5` `claude-sonnet-5` `claude-fable-5` `claude-fable-5-1` |
| 时段缓存价 | `text_schedule.windows[].rates.cache_read` | `deepseek-v4-pro` `deepseek-v4-flash` |

⏳ **待确认（目录看不出来，需要 Go 源码或实打）**：网关是否透传显式 `cache_control`
（含 `ttl: "1h"` 与 `anthropic-beta: extended-cache-ttl-2025-04-11`）。
`cache_write_1h` 这一档单价**只有显式 TTL 缓存才用得到**，所以 Claude 那四个型号很可能
已放开；但单模型页的验收记录写的是「缓存价已配置，命中与 TTL 写入尚未验收」，两者需要对齐。
确认放开后，参考 APIMart `texts/general/claude-context-cache` 的结构写一节：
使用场景 / Messages 写法 / OpenAI 兼容写法 / 命中条件 / 计费口径 / 排查清单。

## B. 多模态：目录未声明，且 `openai-multimodal.mdx` 超额宣称 🔴

目录里 77 个文本模型的 `tags` 只有四种：文本生成 / 流式输出 / 函数调用 / 结构化输出。
**没有任何多模态或视觉标签。**

而 `cn|en/api-reference/text/openai-multimodal.mdx`（本次未动，从 main 继承）写着：

- 模型清单为 `gpt-5-codex` / `gpt-5.1-codex` / `gpt-5.1-codex-mini` / `gpt-5.2-codex`
  —— **目录里一个都没有**。目录里只走 Responses 的型号是 `gpt-5-pro` / `gpt-5.2-pro` /
  `gpt-5.3-codex` / `gpt-5.4-pro` / `o3-pro`，且它们的能力位只有「流式输出」。
- 完整写了 `web_search` / `file_search` / `remote_mcp` 三个托管工具的用法，
  而 overview 明确写这些在预扣前拒绝。
- 写了 `input_image` / `input_video` 多模态输入、图像格式与大小限制。

⏳ **待办**：按目录重写该页（模型清单、工具章节、多模态章节三处），或在放开多模态后
重新验收再写。这是目前文档里最大的一处不实。

## C. `POST /waveapi/public/quote` 是管理端接口 🔴

实打返回 `401 {"message":"缺少管理鉴权 token (HMAC 或 Bearer)"}`，
开发者拿 WaveAPI Key 调不通。文档里把它写成给用户估价用的位置：

- `cn|en/api-reference/video/overview.mdx`（媒体类，本批暂停）
- `cn|en/changelog/pricing.mdx` 两处（媒体类）

文本类的两处引用已改掉。媒体类那三处待一并处理：改成管理端说明，或删除。

## D. 其他遗留

- `cn/index.mdx` / `en/index.mdx` 三条死链：`api-reference/image/gpt4o-image`、
  `api-reference/task/get-status`、`api-reference/video/veo3`（媒体类，本批暂停）。
- 文本页的 `api:` 字段与示例已回到 `https://www.qingbo.dev/v1`（原 74 个单模型页的
  `http://localhost:40081` 随页面一起删除）。若要保留一处本地联调地址，
  建议只写在 `guides/quickstart.mdx`。
- overview 的表由脚本从 `GET /v1/models` 生成，生成脚本尚未入仓（目前在本机 `~/work/`）。
  长期应放进仓内 `tools/`，模型上下架后重跑。
