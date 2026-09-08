#!/usr/bin/env python3
"""从目录生成 cn|en/changelog/pricing.mdx：每个模型组按「发布日期 + 7 天」记一条上架定价，
停用组照记（标注下架日期），既有的「价格调整 / 计费口径」条目原样保留并按日期插入。

用法：python3 _meta/tools/pricing-changelog/gen.py [--catalog DIR] [--write]
输入：dates.json（group → YYYY-MM-DD，覆盖目录 released_at；核对过的发布日期或强制排到近两周的）
      retired.json（group → 下架日期）
      entry_overrides.json（group → 条目日期，直接指定；Midjourney / Suno 这类老产品按最近两周上架记）
不带 --write 只打印统计。数字全部转义成 \\$，避免同一行两个 $ 被当 LaTeX。
"""
import argparse, datetime, glob, json, os, re
ap = argparse.ArgumentParser(); ap.add_argument("--catalog", default=os.path.expanduser("~/Projects/_worktrees/waveapi-local/go/catalog")); ap.add_argument("--write", action="store_true")
args = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
dates = json.load(open(os.path.join(HERE, "dates.json"))) if os.path.exists(os.path.join(HERE, "dates.json")) else {}
retired = json.load(open(os.path.join(HERE, "retired.json"))) if os.path.exists(os.path.join(HERE, "retired.json")) else {}
entry_overrides = json.load(open(os.path.join(HERE, "entry_overrides.json"))) if os.path.exists(os.path.join(HERE, "entry_overrides.json")) else {}   # 直接指定条目日期（例：老产品按最近两周上架记）
FLOOR = datetime.date(2023, 5, 28)          # 站点最早的一条动态
TODAY = datetime.date.today()
FALLBACK = datetime.date(2026, 9, 1)        # 没有任何日期的组
LAG = datetime.timedelta(days=7)

def money(x):
    s = ("%.5f" % float(x)).rstrip("0").rstrip("."); return "\\$" + (s if s else "0")
def res_key(k): return re.match(r"^(\d+k|\d+p|default|base)$", k) is not None
def res_order(item):
    k = item[0]; m = re.match(r"^(\d+)(k|p)(?:_(\d+)s)?", k)
    if not m: return (9, 0, 0, k)
    return (0, int(m.group(1)) * (1000 if m.group(2) == "k" else 1), int(m.group(3) or 0), k)

# ── 目录 ──
groups = []
for f in sorted(glob.glob(os.path.join(args.catalog, "families", "*.json"))):
    d = json.load(open(f))
    for g in d["groups"]:
        name = g["group_name"]; ra = g.get("released_at")
        if name in dates: day = datetime.date.fromisoformat(dates[name])
        elif ra: day = datetime.datetime.utcfromtimestamp(ra).date()
        else: day = None
        entry = (day + LAG) if day else FALLBACK
        if entry < FLOOR: entry = FLOOR
        if entry > TODAY: entry = TODAY
        if name in entry_overrides: entry = datetime.date.fromisoformat(entry_overrides[name])
        live = {r["group_name"] for r in d.get("routes", []) if r.get("status") == 1}
        ret = retired.get(name)
        if ret is None and not (g.get("enable") and name in live): ret = ""   # 停用但没记下架日期
        if ret and entry >= datetime.date.fromisoformat(ret): continue   # 下架日不晚于上架条目日：这组在站上没真正卖过，不记
        groups.append({"family": d["family"], "name": name, "modality": g.get("modality") or "text", "pc": g.get("price_config") or {}, "cap": g.get("capabilities") or {},
                       "display": (g.get("display_name") or {}), "entry": entry, "retired": ret, "bt": g.get("billing_type")})

# ── 单价描述 ──
def desc_text(pc, lang):
    parts = []
    if "input" in pc: parts.append(("输入 %s" if lang == "cn" else "input %s") % money(pc["input"]))
    if "output" in pc: parts.append(("输出 %s" if lang == "cn" else "output %s") % money(pc["output"]))
    if "cache_read" in pc: parts.append(("缓存读 %s" if lang == "cn" else "cache read %s") % money(pc["cache_read"]))
    if "cache_write" in pc: parts.append(("缓存写 %s" if lang == "cn" else "cache write %s") % money(pc["cache_write"]))
    if "cache_write_1h" in pc: parts.append(("缓存写(1h) %s" if lang == "cn" else "cache write (1h) %s") % money(pc["cache_write_1h"]))
    s = " · ".join(parts)
    if "input_tier_threshold" in pc:
        th = pc["input_tier_threshold"]; k = ("%dK" % round(th / 1000)) if th >= 1000 else str(th)
        s += ("；输入超过 %s tokens 后输入 %s / 输出 %s" if lang == "cn" else "; above %s input tokens: input %s / output %s") % (k, money(pc.get("input_above_price", pc.get("input"))), money(pc.get("output_above_price", pc.get("output"))))
    return s + ("（每 1M tokens）" if lang == "cn" else " (per 1M tokens)")

def desc_image(pc, lang):
    ip = pc.get("image_prices") or {}
    if "image_usage_rates" in pc:
        r = pc["image_usage_rates"]; names = {"text_input": ("文本输入", "text input"), "image_input": ("图片输入", "image input"), "text_output": ("文本输出", "text output"), "image_output": ("图片输出", "image output"), "cached_text_input": ("缓存文本输入", "cached text input"), "cached_image_input": ("缓存image输入", "cached image input")}
        parts = ["%s %s" % (names.get(k, (k, k))[0 if lang == "cn" else 1], money(v)) for k, v in r.items()]
        return ("按实际 token 用量：" if lang == "cn" else "By actual token usage: ") + " · ".join(parts) + ("（每 1M tokens）" if lang == "cn" else " (per 1M tokens)")
    tiers = sorted([(k, v) for k, v in ip.items() if res_key(k) and k not in ("default", "base")], key=res_order)
    parts = ["%s %s" % (k, money(v)) for k, v in tiers]
    if not parts and ip.get("default") is not None: parts = [money(ip["default"])]
    if not parts and pc.get("base") is not None: parts = [money(pc["base"])]
    ACTION_ORDER = ["imagine", "upscale", "variation", "high-variation", "low-variation", "reroll", "zoom", "pan", "inpaint", "modal", "edit", "remix-strong", "remix-subtle", "generate"]
    actions = [(k, v) for k, v in ip.items() if not res_key(k) and not k.endswith("_fast") and not k.endswith("_turbo") and k != "ref_image" and not k.startswith("ref_image") and k in ACTION_ORDER]
    actions.sort(key=lambda kv: ACTION_ORDER.index(kv[0]))
    if actions and not tiers:
        parts = ["%s %s" % (k, money(v)) for k, v in actions[:6]]
        if len(actions) > 6: parts.append(("其余动作 %s–%s" if lang == "cn" else "other actions %s–%s") % (money(min(v for _, v in actions)), money(max(v for _, v in actions))))
    s = ("按张：" if lang == "cn" else "Per image: ") + " · ".join(parts)
    ref = [(k, v) for k, v in ip.items() if k == "ref_image" or k.endswith("_ref_image")]
    if ref: s += ("；参考图 %s / 张" if lang == "cn" else "; reference image %s each") % money(ref[0][1])
    return s

def desc_video(pc, lang):
    vp = pc.get("video_prices") or {}
    if "input" in pc and "output" in pc and "unit" in pc: return desc_text(pc, lang)
    per_sec = bool(pc.get("per_second"))
    base = sorted([(k, v) for k, v in vp.items() if res_key(k) and k not in ("default", "base")], key=res_order)
    clip = sorted([(k, v) for k, v in vp.items() if re.match(r"^(\d+p|\d+k)_\d+s$", k)], key=res_order)
    parts = []
    if per_sec and base: parts.append(" · ".join("%s %s" % (k, money(v)) for k, v in base) + ("/秒" if lang == "cn" else "/s"))
    elif clip: parts.append(("整片：" if lang == "cn" else "Per clip: ") + " · ".join("%s %s" % (k.replace("_", " "), money(v)) for k, v in clip[:8]))
    elif base: parts.append(("整片：" if lang == "cn" else "Per clip: ") + " · ".join("%s %s" % (k, money(v)) for k, v in base))
    elif pc.get("base") is not None: parts.append(("整片 %s" if lang == "cn" else "per clip %s") % money(pc["base"]))
    snd = sorted([(k, v) for k, v in vp.items() if k.endswith("_sound")], key=res_order)
    if snd: parts.append(("带声 " if lang == "cn" else "with audio ") + " · ".join("%s %s" % (k[:-6], money(v)) for k, v in snd) + ("/秒" if per_sec and lang == "cn" else "/s" if per_sec else ""))
    ref = sorted([(k, v) for k, v in vp.items() if k.endswith("_video_ref")], key=res_order)
    if ref: parts.append(("带参考视频 " if lang == "cn" else "with reference video ") + " · ".join("%s %s" % (k[:-10], money(v)) for k, v in ref) + ("/秒" if per_sec and lang == "cn" else "/s" if per_sec else ""))
    inp = sorted([(k, v) for k, v in vp.items() if k.endswith("_video_input_second")], key=res_order)
    if inp: parts.append(("参考视频每秒 " if lang == "cn" else "reference video per second ") + " · ".join("%s %s" % (k[:-19], money(v)) for k, v in inp))
    if pc.get("video_input_image_price"): parts.append(("参考图第 %d 张起 %s / 张" if lang == "cn" else "reference images beyond %d: %s each") % (pc.get("video_input_image_free_count", 0), money(pc["video_input_image_price"])))
    prefix = ("按秒：" if lang == "cn" else "Per second: ") if per_sec else ""
    return prefix + ("；" if lang == "cn" else "; ").join(parts)

def desc_audio(pc, lang):
    if "per_character" in pc: return ("%s / 1M 字符（按输入文本）" if lang == "cn" else "%s per 1M characters of input text") % money(pc["per_character"])
    if "per_minute" in pc: return ("%s / 分钟（按音频时长）" if lang == "cn" else "%s per minute of audio") % money(pc["per_minute"])
    ap_ = pc.get("audio_prices") or {}
    main = [k for k in ("generate", "extend", "cover", "lyrics", "stems", "inspo", "download") if k in ap_]
    parts = ["%s %s" % (k, money(ap_[k])) for k in main]
    rest = [v for k, v in ap_.items() if k not in main and k != "default"]
    if rest: parts.append(("其余动作 %s–%s" if lang == "cn" else "other actions %s–%s") % (money(min(rest)), money(max(rest))))
    return ("按次：" if lang == "cn" else "Per call: ") + " · ".join(parts)

def describe(g, lang):
    m = g["modality"]; pc = g["pc"]
    if not pc: return "—"
    if m == "text": return desc_text(pc, lang)
    if m == "image": return desc_image(pc, lang)
    if m == "video": return desc_video(pc, lang)
    if m == "audio": return desc_audio(pc, lang)
    return "—"

MOD = {"cn": {"text": "文本", "image": "图像", "video": "视频", "audio": "音频"}, "en": {"text": "Text", "image": "Image", "video": "Video", "audio": "Audio"}}

def launch_block(day, gs, lang):
    gs = sorted(gs, key=lambda g: (["text", "image", "video", "audio"].index(g["modality"]), g["name"]))
    n = len(gs)
    if lang == "cn": title = ("**%d 个模型上架 · 定价**" % n) if n > 1 else ("**`%s` 上架 · 定价**" % gs[0]["name"])
    else: title = ("**%d models launched · pricing**" % n) if n > 1 else ("**`%s` launched · pricing**" % gs[0]["name"])
    out = ['<Update label="%s" description="%s">' % (day.isoformat(), "模型上架" if lang == "cn" else "Model launch"), title, ""]
    for m in ("text", "image", "video", "audio"):
        rows = [g for g in gs if g["modality"] == m]
        if not rows: continue
        if n > 1: out.append("**%s**" % MOD[lang][m]); out.append("")
        out.append("| %s | %s |" % (("模型 ID", "单价（USD）") if lang == "cn" else ("Model ID", "Price (USD)"))); out.append("|---|---|")
        for g in rows:
            tag = ""
            if g["retired"]: tag = ("（已于 %s 下架）" if lang == "cn" else " (retired %s)") % g["retired"]
            elif g["retired"] == "": tag = "（已下架）" if lang == "cn" else " (retired)"
            out.append("| `%s`%s | %s |" % (g["name"], tag, describe(g, lang)))
        out.append("")
    out.append("</Update>")
    return "\n".join(out)

# ── 既有的价格调整条目 ──
def preserved(path):
    s = open(path, encoding="utf-8").read()
    head, _, body = s.partition("<Update ")
    blocks = re.findall(r"(<Update [^\n]*>.*?</Update>)", "<Update " + body, re.S)
    keep = [b for b in blocks if not re.search(r'description="(模型上架|Model launch)"', b)]
    return head.rstrip() + "\n", keep

for lang in ("cn", "en"):
    path = os.path.join(ROOT, lang, "changelog", "pricing.mdx")
    head, keep = preserved(path)
    items = []
    for b in keep:
        d = re.search(r'label="(\d{4}-\d{2}-\d{2})"', b).group(1); items.append((datetime.date.fromisoformat(d), 1, b))   # 同日：调价条目排在上架条目前面
    bydate = {}
    for g in groups: bydate.setdefault(g["entry"], []).append(g)
    for day, gs in bydate.items(): items.append((day, 0, launch_block(day, gs, lang)))
    items.sort(key=lambda x: (x[0], x[1]), reverse=True)
    body = head + "\n" + "\n\n".join(b for _, _, b in items) + "\n"
    print("%s: %d launch dates, %d preserved adjustments, %d groups, %d chars" % (lang, len(bydate), len(keep), len(groups), len(body)))
    if args.write: open(path, "w", encoding="utf-8").write(body); print("  written", path)
