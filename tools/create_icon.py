#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图标生成工具 - 为 WinPE Customizer 生成程序图标
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_winpe_icon():
    """创建 WinPE Customizer 图标"""
    
    # 创建多个尺寸的图标 (ICO 需要多个尺寸)
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    
    for size in sizes:
        # 创建图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制渐变背景圆形
        # 外圈：深蓝色
        draw.ellipse([2, 2, size-2, size-2], fill=(41, 98, 255, 255), outline=(30, 70, 200, 255), width=2)
        
        # 内圈：浅蓝色
        margin = size // 8
        draw.ellipse([margin, margin, size-margin, size-margin], fill=(100, 149, 237, 255))
        
        # 绘制 WinPE 标志 - Windows 窗口形状
        window_margin = size // 4
        window_size = size - window_margin * 2
        
        # 窗口外框
        draw.rectangle(
            [window_margin, window_margin, size-window_margin, size-window_margin],
            outline=(255, 255, 255, 255),
            width=max(2, size//32)
        )
        
        # 窗口标题栏
        titlebar_height = window_size // 4
        draw.rectangle(
            [window_margin, window_margin, size-window_margin, window_margin + titlebar_height],
            fill=(255, 255, 255, 200)
        )
        
        # 窗口四格（Windows 标志风格）
        center_x = size // 2
        center_y = window_margin + titlebar_height + (size - window_margin - window_margin - titlebar_height) // 2
        grid_size = window_size // 3
        gap = max(2, size // 64)
        
        # 四个小方块
        squares = [
            (center_x - grid_size - gap//2, center_y - grid_size - gap//2, center_x - gap//2, center_y - gap//2),  # 左上
            (center_x + gap//2, center_y - grid_size - gap//2, center_x + grid_size + gap//2, center_y - gap//2),  # 右上
            (center_x - grid_size - gap//2, center_y + gap//2, center_x - gap//2, center_y + grid_size + gap//2),  # 左下
            (center_x + gap//2, center_y + gap//2, center_x + grid_size + gap//2, center_y + grid_size + gap//2),  # 右下
        ]
        
        for square in squares:
            draw.rectangle(square, fill=(255, 255, 255, 230))
        
        images.append(img)
    
    # 确保ico目录存在
    ico_dir = Path('ico')
    ico_dir.mkdir(exist_ok=True)
    
    # 保存为 ICO 文件
    output_path = ico_dir / 'winpe_customizer.ico'
    images[0].save(output_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    
    print(f"✅ 图标已生成: {output_path}")
    print(f"   包含尺寸: {', '.join([f'{s}x{s}' for s in sizes])}")
    
    return output_path


def create_simple_icon():
    """创建简单的 PE 字母图标"""
    
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    
    for size in sizes:
        # 创建图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 渐变圆形背景
        colors = [
            (41, 98, 255),    # 深蓝
            (65, 105, 225),   # 皇家蓝
            (100, 149, 237),  # 矢车菊蓝
        ]
        
        # 绘制渐变圆
        for i, color in enumerate(colors):
            radius = size // 2 - i * (size // 10)
            if radius > 0:
                draw.ellipse([size//2-radius, size//2-radius, size//2+radius, size//2+radius], 
                           fill=color + (255,))
        
        # 尝试加载字体
        try:
            font_size = size // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # 绘制 PE 文字
        text = "PE"
        
        # 计算文字位置（居中）
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            text_width = size // 2
            text_height = size // 3
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - size // 20
        
        # 绘制文字阴影
        shadow_offset = max(1, size // 64)
        draw.text((x + shadow_offset, y + shadow_offset), text, fill=(0, 0, 0, 128), font=font)
        
        # 绘制文字
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        images.append(img)
    
    # 确保ico目录存在
    ico_dir = Path('ico')
    ico_dir.mkdir(exist_ok=True)
    
    # 保存为 ICO 文件
    output_path = ico_dir / 'winpe_simple.ico'
    images[0].save(output_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    
    print(f"✅ 简洁图标已生成: {output_path}")
    
    return output_path


def main():
    """主函数"""
    print("=" * 50)
    print("WinPE Customizer 图标生成工具")
    print("=" * 50)
    print()
    
    try:
        from PIL import Image
    except ImportError:
        print("❌ 需要安装 Pillow 库")
        print("   运行: pip install Pillow")
        return
    
    print("正在生成图标...")
    print()
    
    try:
        # 生成两种风格的图标
        icon1 = create_winpe_icon()
        print()
        icon2 = create_simple_icon()
        
        print()
        print("=" * 50)
        print("✅ 图标生成完成！")
        print("=" * 50)
        print()
        print("已生成:")
        print(f"  1. winpe_customizer.ico  - Windows 风格图标")
        print(f"  2. winpe_simple.ico      - 简洁 PE 字母图标")
        print()
        print("使用方法:")
        print("  1. 将 .ico 文件复制到项目根目录")
        print("  2. 程序会自动使用图标")
        print()
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

