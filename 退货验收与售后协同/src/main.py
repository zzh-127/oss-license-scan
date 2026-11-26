"""万象优选 · 退货验收与售后协同 — MVP 原型（训练数据）"""
import json, os, re
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent
with (BASE / "data" / "facts.json").open(encoding="utf-8") as fp:
    FACT_LIST = json.load(fp)["facts"]
FACT_INDEX = {f["id"].replace("ecommerce-returns-", ""): f for f in FACT_LIST}


def _cite(fact_id: str):
    """引用统一为 {fact_id, text}，保证解释里的每条结论都能回溯到事实。"""
    return {"fact_id": fact_id, "text": FACT_INDEX[fact_id]["text"]}


# 演示包裹数据（训练场景合成数据，节点时间戳为示意）
PARCELS = {
    "WB2026W44-001": {
        "parcel_id": "WB2026W44-001", "after_sale_ids": ["AS-88621"],
        "current_node": "queued_not_visible",
        "timeline": [
            {"node": "客户提交退货申请", "actor": "客服", "at": "2026-11-02 09:14", "status": "done"},
            {"node": "订单与政策校核", "actor": "客服/工单员", "at": "2026-11-02 09:40", "status": "done"},
            {"node": "客户寄回", "actor": "客户", "at": "2026-11-02 15:22", "status": "done"},
            {"node": "仓库签收", "actor": "收货岗", "at": "2026-11-03 08:05", "status": "done"},
            {"node": "待质检排队", "actor": "待定", "at": None,
             "status": "black_box",
             "note": "签收→排检无系统状态、无标准时限（f10），责任岗位待定"},
            {"node": "开箱与质检判定", "actor": "质检员", "at": None, "status": "pending"},
            {"node": "退款审批", "actor": "审批人", "at": None, "status": "pending"},
            {"node": "客户通知", "actor": "客服", "at": None, "status": "pending"},
        ],
    },
    "WB2026W44-002": {
        "parcel_id": "WB2026W44-002", "after_sale_ids": ["AS-88714"],
        "current_node": "refund_pending",
        "timeline": [
            {"node": "客户提交退货申请", "actor": "客服", "at": "2026-11-01 10:02", "status": "done"},
            {"node": "客户寄回", "actor": "客户", "at": "2026-11-01 16:40", "status": "done"},
            {"node": "仓库签收", "actor": "收货岗", "at": "2026-11-02 09:30", "status": "done"},
            {"node": "质检判定 PASS", "actor": "质检员", "at": "2026-11-02 14:10", "status": "done"},
            {"node": "退款审批", "actor": "审批人", "at": None,
             "status": "in_progress", "note": "涉及最终决定须由对应审批人确认（f41）"},
            {"node": "客户通知", "actor": "客服", "at": None, "status": "pending"},
        ],
    },
    "WB2026W44-003": {
        "parcel_id": "WB2026W44-003", "after_sale_ids": ["AS-88690", "AS-88691"],
        "current_node": "exception_hold",
        "timeline": [
            {"node": "客户提交退货申请", "actor": "客服", "at": "2026-11-02 11:20", "status": "done"},
            {"node": "客户寄回", "actor": "客户", "at": "2026-11-03 09:15", "status": "done"},
            {"node": "仓库签收", "actor": "收货岗", "at": "2026-11-03 10:47", "status": "done"},
            {"node": "异常暂停：一包多单", "actor": "质检员", "at": "2026-11-03 11:02",
             "status": "exception",
             "note": "包裹含 2 个订单、退回件数与申请不符，暂停判定待工单员核对（f11、f15）"},
            {"node": "开箱与质检判定", "actor": "质检员", "at": None, "status": "pending"},
            {"node": "退款审批", "actor": "审批人", "at": None, "status": "pending"},
            {"node": "客户通知", "actor": "客服", "at": None, "status": "pending"},
        ],
        # 异常待办三态：pending（待核对）→ claimed（已认领）→ closed（已关闭），f23
        "exception": {"type": "一包多单/数量不符", "assignee_role": "工单员",
                      "checklist": ["核对包裹内订单清单", "逐单核对退回件数", "结论写明核对依据"],
                      "state": "pending", "claimed_by": None, "claimed_at": None,
                      "closed_at": None},
    },
}

# 三口径完成量（f53，训练合成数据）
CALIBER = {"cs": {"name": "客服·到仓", "count": 10500},
           "wh": {"name": "仓库·验收", "count": 9847},
           "fin": {"name": "财务·到账", "count": 9402}}
CALIBER_DATE = "2026-W44"

app = FastAPI(title="退货验收与售后协同 MVP", version="0.1.0",
              description="训练场景原型：签收后状态可视化 / 异常件提示 / 三口径对账 / 事实知识问答。数据为训练合成事实。")


def _parcel_or_404(parcel_id: str):
    p = PARCELS.get(parcel_id)
    if not p:
        raise HTTPException(404, "包裹不存在（演示数据仅 WB2026W44-001/002/003）")
    return p


@app.get("/api/parcels/{parcel_id}/status")
def parcel_status(parcel_id: str):
    p = _parcel_or_404(parcel_id)
    out = {k: p[k] for k in ("parcel_id", "after_sale_ids", "current_node", "timeline")}
    if p["current_node"] == "queued_not_visible":
        out["waiting_reason"] = "queued_not_visible"  # f10 空窗
    if "exception" in p:
        out["exception"] = p["exception"]
    return out


@app.get("/api/parcels/{parcel_id}/explain")
def parcel_explain(parcel_id: str):
    p = _parcel_or_404(parcel_id)
    node = p["current_node"]
    if node == "queued_not_visible":
        text = ("仓库已签收，但尚未排上质检：签收后到排检之间没有系统状态，"
                "管理层也还没有分别量出各节点的等待时间，因此无法给出预计时间（依据 f10、f01）。")
        cites = ["f10", "f01"]
    elif node == "exception_hold":
        text = ("包裹为一包多单且退回件数与申请不符，已暂停判定，待工单员拆单核对；"
                "核对完成前不进入质检（依据 f11、f15、f25）。")
        cites = ["f11", "f15", "f25"]
    elif node == "refund_pending":
        text = ("质检判定已通过，正在退款审批；涉及最终决定须由对应审批人确认，"
                "AI 不代替审批人做决定（依据 f41）。")
        cites = ["f41"]
    else:
        text = "当前节点正常流转。"
        cites = []
    return {"parcel_id": parcel_id, "explanation": text,
            "citations": [_cite(fid) for fid in cites]}


@app.post("/api/exceptions/{parcel_id}/claim")
def claim_exception(parcel_id: str, claimant: str = "工单员"):
    """认领异常待办：只做状态流转，不自动关闭（f23）。"""
    p = _parcel_or_404(parcel_id)
    exc = p.get("exception")
    if not exc:
        raise HTTPException(404, "该包裹无异常待办")
    if exc["state"] == "closed":
        raise HTTPException(409, "异常已关闭，不能重复认领")
    if exc["state"] == "claimed" and exc["claimed_by"] != claimant:
        raise HTTPException(409, f"该异常已由 {exc['claimed_by']} 认领")
    exc["state"] = "claimed"
    exc["claimed_by"] = claimant
    exc["claimed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return {"parcel_id": parcel_id, "exception": exc,
            "sla_hint": None,  # 异常件停留时长尚无统计（方案 B 栏假设），不编造
            "note": "待办以接手人确认为完成，不自动关闭（f23）"}


@app.post("/api/exceptions/{parcel_id}/close")
def close_exception(parcel_id: str, operator: str = "工单员"):
    """由接手人确认核对完成后关闭待办（f23）。"""
    p = _parcel_or_404(parcel_id)
    exc = p.get("exception")
    if not exc:
        raise HTTPException(404, "该包裹无异常待办")
    if exc["state"] != "claimed":
        raise HTTPException(409, "需先认领再关闭")
    if exc["claimed_by"] != operator:
        raise HTTPException(409, f"只有接手人 {exc['claimed_by']} 可以关闭该待办")
    exc["state"] = "closed"
    exc["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return {"parcel_id": parcel_id, "exception": exc}


@app.get("/api/metrics/completion")
def completion(date: str = CALIBER_DATE, caliber: str = ""):
    if date != CALIBER_DATE:
        raise HTTPException(404, f"仅有 {CALIBER_DATE} 的训练快照，其他日期无数据")
    if caliber and caliber not in CALIBER:
        raise HTTPException(400, "caliber 仅支持 cs（到仓）/ wh（验收）/ fin（到账）")
    calibers = {caliber: CALIBER[caliber]} if caliber else CALIBER
    vals = [v["count"] for v in CALIBER.values()]
    diff = max(vals) - min(vals)
    return {"date": date, "calibers": calibers, "max_diff": diff,
            "diff_percent": round(diff / max(vals) * 100, 1),
            "source": "f53", "note": "三套完成口径互不一致，口径统一是收益可度量的前置（O3）"}


SYNONYMS = {
    "一包多单": ["多个订单", "件数量", "不一致"], "卡在哪": ["签收", "排检", "等待"],
    "黑箱": ["签收", "排检", "状态"], "多久": ["时长", "等待"], "红线": ["不能", "权限", "退款"],
    "自动退款": ["不能", "权限"], "慢": ["等待", "排检", "时长", "延误"],
    "卡": ["等待", "排检", "停滞"], "催": ["催问", "状态", "客服"],
    "异常件": ["异常", "不一致", "分派"], "完成": ["到仓", "验收", "到账"], "口径": ["到仓", "验收", "到账"],
    "交接": ["接手", "确认", "待办"], "权限": ["授权", "岗位", "签核"],
}
MIN_SCORE = 2.4  # 低于该分数视为无依据，避免用弱相关事实回答并列条凑数
PROJECT_NAME = "退货验收与售后协同"  # 出现在模板化事实里，检索前剔除

# 疑问词与口头语先剥离：否则「退货为什么慢」会被当成一个完整检索词，永远不命中
STOP_PHRASES = ["请问", "我想知道", "想知道", "帮我", "为什么", "为啥", "怎么样", "怎么",
                "如何", "多长时间", "多少", "是什么", "什么", "能否", "能不能", "可不可以",
                "是否", "可以", "一下", "的话", "多久", "怎么办", "处理", "怎么弄", "如何做",
                "吗", "呢", "吧", "呀", "啊", "嘛", "的", "了"]
SPLIT_RE = re.compile(r"[\s，。？?！!、；;：:,\.\(\)（）\[\]【】\"'“”‘’]+")


def bigrams(s: str):
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 1 else {s}


def query_units(q: str):
    s = q or ""
    for p in STOP_PHRASES:
        s = s.replace(p, " ")
    parts = [p.strip() for p in SPLIT_RE.split(s) if p.strip()]
    return parts or ([q.strip()] if q.strip() else [])


@app.get("/api/kb/ask")
def kb_ask(q: str):
    units = query_units(q)
    if not units:
        return {"answer": "尚无记录。", "citations": [],
                "note": "无来源不编造（f34 口径）"}
    expanded = list(units)
    joined = "".join(units)
    for k, vs in SYNONYMS.items():
        if k in q or k in joined:
            expanded.extend(vs)
    expanded = list(dict.fromkeys([e for e in expanded if e]))
    syn_only = [e for e in expanded if e not in units]

    qb = set()
    for u in units:
        qb |= bigrams(u)

    scored = []
    for f in FACT_LIST:
        # 项目名会出现在部分模板化事实里，先剔除，避免"退货验收"这类词凭字面命中把所有事实拉平
        blob = (f["text"] + f["topic"] + f["role"] + f["evidence"]).replace(PROJECT_NAME, "")
        fb = bigrams(blob)
        s = 0.0
        # 整词命中：原词权重高，同义词低一档
        s += 3.0 * sum(1 for u in units if u in blob)
        s += 1.0 * sum(1 for e in syn_only if e in blob)
        # 二元组覆盖率：短问题能命中，长句不被阈值挡在门外
        if qb:
            hit = len(qb & fb)
            s += 3.0 * hit / len(qb) + 0.4 * hit
        s += 0.3 * sum(1 for e in syn_only if bigrams(e) & fb)
        if s >= MIN_SCORE:
            scored.append((s, f))
    scored.sort(key=lambda x: -x[0])
    hits = [{"fact_id": f["id"].replace("ecommerce-returns-", ""), "text": f["text"],
             "role": f["role"], "evidence": f["evidence"]} for _, f in scored[:3]]
    if not hits:
        return {"answer": "尚无记录。", "citations": [],
                "note": "无来源不编造（f34 口径）"}
    return {"answer": "按知识库检索到的相关记录：", "citations": hits}


@app.get("/api/facts")
def facts():
    return [{"fact_id": f["id"].replace("ecommerce-returns-", ""), "text": f["text"],
             "character": f["character"], "role": f["role"], "topic": f["topic"]}
            for f in FACT_LIST]


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")


app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
