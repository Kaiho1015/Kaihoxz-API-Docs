# 模型上架 · 文档更新 SOP

> 后台按**组**逐批上架模型，每上架一组就按本文更新一次文档。
> 目的：不同人在不同时间写出的页面形状一致，且每个字都能在模型组里查到出处。
> 建立：2026-09-06（随 GPT Image 组上架）。

---

## 0. 三条纪律

1. **只写已上架的组**。判据是模型组同时满足 `enable = true` 且 `active_route_count > 0`。
   配了价没承接、或有承接没启用（例如 `gpt-image-1` / `gpt-image-1.5`），一律不进文档，
   也不要写成"即将上线"——上线时间不由文档承诺。
2. **参数只写声明过的**。请求字段来自 `capabilities.supported_common_params` +
   `capabilities.specific_parameters`，其余一律不写；网关会把未声明的参数在**额度预扣前**
   拒绝（HTTP 400，不计费），文档写了就是骗用户。反向也要写清楚：**本组不接受哪些常见参数**
   （例如 `seed`、`quality`），否则用户会从别的模型页抄过来。
3. **价格只写 `price_config` 里有的**。官方能力、上游价目表都不能替代本渠道配置；
   没配的维度就写"不开放"，不要按官方推断。

---

## 1. 数据从哪儿取

| 来源 | 取什么 | 备注 |
|---|---|---|
| `GET /v1/models`（公开，无需 Key） | 已启用模型的 `id` / `tags` / `price_config` / `description` | 与 C 端看到的完全一致 |
| `GET /v1/models/{id}` | 单个模型；**注意它能解析到"停用"组**，判断是否上架要以列表为准 | |
| 管理端 `GET /admin/waveapi/model-groups?modality=image&page_size=500` | `capabilities` 全量（`supported_actions` / `supported_common_params` / `specific_parameters` / `constraints` / `aspect_ratios` / `resolutions` / `qualities` / `max_image_inputs` / `default_*`）、`active_route_count`、`enable` | 后台会话下调用 |

**字段 → 文档位置对照**

| 模型组字段 | 写到哪 |
|---|---|
| `display_name` / `descriptions` | 页面标题与首段定位 |
| `supported_actions` | 「快速开始」出几个 CodeGroup 标签 |
| `supported_common_params` + `specific_parameters` | 「请求参数」逐个 `ParamField`（带 `enum` / `default` / `min`-`max`） |
| `aspect_ratios` / `resolutions` / `qualities` / `default_*` | 对应 `ParamField` 的取值与默认值 |
| `max_image_inputs` | `image_urls` 的上限 |
| `constraints[].message_i18n` | 「限制」小节，**中文用 `zh`、英文用 `en` 原文**，不要自己改写 |
| `price_config` | 「计费」小节，模板见 §4 |
| `billing_type` | 决定用哪套计费模板 |

---

## 2. 目录结构

**一个上架组 = 一个家族目录**，即使这次只上一个模型：

```
cn/api-reference/<模态>/<家族>/
  overview.mdx        家族入口：可用模型卡片 · 如何选 · 统一调用 · 家族共同点
  <model-id>.mdx      每个模型组一页（文件名 = 模型 ID，点号换连字符）
```

`docs.json` 里对应写成带 `root` 的分组，`root` 指向 `overview`：

```json
{
  "group": "GPT Image",
  "root": "cn/api-reference/image/gpt-image/overview",
  "expanded": true,
  "pages": [
    "cn/api-reference/image/gpt-image/gpt-image-2",
    "cn/api-reference/image/gpt-image/gpt-image-2-rev"
  ]
}
```

> **为什么单模型也建目录**：家族早晚会加第二个模型，那时把单页改成目录要改路径、
> 补 redirect、修全库链接。GPT Image 这次就是这么踩过来的（`image/gpt-image.mdx` →
> `image/gpt-image/`，加了 4 条 redirect）。一次建好，后面只加文件。

存量的单文件页（`seedream.mdx` / `midjourney.mdx` 等）暂不动，**等各自家族重新上架时顺手迁进目录**，
迁移时在 `docs.json` 的 `redirects` 里补上旧路径 → 新 `overview` 的跳转。

---

## 3. 合页还是拆页

一个家族上架多个模型 ID 时，按下面四项逐项比对**任意两个模型组**：

1. `supported_actions`
2. `supported_common_params` + `specific_parameters`
3. `constraints`
4. 取值集合：`aspect_ratios` / `resolutions` / `qualities` / `max_image_inputs`

- **四项全同** → **合成一页**，用一张模型表区分 ID 与价格。
  （文本类的教训：契约相同却一模型一页，74 页里 55 页是模板复制，只差模型名和日期。）
- **任一项不同** → **拆成独立页**，并在家族 overview 的「如何选」表里写清差在哪。

计费模型不同（按 token / 按张 / 按秒）**一律拆页**——计费口径是用户选型的第一依据，
混在一页里会被抄错。

> GPT Image 的判定：官方线路有 5 个专有参数、3 档画质、16 张参考图上限、按 token 结算；
> 逆向线路 0 个专有参数、无画质档、15 张上限、按张固定价 → **拆页**。

---

## 4. 页面骨架

### 4.1 家族 `overview.mdx`

```
frontmatter: title（家族名）· description
一句话：本家族统一走哪个端点，选模型只改 model ID
## 当前可用模型      CardGroup，每个模型一张卡：ID + 一句话能力 + 计费方式
## 如何选            表格：需求 → 推荐模型 → 原因
## 家族共同点        所有模型都一样的部分（端点 / 画幅集合 / 分辨率 / n 的限制 / 参考图语义）
## 统一调用方式      一个最小可跑的 curl
## 继续阅读          各模型页 + 任务系统 + 认证
```

### 4.2 模型页 `<model-id>.mdx`

```
frontmatter: title · description · api（写全 URL，Mintlify 的 Try it 读这个字段）
一句话定位（来自模型组 descriptions）+ 与同家族其他模型的关系提示
## 快速开始          按 supported_actions 出 CodeGroup，每个 action 一个可直接跑的 curl
## 请求参数          ParamField：先通用后专有，逐个带 enum / default / 范围
                    末尾一句：本组不接受哪些参数 + 未声明参数在预扣前拒绝
## 限制              constraints 逐条（用 message_i18n 原文）+ 上限表
## 计费              见 §5 模板
## 响应              一个真实形状的完成态 JSON
## 相关文档          提交任务 / 查询状态 / 任务系统 / 同家族其他页
```

**媒体类模型页不重复写任务系统**：提交、轮询、`Prefer: wait`、`Idempotency-Key`、
`callback_url` 一律链到 [提交任务](../cn/api-reference/task/submit) 与
[任务系统](../cn/docs/task-system)，模型页只写本模型独有的部分。

---

## 5. 计费小节模板

按 `price_config` 的形状选：

| `price_config` 形状 | 计费方式 | 页面要写清 |
|---|---|---|
| `image_usage_rates` + `settle_image_by_usage: true` | 按实际 token 用量结算 | 五项单价表（文本输入 / 缓存文本输入 / 图片输入 / 缓存图片输入 / 图片输出）；**预扣不是最终价**：提交时按 `image_usage_reservation` 估算预扣，完成后按实际用量结算退差；缓存价只在上游返回缓存用量时生效 |
| `base` + `image_prices` | 按张固定价 | 分辨率 → 单张价表；`image_prices.default` 是**未命中分辨率键时的兜底价**，要写出来；参考图是否加价要写 |
| `text_schedule` | 时段价 | 时段表 + "按请求开始时刻冻结价格，跨时段不重选" |

三种模板都要带的两句：

- 失败、取消或上游成功但无可交付结果 → 预扣**全额退回**。
- 最终费用以任务响应里的 `cost` 为准，`cost` 是**整数 quota 不是美元**（500,000 quota = 1 USD）。

---

## 6. 上架一组时要动的地方（checklist）

1. `cn|en/api-reference/<模态>/<家族>/overview.mdx` —— 新建或在「当前可用模型」加卡片
2. `cn|en/api-reference/<模态>/<家族>/<model-id>.mdx` —— 每个模型一页（或按 §3 合页）
3. `cn|en/api-reference/<模态>/overview.mdx` —— 「支持的模型」加家族卡片；如果引入了新模式，
   补「模式速查」一行
4. `docs.json` —— 对应语言的分组里加 `group` / `root` / `pages`；路径变更时补 `redirects`
5. `cn|en/changelog/models.mdx` —— **合成一条**，不要一个模型一条；只写这次真正上架的 ID
6. 价格有变动才动 `cn|en/changelog/pricing.mdx`；纯新上架不写价格条目

**收尾自查**

- [ ] 页面里出现的每个模型 ID 都能在 `GET /v1/models` 列表里查到
- [ ] 页面里出现的每个参数都在 `supported_common_params` 或 `specific_parameters` 里
- [ ] 页面里的每个价格都能在 `price_config` 里找到同一个数
- [ ] `docs.json` 里新增的每个 page 路径都有对应 `.mdx` 文件
- [ ] cn 与 en 两版结构一致、模型 ID 与数字一致
- [ ] 本地 `http://localhost:30084` 打开新页面确认渲染（表格是否被挤出可视区、中文粗体
      `**…**` 紧贴全角标点会失效）

---

## 7. 已知易错点

- **中文粗体失效**：收尾 `**` 紧跟在全角括号/顿号后面（如 `以**输入总量（含缓存）**判断`）
  不会渲染，要写成 `以**输入总量**（含缓存）判断`。
- **表格挤出可视区**：Mintlify 表格横向可滚但不显示滚动条，列多了第一列会被滚走。
  经验值：正文区约 700px，**控制在 5 列以内**；长说明放到表格下方的条目里。
- **`api:` frontmatter 决定 Try it 面板打哪个地址**，本地联调地址不要提交。
- **`n` 这类"当前受限"的字段**要写清是**本次验收期的限制**还是模型能力上限，
  两者含义不同。
