# -*- coding: utf-8 -*-
# WaveAPI 文本模型目录数据（来源：WIP 快照 375692f 中 74 个单模型页，2026-09-05 核对价）
# price 单位 USD / 1M token。tier = 长上下文档（输入总量达到阈值后整单切换）。
V = dict(T="文本", S="流式", J="JSON", F="工具", C="缓存命中", N="原生", rT="Responses 文本", rS="Responses 流式")
VE = dict(T="text", S="streaming", J="JSON", F="tools", C="cache hit", N="native", rT="Responses text", rS="Responses streaming")

def m(id, vendor, inp, out, cr=None, cw=None, cw5=None, cw1=None, tier=None, ver="TS", proto="chat",
      limits=None, notes=None, notes_en=None, sched=False):
    return dict(id=id, vendor=vendor, price=dict(inp=inp, out=out, cr=cr, cw=cw, cw5=cw5, cw1=cw1),
                tier=tier, ver=ver, proto=proto, limits=limits, notes=notes or [], notes_en=notes_en or [], sched=sched)

T272 = dict(th="272K", op=">")
T200 = dict(th="200K", op="≥")
T256 = dict(th="256K", op=">")

MODELS = [
 # ---------- OpenAI ----------
 m("gpt-6-astra","openai",9,45,cr=0.9,cw=11.25,tier=dict(T272,inp=18,out=67.5,cr=1.8,cw=22.5),ver="TSJ",limits=("922K","12.8K"),
   notes=["不支持工具调用","`reasoning_effort` 用 `\"low\"`，不支持 `\"none\"`；不接受 `temperature`、`top_p`、`logprobs`",],
   notes_en=["tool calling is not supported","use `reasoning_effort: \"low\"`; `\"none\"` is unsupported, and `temperature`, `top_p` and `logprobs` are not supported",]),
 m("gpt-5.6-luna","openai",0.18,1.08,cr=0.018,cw=0.225,tier=dict(T272,inp=0.36,out=1.62,cr=0.036,cw=0.45),ver="TSJFC",limits=("922K","128K"),
   ),
 m("gpt-5.6-terra","openai",1.80,10.80,cr=0.18,cw=2.25,tier=dict(T272,inp=3.60,out=16.20,cr=0.36,cw=4.50),ver="TSJF",limits=("922K","12.8K")),
 m("gpt-5.6-sol","openai",3.60,18.00,cr=0.36,cw=4.50,tier=dict(T272,inp=7.20,out=27.00,cr=0.72,cw=9.00),ver="TSJF",limits=("922K","12.8K"),
   notes=[],notes_en=[]),
 m("gpt-5.5","openai",4.50,27.00,cr=0.45,tier=dict(T272,inp=9.00,out=40.50,cr=0.90),ver="TSJF",limits=("1M","12.8K"),
   notes=["无独立缓存写入价"],notes_en=["No separate cache-write rate"]),
 m("gpt-5.4","openai",2.25,13.50,cr=0.225,tier=dict(T272,inp=4.50,out=20.25,cr=0.45),ver="TSJF",limits=("1M","12.8K"),
   notes=["无独立缓存写入价"],notes_en=["No separate cache-write rate"]),
 m("gpt-5.4-pro","openai",27,162,tier=dict(T272,inp=54,out=243),ver="rTrS",proto="responses"),
 m("gpt-5.4-mini","openai",0.675,4.05,ver="TSJF"),
 m("gpt-5.4-nano","openai",0.18,1.125,ver="TSJF"),
 m("gpt-5.3-codex","openai",1.575,12.6,ver="rTrS",proto="responses"),
 m("gpt-5.2","openai",1.575,12.6,ver="TSJF"),
 m("gpt-5.2-pro","openai",18.9,151.2,ver="rTrS",proto="responses"),
 m("gpt-5.1","openai",1.125,9,ver="TSJF"),
 m("gpt-5","openai",1.125,9,ver="TSF"),
 m("gpt-5-mini","openai",0.225,1.8,ver="TSJF"),
 m("gpt-5-nano","openai",0.045,0.36,ver="TSJF"),
 m("gpt-5-pro","openai",13.5,108,ver="rTrS",proto="responses"),
 m("gpt-4.1","openai",1.8,7.2,ver="TSJF"),
 m("gpt-4.1-mini","openai",0.36,1.44,ver="TSJF"),
 m("gpt-4.1-nano","openai",0.09,0.36,ver="TSJF"),
 m("o3","openai",1.8,7.2,ver="TSJF"),
 m("o3-pro","openai",18,72,ver="rTrS",proto="responses"),
 m("o4-mini","openai",0.99,3.96,ver="TSJF"),
 m("o3-mini","openai",0.99,3.96,ver="TSJF"),
 m("o1","openai",13.5,54,ver="TSJF"),
 # ---------- Anthropic ----------
 m("claude-fable-5-1","anthropic",9.00,45.00,cr=0.225,cw5=11.25,cw1=18.00,ver="TSF",limits=("1M","128K"),
   notes=["不支持 JSON Schema 结构化输出","`tool_choice` 只接受 `\"auto\"`，`\"required\"` 与指定函数名会返回 400"],
   notes_en=["JSON Schema structured output is not supported","`tool_choice` accepts only `\"auto\"`; `\"required\"` and named functions return 400"]),
 m("claude-fable-5","anthropic",9,45,cr=0.9,cw5=11.25,cw1=18,ver="TSF",limits=("1M","128K"),
   notes=["不支持 JSON Schema 结构化输出","`tool_choice` 只接受 `\"auto\"`"],
   notes_en=["JSON Schema structured output is not supported","`tool_choice` accepts only `\"auto\"`"]),
 m("claude-opus-5","anthropic",4.50,22.50,cr=0.45,cw5=5.625,cw1=9.00,ver="TSFN",limits=("128K","16K"),
   notes=["不支持 JSON Schema 与 `json_object`","可用原生 `/v1/messages` 接口"],
   notes_en=["JSON Schema and `json_object` are not supported","the native `/v1/messages` endpoint is available"]),
 m("claude-sonnet-5","anthropic",1.80,9.00,cr=0.18,cw5=2.25,cw1=3.60,ver="TSFN",limits=("1M","128K"),
   notes=["不支持 JSON Schema 与 `json_object`","可用原生 `/v1/messages` 接口"],
   notes_en=["JSON Schema and `json_object` are not supported","the native `/v1/messages` endpoint is available"]),
 m("claude-opus-4-8","anthropic",4.5,22.5,ver="TSF"),
 m("claude-opus-4-7","anthropic",4.5,22.5,ver="TSF"),
 m("claude-opus-4-6","anthropic",4.5,22.5,ver="TSF"),
 m("claude-opus-4-5","anthropic",4.5,22.5,ver="TSF"),
 m("claude-sonnet-4-6","anthropic",2.7,13.5,ver="TSF"),
 m("claude-sonnet-4-5","anthropic",2.7,13.5,ver="TSF"),
 m("claude-haiku-4-5","anthropic",0.9,4.5,ver="TSF"),
 # ---------- Google ----------
 m("gemini-3.8-flash","google",0.675,3.375,cr=0.0675,ver="TSJFN",limits=("1M","65K")),
 m("gemini-3.7-flash","google",0.675,3.375,cr=0.0675,ver="TSJFN",limits=("1M","65K")),
 m("gemini-3.6-flash","google",1.35,6.75,cr=0.135,ver="TSJFN",limits=("1M","65K")),
 m("gemini-3.5-flash","google",1.35,8.1,ver="TSJFN"),
 m("gemini-3.5-flash-lite","google",0.27,2.25,ver="TSJF"),
 m("gemini-3.1-pro-preview","google",1.8,10.8,tier=dict(T200,op=">",inp=3.6,out=16.2),ver="TSJN"),
 m("gemini-3-flash-preview","google",0.45,2.7,ver="TSJFN"),
 m("gemini-2.5-pro","google",1.125,9,tier=dict(T200,op=">",inp=2.25,out=13.5),ver="TSJFN"),
 m("gemini-2.5-flash-lite","google",0.09,0.36,ver="TSJFN"),
 # ---------- DeepSeek ----------
 m("deepseek-v4-pro","deepseek",None,None,sched=True,ver="TSJFC",limits=("1M","393K"),notes=["按时段计价，见本节末表"],notes_en=["time-of-day pricing, see the table at the end of this section"]),
 m("deepseek-v4-flash","deepseek",None,None,sched=True,ver="TSJFC",limits=("128K","16K"),notes=["按时段计价，见本节末表"],notes_en=["time-of-day pricing, see the table at the end of this section"]),
 m("deepseek-r1-0528","deepseek",0.495,1.971,ver="TSJF"),
 m("deepseek-v3.2","deepseek",0.252,0.378,ver="TSJF"),
 m("deepseek-v3.2-exp","deepseek",0.252,0.378,ver="TSF",notes=["不提供严格 JSON Schema；与 `deepseek-v3.2` 是两个独立模型（2025-09-29 实验版）"],notes_en=["No strict JSON Schema; separate model from `deepseek-v3.2` (2025-09-29 experimental build)"]),
 m("deepseek-v3.1-terminus","deepseek",0.504,1.512,ver="TSF",notes=["不提供严格 JSON Schema；官方主 API 已不再列出该版本"],notes_en=["No strict JSON Schema; no longer listed on DeepSeek's main API"]),
 # ---------- Qwen ----------
 m("qwen3.8-max","qwen",1.485,4.4559,cr=0.1854,ver="TSJFC",limits=("983K","131K"),notes=["不支持显式 `cache_control`","`tool_choice` 用 `\"auto\"`"],notes_en=["explicit `cache_control` is not supported","use `tool_choice: \"auto\"`"]),
 m("qwen3.7-max","qwen",1.485,4.4559,ver="TSJF"),
 m("qwen3.7-plus","qwen",0.2208,0.8808,tier=dict(T256,inp=0.59472,out=2.37672),ver="TSJF"),
 m("qwen3.6-plus","qwen",0.2484,1.4859,tier=dict(T256,inp=0.9909,out=5.9418),ver="TSF"),
 m("qwen3.6-flash","qwen",0.1485,0.891,tier=dict(T256,inp=0.594,out=3.5649),ver="TSF"),
 # ---------- MiniMax ----------
 m("minimax-m3","minimax",0.27,1.08,ver="TSF"),
 m("minimax-m2.7","minimax",0.27,1.08,ver="TSF"),
 m("minimax-m2.5","minimax",0.27,1.08,ver="TSF"),
 m("minimax-m2.1","minimax",0.27,1.08,ver="TSF"),
 # ---------- Moonshot ----------
 m("kimi-k3","moonshot",2.7,13.5,cr=0.27,ver="TSJFC",limits=("1M","105K"),notes=["`tool_choice` 用 `\"auto\"`；函数调用建议给 512 以上的输出预算"],notes_en=["use `tool_choice: \"auto\"`; give function calls an output budget of 512 or more"]),
 m("kimi-k2.7-code","moonshot",0.855,3.6,ver="TSJF"),
 m("kimi-k2.7-code-highspeed","moonshot",1.71,7.2,ver="TSJF"),
 m("kimi-k2.6","moonshot",0.855,3.6,ver="TSF"),
 # ---------- xAI ----------
 m("grok-4.6","xai",1.80,5.40,cr=0.45,tier=dict(T200,inp=3.60,out=10.80,cr=0.90),ver="TSJC",limits=("500K","12.8K"),
   notes=["不支持工具调用","`max_tokens` 不是硬上限，思考可使 completion_tokens 超出"],
   notes_en=["tool calling is not supported","`max_tokens` is not a hard cap; reasoning can push completion_tokens past it"]),
 m("grok-4.5","xai",1.8,5.4,tier=dict(T200,inp=3.6,out=10.8),ver="TSJ",notes=["不支持工具调用"],notes_en=["tool calling is not supported"]),
 m("grok-4.3","xai",1.125,2.25,tier=dict(T200,inp=2.25,out=4.5),ver="TSJF"),
 m("grok-4.20-0309-reasoning","xai",1.125,2.25,tier=dict(T200,inp=2.25,out=4.5),ver="TSJF"),
 m("grok-4.20-0309-non-reasoning","xai",1.125,2.25,tier=dict(T200,inp=2.25,out=4.5),ver="TSJF"),
 m("grok-build-0.1","xai",0.9,1.8,tier=dict(T200,inp=1.8,out=3.6),ver="TSJF"),
 # ---------- Z.ai ----------
 m("glm-5.2","zai",1.26,3.96,ver="TSF"),
 m("glm-5.1","zai",1.26,3.96,ver="TSF"),
 m("glm-5","zai",0.9,2.88,ver="TSJF"),
 m("glm-4.7","zai",0.54,1.98,ver="TSJF"),
 m("glm-4.6","zai",0.54,1.98,ver="TSF"),
 # ---------- 其他 ----------
 m("mimo-v2.5-pro","other",0.3915,0.783,ver="TSJF",notes=["小米 MiMo"],notes_en=["Xiaomi MiMo"]),
 m("step-3.7-flash","other",0.18,1.035,ver="TSF",notes=["阶跃星辰 Step"],notes_en=["StepFun Step"]),
]

VENDORS = [
 ("openai","OpenAI","OpenAI"),
 ("anthropic","Anthropic","Anthropic"),
 ("google","Google Gemini","Google Gemini"),
 ("deepseek","DeepSeek","DeepSeek"),
 ("qwen","Qwen（阿里云）","Qwen (Alibaba Cloud)"),
 ("moonshot","Kimi（Moonshot）","Kimi (Moonshot)"),
 ("xai","Grok（xAI）","Grok (xAI)"),
 ("zai","GLM（Z.ai）","GLM (Z.ai)"),
 ("minimax","MiniMax","MiniMax"),
 ("other","其他","Others"),
]
