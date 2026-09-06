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

## 2. 目录结构与命名

**一个上架组 = 一个家族目录**，即使这次只上一个模型：

```
cn/api-reference/<模态>/<家族>/
  overview.mdx        家族入口（是否需要见 §2.2）
  <model-id>.mdx      每个模型组一页（文件名 = 模型 ID，点号换连字符）
```

> **为什么单模型也建目录**：家族早晚会加第二个模型，那时把单页改成目录要改路径、
> 补 redirect、修全库链接。GPT Image 这次就是这么踩过来的（`image/gpt-image.mdx` →
> `image/gpt-image/`，加了 4 条 redirect）。一次建好，后面只加文件。

存量的单文件页（`seedream.mdx` / `midjourney.mdx` 等）暂不动，**等各自家族重新上架时顺手迁进目录**，
迁移时在 `docs.json` 的 `redirects` 里补上旧路径 → 新 `overview` 的跳转。

### 2.1 命名

侧边栏标签与页面 `title` 必须**同名**，并沿用全库既有惯例：

| 情况 | 中文 | English | 例 |
|---|---|---|---|
| 家族有 2 个及以上模型 | `XX 系列` | `XX Series` | `Seedream 系列` / `FLUX 系列` / `GPT Image 系列` |
| 只有一个型号 | 直接写型号名 | 同 | `Imagen 4.0` / `MiniMax H3` / `Z.ai Image` |

家族目录用 `docs.json` 的 `group` + `root` 表达，`group` 的字面值就是上表的标签，
`root` 指向 `overview`——这样侧边栏的组名本身可点击，不需要额外的入口页：

```json
{
  "group": "GPT Image 系列",
  "root": "cn/api-reference/image/gpt-image/overview",
  "expanded": true,
  "pages": [
    "cn/api-reference/image/gpt-image/gpt-image-2",
    "cn/api-reference/image/gpt-image/gpt-image-2-rev"
  ]
}
```

### 2.2 家族 overview 建不建

**不是每个家族都要**。判据：

| 家族规模 | 建 overview？ | 理由 |
|---|---|---|
| 1 个模型 | **不建** | 组里只有一页，overview 就是它的复制品。`docs.json` 里直接写成一个 page，不建 group |
| 2–3 个模型，且彼此差异小 | **不建** | 差异写在各模型页顶部的交叉提示里即可 |
| 2–3 个模型，但**计费模型或参数集合差异大** | **建** | 用户需要一个中立的地方选型（GPT Image 官方 vs 逆向差 36 倍成本，属于这一类） |
| ≥4 个模型，或家族内有多个 action 页 | **建** | 没有入口页会让侧边栏变成一串看不出关系的型号 |

> 参照：APIMart 的 `images/` 下 20 多个家族**只有 `audios/suno` 一个 overview**——因为他们的
> 家族页是按端点拆的，用户从模型列表直接点到具体端点，不存在"同家族选哪个 ID"的问题。
> 我们不同：**一个模型组 = 一个 model ID = 用户的选择单位和计费单位**，同家族多 ID 之间
> 要选型，所以 overview 在我们这儿承担的是 APIMart 没有的职责。按上表判断，不要一律建。

overview 该写什么、不该写什么：

- **要**：当前可用模型卡片（ID + 一句话能力 + 计费方式）、如何选（需求 → 推荐 → 原因）、
  家族共同点（端点 / action / 画幅 / 分辨率 / 张数等所有模型一致的部分）、一个最小可跑的 curl
- **不要**：把各模型页的参数表再抄一遍；"继续阅读"之类与顶部卡片重复的链接列表；
  未上架模型的预告

### 2.3 不按 action 拆页

APIMart 的 `midjourney/` 有 17 页、`audios/suno/` 有 30 页，是因为**他们直接代理各家原生端点**，
一个 action 就是一个 URL。

我们的媒体类统一走 `POST /v1/tasks`，**action 是请求里的一个字段，不是端点**。所以：
同一个模型组的多个 `supported_actions` 写在**同一页的一张 action 表**里，不拆页。
抄 APIMart 要抄**能力覆盖**，不要抄**页面切分**——照抄会把一页能讲完的事拆成十几页。

## 3. 合页还是拆页

一个家族上架多个模型 ID 时，按下面四项逐项比对**任意两个模型组**：

1. `supported_actions`
2. `supported_common_params` + `specific_parameters`
3. `constraints`
4. 取值集合：`aspect_ratios` / `resolutions` / `qualities` / `max_image_inputs`

判定时要分清**两类差异**：

- **结构性差异**——专有参数集合不同、支持的 action 不同、**计费模型不同**
  （按 token / 按张 / 按秒）。任意一条命中就 **拆页**：请求形状或算钱方式都不一样，
  混在一页里读者一定会抄错。
- **取值范围差异**——画幅少几种、分辨率少一档、单价不同、参考图上限不同。
  这类**不拆页**，一张模型表就能表达完；为它拆页就是在制造模板复制。
  （文本类的教训：契约相同却一模型一页，74 页里 55 页是复制品，只差模型名和日期。）

> 两个已判过的例子：
> **GPT Image** 官方 vs 逆向——5 个专有参数 vs 0 个、有画质档 vs 无、按 token vs 按张，
> 三条结构性差异 → **拆页**。
> **Nano Banana 经济版**三档——同 action、同参数集（都无专有参数）、同计费模型（按张），
> 只差画幅数量（11 / 15）、分辨率档（`1k 2k` / 仅 `1k`）和单价 → **合成一页**，
> 用一张四列模型表区分。

> GPT Image 的判定：官方线路有 5 个专有参数、3 档画质、16 张参考图上限、按 token 结算；
> 逆向线路 0 个专有参数、无画质档、15 张上限、按张固定价 → **拆页**。

---

## 4. 页面骨架

### 4.1 家族 `overview.mdx`（仅在 §2.2 判定需要时）

```
frontmatter: title（家族名）· description
一句话：本家族统一走哪个端点，选模型只改 model ID
## 当前可用模型      CardGroup，每个模型一张卡：ID + 一句话能力 + 计费方式
## 如何选            表格：需求 → 推荐模型 → 原因
## 家族共同点        所有模型都一样的部分（端点 / 画幅集合 / 分辨率 / n 的限制 / 参考图语义）
## 统一调用方式      一个最小可跑的 curl
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
4. `docs.json` —— 对应语言的分组里加 `group` / `root` / `pages`；`group` 的字面值按 §2.1
   命名（多模型 `XX 系列` / `XX Series`，单模型写型号名），并与 `overview` 的 `title` 一致；
   路径变更时补 `redirects`
5. `cn|en/changelog/models.mdx` —— **合成一条**，不要一个模型一条；只写这次真正上架的 ID
6. 价格有变动才动 `cn|en/changelog/pricing.mdx`；纯新上架不写价格条目

**收尾自查**

- [ ] 页面里出现的每个模型 ID 都能在 `GET /v1/models` 列表里查到
- [ ] 页面里出现的每个参数都在 `supported_common_params` 或 `specific_parameters` 里
- [ ] 页面里的每个价格都能在 `price_config` 里找到同一个数
- [ ] `docs.json` 里新增的每个 page 路径都有对应 `.mdx` 文件
- [ ] `docs.json` 的组名与 `overview` 的 `title` 同名，且符合 §2.1 的「系列 / 型号名」惯例
- [ ] cn 与 en 两版结构一致、模型 ID 与数字一致
- [ ] 跑一遍上面的 `$` 自查脚本，确认没有新增中招行
- [ ] 本地 `http://localhost:30084` 打开新页面确认渲染（表格是否被挤出可视区、中文粗体
      `**…**` 紧贴全角标点会失效、价格的 `$` 有没有被吃掉）

---

## 7. 已知易错点

- 🔴 **同一行出现两个 `$` 会被当成 LaTeX 数学公式**——这是最容易中招的一条，价格文档几乎行行有
  `$`。中招后 `$` 消失、中间的内容变成斜体、`**` 以字面量显示，价格直接错给用户
  （`$0.0054 → **$0.03**` 渲染成 `0.0054 → **0.03**`）。**表格和正文都会中**。
  写法：一行里出现两个及以上 `$` 时，全部转义成 `\$`。代码块内不受影响，不用转义。
  自查脚本（会跳过代码块）：

  ```bash
  python3 - <<'EOF'
  import re, glob, os
  incode = re.compile(r'^\s*```')
  for f in glob.glob("cn/**/*.mdx", recursive=True) + glob.glob("en/**/*.mdx", recursive=True):
      inb = False
      for i, line in enumerate(open(f, encoding="utf-8"), 1):
          if incode.match(line): inb = not inb; continue
          if not inb and len(re.findall(r'(?<!\\)\$', line)) >= 2:
              print(f"{f}:{i}  {line.strip()[:100]}")
  EOF
  ```

- **中文粗体失效**：收尾 `**` 紧跟在全角括号/顿号后面（如 `以**输入总量（含缓存）**判断`）
  不会渲染，要写成 `以**输入总量**（含缓存）判断`。
- **表格挤出可视区**：Mintlify 表格横向可滚但不显示滚动条，列多了第一列会被滚走。
  经验值：正文区约 700px，**控制在 5 列以内**；长说明放到表格下方的条目里。
- **`api:` frontmatter 决定 Try it 面板打哪个地址**，本地联调地址不要提交。
- **`n` 这类"当前受限"的字段**要写清是**本次验收期的限制**还是模型能力上限，
  两者含义不同。
