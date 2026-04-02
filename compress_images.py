#!/usr/bin/env python3
"""
图片压缩脚本 - 将图片压缩为 WebP 格式并优化尺寸
"""

import os
from PIL import Image
from pathlib import Path

# 配置
SOURCE_DIR = Path("C:/Users/xiejingyu2/Desktop/Lab_website")
OUTPUT_DIR = SOURCE_DIR / "images_compressed"

# 图片尺寸限制（根据网页显示需求调整）
MAX_WIDTH = {
    'mentor': 400,    # 导师照片
    'lab': 1200,      # 实验室照片
    'SLAB': 1200,     # SLAB 照片
    'logo': 200,      # Logo
}

# WebP 质量 (0-100，推荐 80-85 平衡质量和大小)
WEBP_QUALITY = 85

def get_max_width(filename):
    """根据文件名判断最大宽度"""
    lower_name = filename.lower()
    for prefix, width in MAX_WIDTH.items():
        if lower_name.startswith(prefix):
            return width
    return 800  # 默认最大宽度

def compress_image(input_path, output_path, max_width):
    """压缩单张图片为 WebP 格式"""
    try:
        with Image.open(input_path) as img:
            # 转换为 RGB（处理 RGBA 或其他模式）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整尺寸
            original_width, original_height = img.size
            if original_width > max_width:
                ratio = max_width / original_width
                new_height = int(original_height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                print(f"  调整尺寸: {original_width}x{original_height} -> {max_width}x{new_height}")
            
            # 保存为 WebP
            img.save(output_path, 'WEBP', quality=WEBP_QUALITY, method=6)
            
            # 计算压缩比
            original_size = input_path.stat().st_size
            compressed_size = output_path.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100
            
            print(f"  原大小: {original_size/1024/1024:.2f} MB")
            print(f"  压缩后: {compressed_size/1024/1024:.2f} MB")
            print(f"  节省: {ratio:.1f}%")
            
            return True
    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 查找所有图片
    image_files = [
        f for f in SOURCE_DIR.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    print(f"找到 {len(image_files)} 张图片需要压缩\n")
    
    total_original = 0
    total_compressed = 0
    success_count = 0
    
    for img_file in sorted(image_files):
        print(f"处理: {img_file.name}")
        
        max_width = get_max_width(img_file.stem)
        output_path = OUTPUT_DIR / f"{img_file.stem}.webp"
        
        original_size = img_file.stat().st_size
        total_original += original_size
        
        if compress_image(img_file, output_path, max_width):
            compressed_size = output_path.stat().st_size
            total_compressed += compressed_size
            success_count += 1
        
        print()
    
    # 打印汇总
    print("=" * 50)
    print(f"压缩完成: {success_count}/{len(image_files)} 张图片")
    print(f"原始总大小: {total_original/1024/1024:.2f} MB")
    print(f"压缩后总大小: {total_compressed/1024/1024:.2f} MB")
    if total_original > 0:
        print(f"总体节省: {(1 - total_compressed/total_original)*100:.1f}%")
    print(f"\n压缩后的图片保存在: {OUTPUT_DIR}")
    print("\n提示: 你可以在 HTML 中使用 <picture> 标签来兼容旧浏览器:")
    print("""
<picture>
    <source srcset="images_compressed/xxx.webp" type="image/webp">
    <img src="xxx.jpg" alt="描述" loading="lazy">
</picture>
    """)

if __name__ == "__main__":
    main()
