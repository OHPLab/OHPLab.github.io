# 论文数据维护说明

`publications.json` 是网站“论文发表”板块目前唯一的正式数据源，前端只读取该文件进行展示。

论文数据现阶段采用人工维护：条目应来自学院官网或已完成核对的论文信息，并在确认后写入 `publications.json`。每条正式论文应包含 `confirmed: true`、`manual: true` 和 `source_note` 字段，例如“来源：学院官网人工核对”。

`publications.pending.json` 保留为自动抓取或后续候选检查结果，不用于网页展示。`scripts/fetch-publications.js` 和 GitHub Actions 工作流仍保留，但自动抓取仅作为后续候选检查工具；当前工作流只支持 `workflow_dispatch` 手动触发，不再定时运行。
