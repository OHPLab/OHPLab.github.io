"""从 BMC Medical Ethics 论文 PDF 中导出题图与 Figure 素材。

用法: python scripts/extract-bmc-figures.py
"""
import io
from pathlib import Path

import pymupdf

PDF = Path(r"D:\迅雷下载\s12910-026-01604-2_reference.pdf")
OUT = Path(__file__).resolve().parent.parent / "images_compressed" / "bmc"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    doc = pymupdf.open(PDF)

    # 1) 题图：渲染第 1 页顶部（期刊名 + 标题 + 作者 + 收稿信息）
    page = doc[0]
    clip = pymupdf.Rect(0, 25, page.rect.width, 255)
    pix = page.get_pixmap(clip=clip, dpi=180)
    title_path = OUT / "bmc-title.png"
    pix.save(title_path)
    print(f"题图: {title_path.name} {pix.width}x{pix.height}")

    # 2) Figure 1（第 3 页）
    fig1 = doc.extract_image(doc[2].get_images(full=True)[0][0])
    p = OUT / "bmc-fig1.png"
    p.write_bytes(fig1["image"])
    print(f"Fig 1: {p.name} {fig1['width']}x{fig1['height']}")

    # 3) 第 7 页两张图：按纵向位置区分 Fig 2（上）/ Fig 3（下）
    p7 = doc[6]
    items = []
    for im in p7.get_images(full=True):
        rects = p7.get_image_rects(im[0])
        if not rects:
            continue
        items.append((rects[0].y0, im[0]))
    items.sort()

    # 过滤掉 OA 图标等小图（宽高任一小于 300px）
    items = [(_y, x) for _y, x in items if min(
        doc.extract_image(x)["width"], doc.extract_image(x)["height"]) >= 300]

    for idx, (_y, xref) in enumerate(items, start=2):
        data = doc.extract_image(xref)
        p = OUT / f"bmc-fig{idx}.png"
        p.write_bytes(data["image"])
        print(f"Fig {idx}: {p.name} {data['width']}x{data['height']}")

    print("导出完成 ->", OUT)


if __name__ == "__main__":
    main()
