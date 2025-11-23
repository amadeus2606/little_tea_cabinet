#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建欧式豪华风格背景图片
"""

from PIL import Image, ImageDraw, ImageFilter
import os

def create_luxury_background():
    """创建欧式豪华风格背景图片"""
    # 创建图片尺寸
    width, height = 1200, 800
    
    # 创建基础图片
    img = Image.new('RGB', (width, height), '#8B4513')  # 深棕色背景
    draw = ImageDraw.Draw(img)
    
    # 添加渐变效果 - 从深棕色到浅棕色
    for y in range(height):
        # 计算渐变颜色
        ratio = y / height
        r = int(139 + (205 - 139) * ratio * 0.3)  # 从139到更亮的棕色
        g = int(69 + (133 - 69) * ratio * 0.3)
        b = int(19 + (63 - 19) * ratio * 0.3)
        color = (r, g, b)
        draw.line([(0, y), (width, y)], fill=color)
    
    # 添加木纹纹理效果
    for i in range(0, width, 20):
        # 垂直木纹线条
        color_variation = int(20 * (i % 3 - 1))  # 颜色变化
        line_color = (
            max(0, min(255, 139 + color_variation)),
            max(0, min(255, 69 + color_variation)),
            max(0, min(255, 19 + color_variation))
        )
        draw.line([(i, 0), (i, height)], fill=line_color, width=2)
    
    # 添加一些装饰性的矩形区域（模拟木板）
    for i in range(3):
        for j in range(2):
            x1 = i * (width // 3) + 50
            y1 = j * (height // 2) + 100
            x2 = x1 + (width // 3) - 100
            y2 = y1 + (height // 2) - 200
            
            # 绘制装饰边框
            draw.rectangle([x1, y1, x2, y2], outline='#CD853F', width=3)
            draw.rectangle([x1+10, y1+10, x2-10, y2-10], outline='#DEB887', width=2)
    
    # 添加一些金色装饰点
    for i in range(20):
        x = (i * 60) % width
        y = (i * 40) % height
        draw.ellipse([x-3, y-3, x+3, y+3], fill='#DAA520')
    
    # 应用轻微的模糊效果，使背景更柔和
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # 保存图片
    img.save('background1.jpg', 'JPEG', quality=95)
    print("背景图片创建成功：background1.jpg")

if __name__ == "__main__":
    create_luxury_background()