"""把 data/publications.json 内联进 index.html，使其在 file:// 直接打开时也能渲染论文列表。

用法: python scripts/inline-publications.py
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
DATA = ROOT / "data" / "publications.json"

MARKER_START = "const PUBLICATIONS_FALLBACK = "
MARKER_END = ";\n"


def build_block(publications):
    payload = json.dumps(publications, ensure_ascii=False, separators=(",", ":"))
    # 防止提前闭合 <script>
    payload = payload.replace("</", "<\\/")
    return f"{MARKER_START}{payload}{MARKER_END}"


def main():
    html = HTML.read_text(encoding="utf-8")
    publications = json.loads(DATA.read_text(encoding="utf-8"))

    block = build_block(publications)

    # 1) 替换或插入内联数据块
    pattern = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), re.S)
    if pattern.search(html):
        html = pattern.sub(lambda _: block, html, count=1)
        print("已更新已存在的 PUBLICATIONS_FALLBACK 数据块")
    else:
        script_tag = "    <script>\n"
        idx = html.find(script_tag)
        if idx == -1:
            raise SystemExit("未找到 <script> 标签，无法插入内联数据")
        insert_at = idx + len(script_tag)
        html = html[:insert_at] + "        " + block + html[insert_at:]
        print("已插入 PUBLICATIONS_FALLBACK 数据块")

    HTML.write_text(html, encoding="utf-8")
    print(f"完成，共内联 {len(publications)} 条论文")


if __name__ == "__main__":
    main()
