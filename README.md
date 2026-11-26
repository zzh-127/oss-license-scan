# 万象优选 · 退货验收与售后协同

按 FDE 九阶段方法完成的教学实战项目：从业务挖掘、六角色访谈、现场调研，到 MVP 原型验证，全链路可追溯到事实编号（f01–f54）。

## 交付物

| 交付物 | 路径 | 线上演示 |
|---|---|---|
| 业务挖掘 | [docs/01_业务挖掘.md](退货验收与售后协同/docs/01_业务挖掘.md) | — |
| 调研记录（36 项任务 / 35 条事实） | [docs/02_调研记录.md](退货验收与售后协同/docs/02_调研记录.md) ｜ [JSON](退货验收与售后协同/docs/02_调研记录.json) ｜ [CSV](退货验收与售后协同/docs/02_调研记录.csv) | — |
| 现场调研分析 | [docs/03_现场调研分析.md](退货验收与售后协同/docs/03_现场调研分析.md) | — |
| MVP 设计方案 | [docs/04_MVP设计方案.md](退货验收与售后协同/docs/04_MVP设计方案.md) | — |
| 现状流程图（任务 2） | [docs/现状流程图_任务2.html](退货验收与售后协同/docs/现状流程图_任务2.html) | — |
| 项目原有资料（4 份） | [docs/项目原有资料/](退货验收与售后协同/docs/项目原有资料) | — |
| MVP 原型源码 + 事实库 | [src/](退货验收与售后协同/src) | [MVP 演示站](https://returns-mvp.app.workbuddy.host/?sharecode=CRDF2OOZ6U) |

调研智能体（知识库问答 + RAG 检索 + Harness 评分）已独立部署，可在线提问：

**https://returns-agent.app.workbuddy.host/?sharecode=FUHWPGWQAG**

## 运行 MVP 原型

```bash
cd 退货验收与售后协同/src
pip install -r requirements.txt
python main.py          # 打开 http://127.0.0.1:8000
```

- 单号时间线：`/api/parcels/{id}/status`，解释：`/api/parcels/{id}/explain`
- 异常闭环：`POST /api/exceptions/{id}/claim` → `POST /api/exceptions/{id}/close`
- 知识问答：`GET /api/kb/ask?q=...`，回答必须带事实来源，无依据时明确拒答

---

# Apache Commons CLI 开源许可证合规扫描（课程作业）

使用 **ScanCode Toolkit** 对 Apache 社区开源项目 **Apache Commons CLI 1.9.0** 进行开源许可证合规检测，输出多格式扫描报告。

- 作业课程：《开源软件构建技术》第 2 章 开源合规与许可证（平时作业 1）
- 扫描工具：ScanCode Toolkit 32.5.0（Apache-2.0，AboutCode 出品）
- 扫描对象：Apache Commons CLI 1.9.0 发布版源码
- 扫描维度：许可证（license）、版权（copyright）、包信息（package）、文件信息（info）、邮箱（email）、URL

## 目录结构

```
license-compliance-scan/
├── README.md                        # 本说明
├── run_scan.ps1                     # 一键扫描脚本（Windows PowerShell）
├── src/commons-cli-1.9.0-src/       # Apache Commons CLI 1.9.0 发布版源码
├── reports/
│   ├── commons-cli-1.9.0-scan.json  # 扫描结果 JSON（机器可读）
│   ├── commons-cli-1.9.0-scan.html  # 扫描报告 HTML（浏览器可视化）
│   └── commons-cli-1.9.0-scan.spdx  # SPDX 文档（SPDX 标准格式）
└── .venv/                           # Python 虚拟环境（ScanCode 运行环境，不入库）
```

## 运行方式

```powershell
# 1. 创建虚拟环境并安装 ScanCode Toolkit
python -m venv .venv
.venv\Scripts\pip install scancode-toolkit

# 2. 执行扫描（输出 JSON / HTML / SPDX 三种报告）
.venv\Scripts\scancode.exe -clipeu `
  --json-pp  reports\commons-cli-1.9.0-scan.json `
  --html-app reports\commons-cli-1.9.0-scan.html `
  --spdx-tv  reports\commons-cli-1.9.0-scan.spdx `
  src\commons-cli-1.9.0-src
```

也可以直接运行 `run_scan.ps1`。

## 扫描参数说明

| 参数 | 含义 |
| --- | --- |
| `-c` | 扫描版权声明（copyright） |
| `-l` | 扫描许可证（license） |
| `-i` | 收集文件基本信息（info） |
| `-p` | 收集包/依赖清单（package） |
| `-e` | 收集邮箱地址（email） |
| `-u` | 收集 URL（url） |
| `--json-pp` | 输出格式化 JSON |
| `--html-app` | 输出带页面的 HTML 报告 |
| `--spdx-tv` | 输出 SPDX 标签值格式文档 |

## 扫描结果要点

- 项目许可证：Apache-2.0（许可证文件 `LICENSE.txt` 与文件头声明）
- 完整统计以 `reports/` 下报告为准，可用浏览器打开 HTML 报告查看
