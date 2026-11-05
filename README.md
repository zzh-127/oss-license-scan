# Apache Commons CLI 开源许可证合规扫描

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
