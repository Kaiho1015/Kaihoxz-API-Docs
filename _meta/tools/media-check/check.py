#!/usr/bin/env python3
"""媒体批文档自查：目录真相 ↔ 页面。只读，不改文件。

用法：python3 _meta/tools/media-check/check.py [--catalog /path/to/go/catalog] [--files a.mdx b.mdx ...]
检查项：
  1. docs.json 里每个 page 都有 .mdx；cn/en 导航结构镜像
  2. 页面里出现的模型 ID：停用组不得出现在 api-reference 页（changelog 例外）
  3. ParamField 的字段名必须在该页所涉模型组声明的参数集合里
  4. 同一行两个未转义 $（SOP §8）
  5. SOP §7.4 黑话 grep
  6. cn/en 结构对照：二级标题序列、ParamField 数量、CodeGroup 数量
"""
import argparse, glob, json, os, re, sys
ap = argparse.ArgumentParser(); ap.add_argument("--catalog", default=os.path.expanduser("~/Projects/_worktrees/waveapi-local/go/catalog")); ap.add_argument("--files", nargs="*")
args = ap.parse_args()
ROOT = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(ROOT, "..", "..", ".."))
os.chdir(ROOT)
PLATFORM = {"model", "action", "callback_url", "callback_events", "ref_task_id", "n", "seed", "prompt"}
# ── 目录 ──
groups = {}
for f in glob.glob(os.path.join(args.catalog, "families", "*.json")):
    d = json.load(open(f))
    live = {r["group_name"] for r in d.get("routes", []) if r.get("status") == 1}
    for g in d["groups"]:
        cap = g.get("capabilities") or {}
        params = set(cap.get("supported_common_params") or []) | {p["name"] for p in cap.get("specific_parameters") or []} | PLATFORM
        # 维度专用声明（同 Go service/wave_capabilities.go commonParamDeclared）：写了取值集合就等于声明了该字段
        if cap.get("qualities") or cap.get("default_quality"): params.add("quality")
        if cap.get("aspect_ratios") or cap.get("default_aspect_ratio"): params.add("aspect_ratio")
        if cap.get("resolutions") or cap.get("default_resolution"): params.add("resolution")
        if cap.get("durations") or cap.get("duration_range") or cap.get("duration_special"): params.add("duration")
        if cap.get("default_generate_audio") is not None: params.add("generate_audio")
        # 同步音频口（/v1/audio/speech、/v1/audio/transcriptions）：字段来自 capabilities.speech 与 multipart 端点本身
        if cap.get("speech"): params |= {"input", "voice", "response_format", "speed"}
        if g.get("modality") == "audio" and "tts" not in (cap.get("supported_actions") or []) and not cap.get("supported_actions"): params |= {"file"}
        groups[g["group_name"]] = {"on": bool(g.get("enable")) and g["group_name"] in live, "params": params, "modality": g.get("modality"), "family": d["family"]}
on = {k for k, v in groups.items() if v["on"]}
problems = []
def P(kind, where, msg): problems.append((kind, where, msg))
# ── 1. docs.json ──
docs = json.load(open("docs.json"))
def walk(pages, out):
    for p in pages:
        if isinstance(p, str): out.append(p)
        else:
            if p.get("root"): out.append(p["root"])
            walk(p.get("pages", []), out)
nav = {}
for lang in docs["navigation"]["languages"]:
    out = []
    for tab in lang["tabs"]:
        for grp in tab.get("groups", []): walk(grp["pages"], out)
    nav[lang["language"]] = out
for lang, pages in nav.items():
    for p in pages:
        if not os.path.exists(p + ".mdx"): P("nav", "docs.json", f"{p} 没有对应 .mdx")
cn_set = {p[3:] for p in nav.get("cn", [])}; en_set = {p[3:] for p in nav.get("en", [])}
for p in sorted(cn_set - en_set): P("nav", "docs.json", f"cn 有 en 没有：{p}")
for p in sorted(en_set - cn_set): P("nav", "docs.json", f"en 有 cn 没有：{p}")
for f in glob.glob("cn/api-reference/**/*.mdx", recursive=True) + glob.glob("en/api-reference/**/*.mdx", recursive=True):
    if f[:-4] not in nav.get(f[:2], []): P("nav", f, "不在 docs.json 导航里（下架页可忽略）")
# ── 页面扫描 ──
files = args.files or sorted(glob.glob("cn/api-reference/**/*.mdx", recursive=True) + glob.glob("en/api-reference/**/*.mdx", recursive=True))
id_re = re.compile(r"`([a-z0-9][a-z0-9.\-]*)`")
pf_re = re.compile(r'<ParamField\s+(?:body|query|path)="([^"]+)"')
banned_cn = re.compile(r"验收|渠道|预扣|实测|联调|本轮|本批|模型组|不承诺|照抄|本页未列出|见上一节|写在表下|怎么选|拿全|就够|花多少|型号|我们|本站")
banned_en = re.compile(r"acceptance|not accepted|route-declared|quota is reserved|exercised|do not budget|when unsure|before you send it|not listed on this page", re.I)
struct = {}
for f in files:
    text = open(f, encoding="utf-8").read()
    lang = f[:2]
    ids = {m for m in id_re.findall(text) if m in groups}
    if "api-reference" in f and f[:-4] in nav.get(lang, []) and not any(seg in f for seg in ("/text/", "/tools/", "/account/", "/task/")):
        for m in sorted(ids):
            if not groups[m]["on"]: P("id", f, f"停用组 `{m}` 仍出现在页面")
        allowed = set().union(*(groups[m]["params"] for m in ids if groups[m]["on"])) if ids else set()
        for name in pf_re.findall(text):
            base = name.split("[")[0].split(".")[0]
            if ids and base not in allowed: P("param", f, f"ParamField `{name}` 不在所涉模型组声明的参数里")
    # $ / 黑话 / 结构
    inb = False; h2 = []; npf = 0; ncg = 0
    for i, line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*```", line): inb = not inb; continue
        if inb: continue
        if len(re.findall(r"(?<!\\)\$", line)) >= 2: P("dollar", f"{f}:{i}", line.strip()[:80])
        if "api-reference" in f and "changelog" not in f:
            m = (banned_cn if lang == "cn" else banned_en).search(line)
            if m: P("wording", f"{f}:{i}", f"「{m.group(0)}」 {line.strip()[:70]}")
        if line.startswith("## "): h2.append(line[3:].strip())
        if "<ParamField" in line: npf += 1
        if "<CodeGroup>" in line: ncg += 1
    struct[f] = (h2, npf, ncg)
for f in files:
    if f.startswith("cn/"):
        twin = "en/" + f[3:]
        if twin not in struct:
            if os.path.exists(twin): continue
            P("parity", f, "没有 en 同位置页"); continue
        a, b = struct[f], struct[twin]
        if len(a[0]) != len(b[0]): P("parity", f, f"二级标题数 cn={len(a[0])} en={len(b[0])}")
        if a[1] != b[1]: P("parity", f, f"ParamField 数 cn={a[1]} en={b[1]}")
        if a[2] != b[2]: P("parity", f, f"CodeGroup 数 cn={a[2]} en={b[2]}")
# ── 覆盖：启用组是否至少在一个 api-reference 页出现 ──
seen = set()
for f in glob.glob("cn/api-reference/**/*.mdx", recursive=True):
    seen |= {m for m in id_re.findall(open(f, encoding="utf-8").read()) if m in groups}
for g in sorted(on):
    if groups[g]["modality"] != "text" and g not in seen: P("coverage", "cn/api-reference", f"启用组 `{g}`（{groups[g]['family']}）没有任何页面提到")
for kind in ("nav", "coverage", "id", "param", "parity", "dollar", "wording"):
    rows = [p for p in problems if p[0] == kind]
    if rows:
        print(f"\n## {kind} ({len(rows)})")
        for _, where, msg in rows: print(f"  {where}: {msg}")
print(f"\n{len(problems)} problems" if problems else "\nOK: 0 problems")
sys.exit(1 if problems else 0)
