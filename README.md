# 翻译

面向 Minecraft 内容的 AI 辅助翻译工作流，支持视频字幕、文章等多种素材，集成 TechMC 术语库与 Minecraft Wiki 官方译名。

## 功能

- **视频字幕翻译** — 从 YouTube / Bilibili 下载字幕，保留时间轴，批量翻译
- **TechMC 术语标注** — 自动识别红石/机制类社区术语，确保译名一致
- **Minecraft Wiki 查询** — 批量或单条查询官方译名（方块、物品、实体等）
- **ASR 支持** — 对无字幕视频可选用 Whisper 自动转录（需额外安装）

## 快速开始

```bash
# 安装依赖
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

用你的 Agent 工具（OpenCode、Claude Code、Windsurf 等）打开本仓库，然后：

1. 将素材放入 `input/` 目录，或直接提供给 AI
2. 使用 `/start-translate` 命令启动翻译任务
3. 翻译结果输出至 `output/`，目录结构与输入保持一致

> [!NOTE]
> 翻译工作流由 AI Agent 驱动。`AGENTS.md` 定义了 Agent 的行为规范，无需手动调用脚本。

## 脚本

脚本供 Agent 内部调用，也可单独使用：

| 脚本 | 用途 |
|------|------|
| `scripts/download_subs.py` | 下载 YouTube / Bilibili 字幕 |
| `scripts/parse_subs.py` | 字幕分块、重组 |
| `scripts/mark_terms.py` | 标注 TechMC 术语 |
| `scripts/query_glossary.py` | 查询 TechMC 术语库 |
| `scripts/query_minecraft_wiki.py` | 查询 Minecraft Wiki 官方译名 |

## 致谢

社区术语库来自 [TechMC-Glossary](https://github.com/TechMC-Glossary/TechMC-Glossary)，以 MIT 许可证授权使用。
