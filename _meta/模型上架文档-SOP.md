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
3. 🔴 **不写具体单价，只写计费维度与口径。**（2026-09-06 Kaiho 拍，对齐 fal 与 APIMart）
   单价随上游调整——`changelog/pricing` 里 09-02、09-03、09-04 连着三天调价，
   任何硬编码进文档的数字几天内就过期，而**错的价格比没有价格更糟**。

   - **要写**：有哪些计费维度（输入 / 输出 / 缓存读 / 缓存写 / 按张 / 按秒 / 时段）、
     怎么分档、什么替代什么、`cost` 是什么单位。这些是定价页给不了的，也不会漂。
   - **不写**：任何具体金额、费率表、"约 \$0.005 一张"这类折算。
   - 每个「计费」小节配一段固定的实时价指引（原文见下）。

   > 参照：**APIMart** 的模型页一个价格数字都没有，唯一叫 pricing 的页是定价 API 参考；
   > **fal** 的 pricing 页只讲机制，原文写「Prices vary by model and may change.
   > Check the model's page or the pricing page for current rates.」——每模型价格在
   > 模型库和定价页，不在文档里。

   **例外**：`changelog/pricing` 保留数字——它记录的是「某日从 X 调到 Y」的**带日期事件**，
   不是当前价声明，删掉数字这页就没意义了。但**上架公告不带价**。

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
| 只有一个模型 | 直接写模型名 | 同 | `Imagen 4.0` / `MiniMax H3` / `Z.ai Image` |

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
| ≥4 个模型，或家族内有多个 action 页 | **建** | 没有入口页会让侧边栏变成一串看不出关系的模型名 |

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
frontmatter: title（「XX 系列」）· description
一段散文（见 §4.4）：本组统一走哪个端点，选模型只改 model ID
## 可用模型          CardGroup，每个模型一张卡：ID + 一句话能力 + 计费方式
## 如何选择          表格：需求 → 推荐模型 → 原因
## 共同点            所有模型都一样的部分（端点 / 画幅集合 / 分辨率 / n 的限制 / 参考图语义）
                    两个模型时写「两条线路的共同点」
## 统一调用方式      一个最小可跑的 curl + 一句「提交成功后返回 task_id……」
## 相关文档          见 §4.5
```

### 4.2 模型页 `<model-id>.mdx`

```
frontmatter: title · description · api（写全 URL，Mintlify 的 Try it 读这个字段）
一段散文（见 §4.4）：本模型定位 + 与同组其他模型的关系
## 快速开始          按 supported_actions 出 CodeGroup，每个 action 一个可直接跑的 curl
                    收尾一句：提交成功后返回 task_id，用 GET /v1/tasks/{task_id} 查询……
## 请求参数          ParamField：先通用后专有，逐个带 enum / default / 范围
                    末尾一句：本组不接受哪些参数 +「以上之外的参数会返回 400，不计费」
## 限制              constraints 逐条（用 message_i18n 原文）+ 上限表
## 计费              见 §5 模板
## 响应              一个真实形状的完成态 JSON + 一句 result 字段说明
## 相关文档          见 §4.5
```

**媒体类模型页不重复写任务系统**：提交、轮询、`Prefer: wait`、`Idempotency-Key`、
`callback_url` 一律链到 [提交任务](../cn/api-reference/task/submit) 与
[任务系统](../cn/docs/task-system)，模型页只写本模型独有的部分。

### 4.3 小节名固定用这一套

新页只能从这张表里挑小节名，不自造。用不上的小节直接不要，但**顺序不能变**：

| 顺序 | 中文 | English | 何时出现 |
|---|---|---|---|
| 1 | 鉴权 | Authorizations | 该接口的请求头与 Chat 不同时必写（例：`x-api-key`、`x-goog-api-key`） |
| 2 | 快速开始 | Quickstart | 媒体类模型页；按 `supported_actions` 出 CodeGroup |
| 3 | 请求参数 | Body | 必写 |
| 4 | 限制 | Limits | 有 `constraints` 时 |
| 5 | 计费 | Pricing | 媒体类必写；文本类合并进「用量与计费」 |
| 6 | 响应 | Response | 必写 |
| 7 | 可用模型 | Available models | 一页覆盖多个模型，或该入口只服务部分模型时 |
| 8 | 使用示例 | Examples | 请求体值得单独举例时（多轮、流式、参数组合） |
| 9 | 流式 | Streaming | 流式事件与非流式响应结构不同时 |
| 10 | 用量与计费 | Usage and billing | 文本类必写 |
| 11 | 当前不支持 | Not supported | 有会返回 400 的请求形状时；写成列表，收尾一句「以上请求返回 `400`，不计费」 |
| 12 | 与官方线路的区别 | Official vs reverse | 逆向线路页 |
| 13 | 相关文档 | Related | 必写 |

### 4.4 开头一段的写法

frontmatter 之后、第一个 `##` 之前只放**一段散文**，不放要点列表。这一段要回答三件事：
这个入口是什么、服务哪些模型、什么时候不该用它（指向该去的页面）。

```mdx
Anthropic 原生 Messages 接口，为已有 Anthropic SDK 的应用保留，只服务 `claude-sonnet-5`
与 `claude-opus-5`。本接口不提供 Chat 之外的额外能力，新接入建议直接用[通用对话接口](...)。
```

`description` 与这一段不要重复同一句话。

### 4.5 「相关文档」用列表，不用 CardGroup

全站统一 `- [页面名](路径)`。顺序：**同组页面 → 本组入口 → 通用接口**。

```mdx
## 相关文档

- [GPT Image 系列](/cn/api-reference/image/gpt-image/overview)
- [GPT Image 2 逆向版](/cn/api-reference/image/gpt-image/gpt-image-2-rev)
- [提交任务](/cn/api-reference/task/submit)
- [查询任务状态](/cn/api-reference/task/status)
- [任务系统](/cn/docs/task-system)
```

链接文案用**目标页的 title 原文**。改了某页 title，必须回头改所有指向它的链接文案——
`grep -rn "旧文案" cn en` 一遍。

### 4.6 固定用词

| 概念 | 全站写法 | 不要写 |
|---|---|---|
| 计费单位 | quota（`500,000 quota = 1 USD`） | 额度 / credits / 点数 |
| 模型 | 模型 | 型号 |
| 线路 | 官方版 / 逆向版 | 官方线路 / 逆向线路（作标题时）|
| 家族 | XX 系列 | XX 模型家族 |

跨页锚点先在本地站点点开验证：Mintlify 的中文锚点会去掉全角括号和冒号，
`## 请求内等待（Prefer: wait）` 的锚点是 `#请求内等待prefer-wait`，不是 `#请求内等待-prefer-wait`。

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

以及这段固定的实时价指引，直接抄进「计费」小节（英文版在 `en/` 同位置页里取）：

```mdx
<Note>
**本站文档不列具体单价。** 单价会随上游调整，写进文档迟早和实际对不上；本节只讲**计费维度与口径**。

看实时单价：`GET /v1/models` 的 `price_config`，或控制台「模型市场」。
看这一单实际花了多少：任务响应里的 `cost`（整数 quota，500,000 quota = 1 USD）。
</Note>
```

---

## 6. 上架一组时要动的地方（checklist）

1. `cn|en/api-reference/<模态>/<家族>/overview.mdx` —— 新建或在「可用模型」加卡片
2. `cn|en/api-reference/<模态>/<家族>/<model-id>.mdx` —— 每个模型一页（或按 §3 合页）
3. `cn|en/api-reference/<模态>/overview.mdx` —— 「支持的模型」加家族卡片；如果引入了新模式，
   补「模式速查」一行
4. `docs.json` —— 对应语言的分组里加 `group` / `root` / `pages`；`group` 的字面值按 §2.1
   命名（多模型 `XX 系列` / `XX Series`，单模型写模型名），并与 `overview` 的 `title` 一致；
   路径变更时补 `redirects`
5. 文本组变更还要改 `_meta/tools/text-overview/`（`data.py` 改模型、模板改通用口径、
   `gen.py` 的 `VENDOR_NOTES` 改厂商段落），然后 cn / en 两版都重新生成——
   `cn|en/api-reference/text/overview.mdx` 是生成结果，**不要直接编辑**
6. `cn|en/changelog/models.mdx` —— **合成一条**，不要一个模型一条；只写这次真正上架的 ID
7. 价格有变动才动 `cn|en/changelog/pricing.mdx`；纯新上架不写价格条目

**收尾自查**

- [ ] 页面里出现的每个模型 ID 都能在 `GET /v1/models` 列表里查到
- [ ] 页面里出现的每个参数都在 `supported_common_params` 或 `specific_parameters` 里
- [ ] 页面里**没有任何具体金额**（`grep -n '\$[0-9]'` 应当只在 changelog 里命中），
      「计费」小节带了实时价指引块
- [ ] `docs.json` 里新增的每个 page 路径都有对应 `.mdx` 文件
- [ ] `docs.json` 的组名与 `overview` 的 `title` 同名，且符合 §2.1 的「系列 / 模型名」惯例
- [ ] cn 与 en 两版结构一致、模型 ID 与数字一致
- [ ] 小节名全部出自 §4.3 的表，顺序没乱
- [ ] 「相关文档」是列表不是 CardGroup，链接文案等于目标页 title（§4.5）
- [ ] 改过任何页面 title 的话，`grep -rn "旧文案" cn en` 无残留
- [ ] 跨页锚点在本地站点点开验证过（§4.6 末尾）
- [ ] 计费单位写的是 quota，不是「额度 / credits」
- [ ] 跑一遍 §7.4 的黑话自查与 §8 的 `$` 自查脚本，两条都应无输出
- [ ] 本地 `http://localhost:30084` 打开新页面确认渲染（表格是否被挤出可视区、中文粗体
      `**…**` 紧贴全角标点会失效、价格的 `$` 有没有被吃掉）

---

## 7. 写作口径：这是给用户看的，不是给我们自己看的

**判断标准只有一条**：这句话对一个刚拿到 Key、要接我们 API 的开发者有用吗？
写的是**产品事实**（支持什么、返回什么、怎么计费），不是**我们的工作过程**
（验收到哪一步、为什么这么定、我们内部怎么叫）。

### 7.1 禁用词表

左边这些是内部黑话，**不能出现在任何 API 参考页里**：

| 内部说法 | 写成 |
|---|---|
| 首批验收期间固定为 1，这是当前接入的限制 | 生成数量，取值 `1`。每次请求返回一张图。 |
| 已验收 / 未验收 / 验收范围 / 尚未验收 | 支持 / 不支持 |
| 实测 / 联调 / 本轮 / 本批 | （删掉，或改成对行为的陈述） |
| 本渠道 / 渠道声明上限 | （删「渠道」二字）最大输入 X、最大输出 Y |
| 模型组 / 模型组里声明 | （删，直接说这个模型支不支持） |
| 在额度预扣前被拒绝（HTTP 400，不计费） | 返回 `400`，不计费 |
| 预扣 / 预扣全额退回 | 冻结额度 / 全额退款；更好的说法是「只有成功出图才计费」 |
| 不承诺 X | （改成正向陈述）X 不可用 / X 由上游决定 |
| 不要从其他模型页照抄字段 | （删。本页未列出的参数不支持，说到这里就够了） |
| 本站文档不列具体单价，因为…… | 各模型的单价见 `GET /v1/models` 的 `price_config`。（一句话，不解释我们为什么） |
| 不确定时先用 `low` 试 | `quality` 是影响成本最大的参数，默认值为 `low`。 |
| 提交前就能确定这一单花多少 | 分辨率是唯一的计费维度，提交前即可确定单次费用。 |
| 不要把 `candidatesTokenCount` 当成 `completion_tokens` | 两者语义不同：`completion_tokens` 已含思考 token。 |
| 请走 Chat 接口 / 需要 X 请用 Y | 其余模型走 Chat 接口 / 需要 X 时用 Y |
| 本页未列出的参数会返回 `400` | 以上之外的参数会返回 `400`，不计费。 |
| 见上一节 / 写在表下的 / 本页表格的来源 | 见「缓存」/ 见「模型备注」（用小节名，不用方位词） |
| 文档更新会滞后于目录 | （删。直接说目录接口是准的） |
| 自己写代码时用本页这个更直观 | 新接入推荐本端点。 |
| 一次拿全 / 还剩多少钱 / 就够了 | 一次请求取全 / 剩余余额 / 即可 |

### 7.2 三条正面规则

1. **陈述事实，不解释决定。** 文档不是给用户看的会议纪要。「我们没测过所以不敢写」是内部信息；
   对用户来说，能写进文档的就是支持的，没把握的**不写**（这也正是纪律 1 的意思）。
2. **不替读者辩解，也不教训读者。**「不要照抄」「请注意」「务必」这类祈使句尽量少用；
   把限制写清楚，读者自己会判断。
3. **说清后果，而不是说清机制。** 用户关心「传错了会怎样」（返回 400、不扣钱），
   不关心「我们在预扣前的哪一层校验拦下的」。

### 7.3 两家参照的原句

抄不准的时候照这个语感：

> **fal**：「You pay only for successful outputs, and you are never charged for server errors or
> time spent waiting in the queue.」
> 「Each model on fal has its own pricing and billing unit, visible on the model's page in the
> gallery and at fal.ai/pricing.」

> **APIMart**：「Number of images to generate. Value: `1`.」
> 「Up to 15 reference images, exceeding returns `image_urls exceeds max 15`.」
> 「Other OpenAI standard fields (`response_format`, `style`) are not supported and will be ignored.」

都是短句、陈述、第二人称，没有一句在讲他们自己的流程。

### 7.4 自查

```bash
grep -rnE "验收|渠道|预扣|实测|联调|本轮|本批|模型组|不承诺|照抄" --include=*.mdx cn/api-reference
grep -rnE "acceptance|not accepted|route-declared|quota is reserved|exercised" --include=*.mdx en/api-reference
grep -rnE "本页未列出|见上一节|写在表下|怎么选|拿全|就够|花多少|型号|我们|本站" --include=*.mdx cn/api-reference
grep -rnE "do not budget|when unsure|before you send it|not listed on this page" --include=*.mdx en/api-reference
```

四条都应当无输出。（`changelog/` 里的历史条目不在此列。）

## 8. 已知易错点

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
