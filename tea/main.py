#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
茶叶冲泡定时提醒程序 - 主启动文件
Tea Brewing Timer Application - Main Entry Point

这是一个专业的红茶冲泡助手程序，帮助用户精确控制冲泡时间，
记录品茶体验，并提供个性化的UI定制功能。

版本: 2.0
日期: 2025年1月
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """检查必要的依赖库"""
    missing_deps = []
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    if missing_deps:
        error_msg = f"""
缺少必要的依赖库：{', '.join(missing_deps)}

请运行以下命令安装：
pip install {' '.join(missing_deps)}

或者运行：
pip install -r requirements.txt
        """
        messagebox.showerror("依赖库缺失", error_msg)
        return False
    
    return True

def main():
    """主函数"""
    # 设置当前工作目录为脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # 导入UI模块
        sys.path.insert(0, os.path.join(script_dir, 'UI'))
        from gal import TeaBrewingApp
        
        # 创建主窗口
        root = tk.Tk()
        
        # 设置窗口图标（如果存在）
        try:
            icon_path = os.path.join(script_dir, 'UI', 'icon.ico')
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except:
            pass
        
        # 创建应用实例
        app = TeaBrewingApp(root)
        
        # 启动主循环
        root.mainloop()
        
    except ImportError as e:
        messagebox.showerror("导入错误", f"无法导入必要模块：{str(e)}")
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("程序错误", f"程序运行出错：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()