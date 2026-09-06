# 文本类文档 · 待核对清单（2026-09-06）

文本类已按「一入口一页 + `text/overview` 目录总览」收敛（提交 `53e1513`），
74 个单模型页原文保留在 WIP 快照 `375692f`。下面是重构中发现、**需要拿 Go 模型目录
（`GET /v1/models`）或后台配置对一遍**的问题，不要凭文档互相印证。

## A. 模型 ID 写法冲突（Anthropic）

同一批模型在两处写法不同，只能有一个对：

| 来源 | 写法 |
|---|---|
| main 上 `general-chat.mdx` 的模型清单 | `claude-opus-4.8`、`claude-sonnet-4.6`、`claude-opus-4.5-20251101`（点号 + 带日期后缀） |
| 单模型页（本次数据来源） | `claude-opus-4-8`、`claude-sonnet-4-6`、`claude-opus-4-5`（连字符 + 无日期） |

其余厂商两处一致（都用点号：`gemini-2.5-pro`、`gpt-5.4-pro`、`qwen3.6-flash`…），
只有 Anthropic 系不一致。overview 目前采用**单模型页的连字符写法**（因为它更新、
且与 `claude-fable-5-1` 一致）。请以目录接口为准确认后统一。

## B. 两处清单的模型集合差异

**main 清单有、单模型页没有** —— overview 目前**未收录**，需确认是已下架还是漏写：
`gpt-4o` · `gpt-4o-mini` · `gpt-5.2-codex` · `gpt-5.1-codex-max` · `gemini-2.5-flash` ·
`gemini-3.1-flash-lite-preview` · `kimi-k2.5`

**单模型页有、main 清单没有** —— overview 已收录，需确认确已上架：
`gpt-6-astra` · `gpt-5-pro` · `o3-pro` · `claude-fable-5-1` · `gemini-3.8-flash` ·
`deepseek-v3.1-terminus` · `grok-4.20-0309-reasoning` · `grok-4.20-0309-non-reasoning` ·
`mimo-v2.5-pro` · `step-3.7-flash`

（`claude-*` 的差异属于 A 项写法问题，不是集合差异。）

## C. 长上下文分档阈值口径不统一

单模型页里同为「200K 档」写了三种边界，overview 统一按各页原值保留，需要一次性对齐：

| 型号 | 页面原文阈值 |
|---|---|
| `grok-4.6` | `≥200,000` 进高档 |
| `grok-4.3` / `grok-4.5` / `grok-build-0.1` | `>199,999` 进高档 |
| `grok-4.20-0309-*` | `≥200,000` |
| `gemini-2.5-pro` / `gemini-3.1-pro-preview` | `>200,000` |

`≥200,000` 与 `>199,999` 等价，`>200,000` 与它们**差一个 token**。以计费代码为准。

另：main 的 `general-chat.mdx` 提过 **MiniMax M3 512K 分档**，单模型页的 MiniMax
全是两项计价、无分档。overview 按单模型页写（无分档），需确认。

## D. 已知遗留（本批未动）

- `cn/index.mdx` / `en/index.mdx` 三条死链：`api-reference/image/gpt4o-image`、
  `api-reference/task/get-status`、`api-reference/video/veo3`（媒体类，本批暂停）。
- 文本页的 `api:` 字段与示例已随恢复回到 `https://www.qingbo.dev/v1`
  （原 74 个单模型页的 `http://localhost:40081` 随页面一起删除）。若要保留一处
  本地联调地址，建议只写在 `guides/quickstart.mdx`。
- 目录表长期应由 Go 模型目录导出生成，避免 60+ 行价格再次漂移；生成脚本
  `phase3-two-rate-docs.py` 不在本仓内。
