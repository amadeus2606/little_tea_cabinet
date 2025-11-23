#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红茶冲泡定时提醒程序
Tea Brewing Timer Application

作者: AmaZhao
功能: 创建茶种实例，管理茶柜，定时提醒冲泡
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from PIL import Image, ImageTk, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import shutil
import uuid

class TeaBrewingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("红茶冲泡定时提醒程序")
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置主窗口最佳尺寸（考虑不同分辨率）
        if screen_width >= 1920:  # 高分辨率屏幕
            window_width = 1200
            window_height = 800
        elif screen_width >= 1366:  # 中等分辨率屏幕
            window_width = 1000
            window_height = 700
        else:  # 低分辨率屏幕
            window_width = 900
            window_height = 650
        
        # 计算窗口居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置窗口大小限制
        self.root.minsize(900, 650)  # 最小尺寸
        self.root.maxsize(1400, 900)  # 最大尺寸
        
        # 背景图片相关
        self.background_image = None
        self.background_photo = None
        self.background_label = None
        
        # 创建tea_closet文件夹
        self.tea_closet_path = os.path.join(os.path.dirname(__file__), "..", "tea_closet")
        if not os.path.exists(self.tea_closet_path):
            os.makedirs(self.tea_closet_path)
        
        # 创建record文件夹
        self.record_path = os.path.join(os.path.dirname(__file__), "..", "record")
        if not os.path.exists(self.record_path):
            os.makedirs(self.record_path)
        
        # 创建images文件夹
        self.images_path = os.path.join(self.record_path, "images")
        if not os.path.exists(self.images_path):
            os.makedirs(self.images_path)
        
        # 设置文件路径
        self.settings_path = os.path.join(self.tea_closet_path, "settings.json")
        self.tea_records_path = os.path.join(self.record_path, "tea_records.json")
        
        # 当前运行的定时器
        self.active_timers = []
        
        # 冲泡状态管理
        self.brewing_status = {
            'is_brewing': False,
            'tea_data': None,
            'current_pour': 0,
            'start_time': None,
            'next_pour_time': None,
            'remaining_time': 0,
            'skip_current': False  # 跳过当前倒茶的标志
        }
        
        # 加载背景图片
        self.load_background_image()
        
        # 定义主题配置
        self.themes = {
            "classic": {  # 米色经典主题
                "name": "经典米色",
                "bg_color": "#f5f5dc",
                "button_color": "#daa520",
                "button_color_2": "#cd853f",
                "button_color_3": "#228b22",
                "button_color_4": "#dc143c",
                "button_color_5": "#4169e1",
                "button_color_6": "#708090",
                "text_color": "#8b4513",
                "text_color_2": "#a0522d",
                "text_color_3": "#2f4f4f",
                "font_family": "微软雅黑",
                "title_font": "华文行楷",
                "subtitle_font": "楷体"
            },
            "wooden": {  # 欧式豪华木柜主题
                "name": "欧式豪华",
                "bg_color": "#2d1b14",  # 深胡桃木背景
                "button_color": "#cd853f",  # 古铜金色主按钮
                "button_color_2": "#b8860b",  # 深金色次要按钮
                "button_color_3": "#1a4a3a",  # 深绿色（模拟皮质）
                "button_color_4": "#8b1538",  # 酒红色重要按钮
                "button_color_5": "#4a3728",  # 深棕色辅助按钮
                "button_color_6": "#5d4e37",  # 橄榄棕色
                "text_color": "#f5f5dc",  # 象牙白主文字
                "text_color_2": "#daa520",  # 金色强调文字
                "text_color_3": "#cd853f",  # 古铜色辅助文字
                "sidebar_bg": "#1a4a3a",  # 深绿色侧边栏背景（皮质效果）
                "sidebar_text": "#f5f5dc",  # 侧边栏文字颜色
                "accent_color": "#8b1538",  # 酒红色强调色
                "border_color": "#5d4e37",  # 边框颜色
                "font_family": "Georgia",  # 更优雅的衬线字体
                "title_font": "Times New Roman",
                "subtitle_font": "Georgia"
            },
            "modern": {  # 现代简约主题
                "name": "现代简约",
                "bg_color": "#2c3e50",
                "button_color": "#3498db",
                "button_color_2": "#e74c3c",
                "button_color_3": "#27ae60",
                "button_color_4": "#e67e22",
                "button_color_5": "#9b59b6",
                "button_color_6": "#95a5a6",
                "text_color": "#ecf0f1",
                "text_color_2": "#bdc3c7",
                "text_color_3": "#34495e",
                "font_family": "Segoe UI",
                "title_font": "Segoe UI",
                "subtitle_font": "Segoe UI"
            }
        }
        
        # 自定义UI设置
        self.custom_background_path = None
        self.custom_button_background_path = None
        
        # 加载设置
        self.current_theme = "wooden"  # 默认主题为深棕木柜
        self.load_settings()
        
        # 应用当前主题
        self.apply_theme()
        
        # 创建主界面
        self.create_main_interface()

        # 初始化顶层窗口列表，用于ESC关闭弹窗（Toplevel windows）
        # 中文注释：用于记录所有打开的Toplevel弹窗，以便按下ESC时优先关闭弹窗而不是直接返回主页。
        self.toplevels = []  # 记录当前打开的所有Toplevel窗口引用

        # 全局绑定 ESC 键，实现“返回”功能（keyboard event）(๑•̀ㅂ•́)و✧
        # 逻辑：
        # 1) 若存在打开的Toplevel窗口，则按ESC会优先关闭最近打开的弹窗；
        # 2) 若没有弹窗，则按ESC会返回到主界面；
        # 这样可以符合用户直觉的“返回/关闭”操作。
        try:
            self.root.bind_all("<Escape>", self.handle_escape)
        except tk.TclError:
            pass
    
    def load_settings(self):
        """加载设置"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.current_theme = settings.get('theme', 'wooden')
                self.custom_background_path = settings.get('custom_background', None)
                self.custom_button_background_path = settings.get('custom_button_background', None)
        except Exception as e:
            print(f"加载设置失败: {e}")
            self.current_theme = "wooden"
            self.custom_background_path = None
            self.custom_button_background_path = None
    
    def save_settings(self):
        """保存设置"""
        try:
            settings = {
                'theme': self.current_theme,
                'custom_background': self.custom_background_path,
                'custom_button_background': self.custom_button_background_path
            }
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败：{str(e)}")
    
    def apply_theme(self):
        """应用主题"""
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme['bg_color'])
    
    def get_theme_config(self):
        """获取当前主题配置"""
        return self.themes[self.current_theme]
    
    def load_background_image(self):
        """加载背景图片"""
        try:
            # 优先使用自定义背景图片
            bg_path = None
            if hasattr(self, 'custom_background_path') and self.custom_background_path and os.path.exists(self.custom_background_path):
                bg_path = self.custom_background_path
            else:
                # 使用默认背景图片
                bg_path = os.path.join(os.path.dirname(__file__), "background1.jpg")
            
            if bg_path and os.path.exists(bg_path):
                # 加载图片
                self.background_image = Image.open(bg_path)
                # 获取窗口尺寸
                self.root.update_idletasks()
                window_width = self.root.winfo_width() if self.root.winfo_width() > 1 else 800
                window_height = self.root.winfo_height() if self.root.winfo_height() > 1 else 600
                
                # 调整图片大小以适应窗口
                img_width, img_height = self.background_image.size
                aspect_ratio = img_width / img_height
                
                if window_width / window_height > aspect_ratio:
                    # 窗口更宽，以高度为准
                    new_height = window_height
                    new_width = int(new_height * aspect_ratio)
                else:
                    # 窗口更高，以宽度为准
                    new_width = window_width
                    new_height = int(new_width / aspect_ratio)
                
                # 调整图片大小
                resized_image = self.background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.background_photo = ImageTk.PhotoImage(resized_image)
                
        except Exception as e:
            print(f"加载背景图片失败: {e}")
            self.background_image = None
            self.background_photo = None
    
    def setup_background(self, parent):
        """设置背景图片"""
        if self.background_photo:
            # 创建背景标签
            if self.background_label:
                self.background_label.destroy()
            
            self.background_label = tk.Label(parent, image=self.background_photo)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # 确保背景在最底层
            self.background_label.lower()

    def create_main_interface(self):
        """创建主界面"""
        # 清空窗口
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
        except tk.TclError:
            pass
        
        # 重置边栏相关属性（但保持冲泡状态）
        if hasattr(self, 'sidebar'):
            delattr(self, 'sidebar')
        if hasattr(self, 'status_frame'):
            delattr(self, 'status_frame')
        if hasattr(self, 'countdown_label'):
            delattr(self, 'countdown_label')
        
        # 重新加载背景图片以适应当前窗口大小
        self.load_background_image()
        
        # 设置背景图片
        self.setup_background(self.root)
        
        # 获取当前主题配置
        theme = self.get_theme_config()
        
        # 创建主容器框架（半透明）
        main_container = tk.Frame(self.root, bg='')
        main_container.pack(fill='both', expand=True)
        
        # 创建左侧主内容区域（半透明背景）
        main_content = tk.Frame(main_container, bg='#F5F5DC', relief='raised', bd=2)
        main_content.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        
        # 创建右侧边栏（豪华风格）
        sidebar_bg = theme.get('sidebar_bg', theme['text_color_3'])
        self.sidebar = tk.Frame(main_container, bg=sidebar_bg, width=250, relief='raised', bd=4)
        self.sidebar.pack(side='right', fill='y', padx=(10, 20), pady=20)
        self.sidebar.pack_propagate(False)  # 防止边栏收缩
        
        # 标题（增强视觉效果，添加背景）
        title_frame = tk.Frame(main_content, bg='#8B4513', relief='ridge', bd=3)
        title_frame.pack(pady=20, padx=20, fill='x')
        
        title_label = tk.Label(
            title_frame, 
            text="🍵 红茶冲泡定时提醒程序 🍵", 
            font=(theme['title_font'], 24, "bold"),
            bg='#8B4513',
            fg='#F5F5DC',
            padx=20,
            pady=10
        )
        title_label.pack()
        
        # 副标题（优雅风格，添加背景）
        subtitle_frame = tk.Frame(main_content, bg='#CD853F', relief='groove', bd=2)
        subtitle_frame.pack(pady=5, padx=40, fill='x')
        
        subtitle_label = tk.Label(
            subtitle_frame,
            text="专业红茶品尝家的冲泡助手",
            font=(theme['subtitle_font'], 14, "italic"),
            bg='#CD853F',
            fg='#2F4F2F',
            padx=15,
            pady=5
        )
        subtitle_label.pack()
        
        # 主按钮框架（添加背景）
        button_frame = tk.Frame(main_content, bg='#F5F5DC', relief='sunken', bd=2)
        button_frame.pack(pady=50, padx=30, fill='x')
        
        # 创建茶种按钮（豪华风格，增强对比度）
        create_button = tk.Button(
            button_frame,
            text="🌿 创建新茶种",
            font=(theme['font_family'], 16, "bold"),
            bg='#8B4513',
            fg='#F5F5DC',
            activebackground='#A0522D',
            activeforeground='#FFFAF0',
            relief='raised',
            bd=4,
            padx=20,
            pady=12,
            cursor='hand2'
        )
        create_button.pack(pady=12, fill='x', padx=20)
        create_button.config(command=self.show_create_tea_page)
        
        # 茶柜按钮（增强对比度）
        closet_button = tk.Button(
            button_frame,
            text="🏺 我的茶柜",
            font=(theme['font_family'], 16, "bold"),
            bg='#2F4F2F',
            fg='#F5F5DC',
            activebackground='#228B22',
            activeforeground='#FFFAF0',
            relief='raised',
            bd=4,
            padx=20,
            pady=12,
            cursor='hand2'
        )
        closet_button.pack(pady=12, fill='x', padx=20)
        closet_button.config(command=self.show_tea_closet_page)
        
        # 设置按钮（增强对比度）
        settings_button = tk.Button(
            button_frame,
            text="⚙️ 设置",
            font=(theme['font_family'], 16, "bold"),
            bg='#B8860B',
            fg='#F5F5DC',
            activebackground='#DAA520',
            activeforeground='#FFFAF0',
            relief='raised',
            bd=4,
            padx=20,
            pady=12,
            cursor='hand2'
        )
        settings_button.pack(pady=12, fill='x', padx=20)
        settings_button.config(command=self.show_settings_page)
        
        # 茶记按钮（新增）
        tea_notes_button = tk.Button(
            button_frame,
            text="📝 茶记",
            font=(theme['font_family'], 16, "bold"),
            bg='#8B008B',
            fg='#F5F5DC',
            activebackground='#9932CC',
            activeforeground='#FFFAF0',
            relief='raised',
            bd=4,
            padx=20,
            pady=12,
            cursor='hand2'
        )
        tea_notes_button.pack(pady=12, fill='x', padx=20)
        tea_notes_button.config(command=self.show_tea_notes_page)
        
        # 信息标签（添加背景）
        info_frame = tk.Frame(main_content, bg='#DEB887', relief='groove', bd=2)
        info_frame.pack(pady=30, padx=40, fill='x')
        
        info_label = tk.Label(
            info_frame,
            text="让每一泡茶都恰到好处 ☕",
            font=(theme['font_family'], 12, "italic"),
            bg='#DEB887',
            fg='#8B4513',
            padx=15,
            pady=8
        )
        info_label.pack()
        
        # 创建边栏内容
        self.create_sidebar_content()

    # ========================= ESC 返回/关闭 相关工具方法 =========================
    def handle_escape(self, event=None):
        """按下 ESC 键后的统一处理逻辑
        中文说明：
        - 如果有弹窗（Toplevel window）打开，优先关闭最近一个弹窗；
        - 如果没有弹窗，则返回主界面。
        专业术语：keyboard event, Toplevel window, destroy
        """
        try:
            # 若有已注册的弹窗，优先关闭最近打开的一个
            if hasattr(self, 'toplevels') and self.toplevels:
                # 逆序遍历，找到还存在的最后一个弹窗并关闭
                for w in reversed(self.toplevels):
                    try:
                        if w and w.winfo_exists():
                            w.destroy()
                            return
                    except tk.TclError:
                        continue
            # 没有弹窗则返回主页
            self.create_main_interface()
        except Exception:
            # 兜底处理，避免异常导致键盘事件失效
            try:
                self.create_main_interface()
            except Exception:
                pass

    def register_toplevel(self, window: tk.Toplevel):
        """注册一个 Toplevel 弹窗，使其支持 ESC 关闭并参与统一管理
        中文说明：
        - 将窗口加入管理列表，方便handle_escape统一处理；
        - 同时为该窗口绑定自身范围内的ESC关闭（window.bind）；
        专业术语：register, Toplevel, bind, Destroy event
        """
        try:
            if not hasattr(self, 'toplevels'):
                self.toplevels = []
            # 记录该弹窗
            self.toplevels.append(window)

            # 在弹窗自身范围内绑定 ESC，按下即可关闭该弹窗 ╰(°▽°)╯
            try:
                window.bind("<Escape>", lambda e, w=window: w.destroy())
            except tk.TclError:
                pass

            # 当弹窗销毁时，从列表中移除（避免残留引用）
            def _on_destroy(event, w=window):
                try:
                    if hasattr(self, 'toplevels') and w in self.toplevels:
                        self.toplevels.remove(w)
                except Exception:
                    pass
            try:
                window.bind("<Destroy>", _on_destroy)
            except tk.TclError:
                pass
        except Exception:
            pass
    
    def create_sidebar_content(self):
        """创建边栏内容"""
        theme = self.get_theme_config()
        
        # 使用专门的侧边栏背景色（如果有的话）
        sidebar_bg = theme.get('sidebar_bg', theme['text_color_3'])
        sidebar_text = theme.get('sidebar_text', theme['text_color'])
        
        # 边栏标题
        sidebar_title = tk.Label(
            self.sidebar,
            text="🍵 冲泡状态",
            font=(theme['font_family'], 16, "bold"),
            bg=sidebar_bg,
            fg=sidebar_text,
            relief='raised',
            bd=2
        )
        sidebar_title.pack(pady=(20, 10))
        
        # 分隔线（增强视觉效果）
        separator = tk.Frame(self.sidebar, height=3, bg=theme.get('border_color', theme['text_color_2']), relief='sunken', bd=1)
        separator.pack(fill='x', padx=20, pady=5)
        
        # 冲泡状态显示区域
        self.status_frame = tk.Frame(self.sidebar, bg=sidebar_bg, relief='sunken', bd=2)
        self.status_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 初始化边栏显示
        self.update_sidebar_display()
        
        # 启动定时更新
        self.update_countdown()
    
    def update_sidebar_display(self):
        """更新边栏显示内容"""
        # 检查边栏和状态框架是否存在
        if not hasattr(self, 'sidebar') or not hasattr(self, 'status_frame'):
            return
        
        try:
            # 检查组件是否仍然有效
            if not self.status_frame.winfo_exists():
                return
        except tk.TclError:
            return
        
        theme = self.get_theme_config()
        
        # 清空状态框架
        try:
            for widget in self.status_frame.winfo_children():
                widget.destroy()
        except tk.TclError:
            return
        
        if self.brewing_status['is_brewing']:
            # 显示冲泡中的茶信息
            tea_data = self.brewing_status['tea_data']
            
            # 使用专门的侧边栏颜色
            sidebar_bg = theme.get('sidebar_bg', theme['text_color_3'])
            sidebar_text = theme.get('sidebar_text', theme['text_color'])
            
            try:
                # 茶名（增强视觉效果）
                tea_name_label = tk.Label(
                    self.status_frame,
                    text=f"茶种: {tea_data['name']}",
                    font=(theme['font_family'], 12, "bold"),
                    bg=sidebar_bg,
                    fg=sidebar_text,
                    wraplength=200,
                    relief='ridge',
                    bd=2,
                    padx=10,
                    pady=5
                )
                tea_name_label.pack(pady=(0, 10), padx=5, fill='x')
                
                # 当前倒茶次数
                pour_info_label = tk.Label(
                    self.status_frame,
                    text=f"第 {self.brewing_status['current_pour']} / {tea_data['pour_count']} 次",
                    font=(theme['font_family'], 11),
                    bg=sidebar_bg,
                    fg=theme.get('accent_color', theme['text_color_2']),
                    relief='groove',
                    bd=1,
                    padx=8,
                    pady=3
                )
                pour_info_label.pack(pady=(0, 15), padx=5, fill='x')
                
                # 倒计时显示（豪华风格）
                self.countdown_label = tk.Label(
                    self.status_frame,
                    text="计算中...",
                    font=(theme['font_family'], 14, "bold"),
                    bg=theme.get('accent_color', theme['button_color']),
                    fg='white',
                    relief='raised',
                    bd=3,
                    padx=10,
                    pady=8
                )
                self.countdown_label.pack(pady=(0, 10), padx=5, fill='x')
                
                # 下次倒茶时间
                next_pour_label = tk.Label(
                    self.status_frame,
                    text="下次倒茶倒计时",
                    font=(theme['font_family'], 10),
                    bg=sidebar_bg,
                    fg=theme['text_color_2'],
                    relief='flat',
                    padx=5,
                    pady=2
                )
                next_pour_label.pack(padx=5)
                
                # 提前结束按钮（豪华风格）
                skip_button = tk.Button(
                    self.status_frame,
                    text="⏭ 提前结束本次倒茶",
                    font=(theme['font_family'], 10, "bold"),
                    bg=theme.get('accent_color', theme['button_color_4']),
                    fg='white',
                    activebackground=theme['button_color_2'],
                    activeforeground='white',
                    relief='raised',
                    bd=3,
                    padx=12,
                    pady=6,
                    command=self.skip_current_pour,
                    cursor='hand2'
                )
                skip_button.pack(pady=(20, 10), padx=5, fill='x')
            except tk.TclError:
                return
            
        else:
            try:
                # 使用专门的侧边栏颜色
                sidebar_bg = theme.get('sidebar_bg', theme['text_color_3'])
                sidebar_text = theme.get('sidebar_text', theme['text_color'])
                
                # 显示无冲泡状态（豪华风格）
                no_brewing_label = tk.Label(
                    self.status_frame,
                    text="暂无冲泡中的茶",
                    font=(theme['font_family'], 12, "italic"),
                    bg=sidebar_bg,
                    fg=theme['text_color_2'],
                    relief='sunken',
                    bd=2,
                    padx=15,
                    pady=20
                )
                no_brewing_label.pack(pady=50, padx=10, fill='x')
            except tk.TclError:
                return
    
    def update_countdown(self):
        """更新倒计时显示"""
        try:
            if (self.brewing_status['is_brewing'] and 
                hasattr(self, 'countdown_label') and 
                self.countdown_label.winfo_exists()):
                
                current_time = time.time()
                if self.brewing_status['next_pour_time']:
                    remaining = self.brewing_status['next_pour_time'] - current_time
                    if remaining > 0:
                        minutes = int(remaining // 60)
                        seconds = int(remaining % 60)
                        self.countdown_label.config(text=f"{minutes}分{seconds}秒")
                    else:
                        self.countdown_label.config(text="准备倒茶")
        except (tk.TclError, AttributeError):
            pass
        
        # 每秒更新一次
        try:
            self.root.after(1000, self.update_countdown)
        except tk.TclError:
            pass

    def show_create_tea_page(self):
        """显示创建茶种页面"""
        # 停止所有定时器并清理状态
        self.stop_all_timers()
        
        # 清空窗口
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
        except tk.TclError:
            pass
        
        # 获取当前主题配置
        theme = self.get_theme_config()
        
        # 创建滚动框架
        canvas = tk.Canvas(self.root, bg=theme['bg_color'])
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=theme['bg_color'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 标题
        title_label = tk.Label(
            scrollable_frame,
            text="🌿 创建新茶种",
            font=(theme['title_font'], 20, "bold"),
            bg=theme['bg_color'],
            fg=theme['text_color']
        )
        title_label.pack(pady=20)
        
        # 创建输入框架
        input_frame = tk.Frame(scrollable_frame, bg=theme['bg_color'])
        input_frame.pack(padx=50, pady=20, fill='both', expand=True)
        
        # 茶名输入
        tk.Label(input_frame, text="茶叶名称:", font=(theme['font_family'], 12, "bold"), bg=theme['bg_color'], fg=theme['text_color']).grid(row=0, column=0, sticky='w', pady=5)
        self.tea_name_entry = tk.Entry(input_frame, font=(theme['font_family'], 12), width=30)
        self.tea_name_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # 水温输入
        tk.Label(input_frame, text="冲泡水温(°C):", font=(theme['font_family'], 12, "bold"), bg=theme['bg_color'], fg=theme['text_color']).grid(row=1, column=0, sticky='w', pady=5)
        self.water_temp_entry = tk.Entry(input_frame, font=(theme['font_family'], 12), width=30)
        self.water_temp_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # 茶具输入
        tk.Label(input_frame, text="使用茶具:", font=(theme['font_family'], 12, "bold"), bg=theme['bg_color'], fg=theme['text_color']).grid(row=2, column=0, sticky='w', pady=5)
        self.tea_ware_entry = tk.Entry(input_frame, font=(theme['font_family'], 12), width=30)
        self.tea_ware_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # 水量输入
        tk.Label(input_frame, text="水量(ml):", font=(theme['font_family'], 12, "bold"), bg=theme['bg_color'], fg=theme['text_color']).grid(row=3, column=0, sticky='w', pady=5)
        self.water_amount_entry = tk.Entry(input_frame, font=(theme['font_family'], 12), width=30)
        self.water_amount_entry.grid(row=3, column=1, pady=5, padx=10)
        
        # 茶叶重量输入
        tk.Label(input_frame, text="茶叶重量(g):", font=(theme['font_family'], 12, "bold"), bg=theme['bg_color'], fg=theme['text_color']).grid(row=4, column=0, sticky='w', pady=5)
        self.tea_weight_entry = tk.Entry(input_frame, font=(theme['font_family'], 12), width=30)
        self.tea_weight_entry.grid(row=4, column=1, pady=5, padx=10)
        
        # 是否加奶
        tk.Label(input_frame, text="是否加奶:", font=(theme['font_family'], 12, "bold"), bg=theme['bg_color'], fg=theme['text_color']).grid(row=5, column=0, sticky='w', pady=5)
        self.add_milk_var = tk.BooleanVar()
        milk_checkbox = tk.Checkbutton(input_frame, text="加奶", variable=self.add_milk_var, font=(theme['font_family'], 12), bg=theme['bg_color'], fg=theme['text_color_2'])
        milk_checkbox.grid(row=5, column=1, sticky='w', pady=5, padx=10)
        
        # 倒茶次数和时间设置
        tk.Label(input_frame, text="倒茶设置:", font=(theme['font_family'], 12, "bold"), bg=theme['bg_color'], fg=theme['text_color']).grid(row=6, column=0, sticky='w', pady=10)
        
        # 倒茶次数
        tk.Label(input_frame, text="倒茶次数:", font=(theme['font_family'], 10), bg=theme['bg_color'], fg=theme['text_color_2']).grid(row=7, column=0, sticky='w', pady=5)
        self.pour_count_var = tk.IntVar(value=3)
        pour_count_spinbox = tk.Spinbox(input_frame, from_=1, to=10, textvariable=self.pour_count_var, font=(theme['font_family'], 10), width=10)
        pour_count_spinbox.grid(row=7, column=1, sticky='w', pady=5, padx=10)
        
        # 动态创建时间输入框
        self.time_entries_frame = tk.Frame(input_frame, bg=theme['bg_color'])
        self.time_entries_frame.grid(row=8, column=0, columnspan=2, pady=10, sticky='w')
        
        self.time_entries = []
        self.update_time_entries()
        
        # 绑定倒茶次数变化事件
        self.pour_count_var.trace('w', lambda *args: self.update_time_entries())
        
        # 按钮框架
        button_frame = tk.Frame(scrollable_frame, bg=theme['bg_color'])
        button_frame.pack(pady=30)
        
        # 保存按钮
        save_button = tk.Button(
            button_frame,
            text="💾 保存茶种",
            font=(theme['font_family'], 14, "bold"),
            bg=theme['button_color_3'],
            fg='white',
            width=12,
            height=2,
            command=self.save_tea_instance
        )
        save_button.pack(side='left', padx=10)
        
        # 返回按钮
        back_button = tk.Button(
            button_frame,
            text="🔙 返回主页",
            font=(theme['font_family'], 14, "bold"),
            bg=theme['button_color_4'],
            fg='white',
            width=12,
            height=2,
            command=self.create_main_interface
        )
        back_button.pack(side='left', padx=10)
        
        # 配置滚动
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def update_time_entries(self):
        """更新时间输入框"""
        # 清空现有的时间输入框
        for widget in self.time_entries_frame.winfo_children():
            widget.destroy()
        
        # 获取当前主题配置
        theme = self.get_theme_config()
        
        self.time_entries = []
        count = self.pour_count_var.get()
        
        tk.Label(self.time_entries_frame, text="各次倒茶时间间隔:", font=(theme['font_family'], 10, "bold"), bg=theme['bg_color'], fg=theme['text_color']).grid(row=0, column=0, columnspan=4, sticky='w', pady=5)
        
        for i in range(count):
            tk.Label(self.time_entries_frame, text=f"第{i+1}次:", font=(theme['font_family'], 10), bg=theme['bg_color'], fg=theme['text_color_2']).grid(row=i+1, column=0, sticky='w', pady=2)
            
            # 分钟输入
            minutes_var = tk.IntVar(value=0 if i == 0 else 1)
            minutes_spinbox = tk.Spinbox(self.time_entries_frame, from_=0, to=60, textvariable=minutes_var, font=(theme['font_family'], 10), width=5)
            minutes_spinbox.grid(row=i+1, column=1, pady=2, padx=2)
            tk.Label(self.time_entries_frame, text="分", font=(theme['font_family'], 10), bg=theme['bg_color'], fg=theme['text_color_2']).grid(row=i+1, column=2, sticky='w', pady=2)
            
            # 秒数输入
            seconds_var = tk.IntVar(value=30 if i == 0 else 0)
            seconds_spinbox = tk.Spinbox(self.time_entries_frame, from_=0, to=59, textvariable=seconds_var, font=(theme['font_family'], 10), width=5)
            seconds_spinbox.grid(row=i+1, column=3, pady=2, padx=2)
            tk.Label(self.time_entries_frame, text="秒", font=(theme['font_family'], 10), bg=theme['bg_color'], fg=theme['text_color_2']).grid(row=i+1, column=4, sticky='w', pady=2)
            
            self.time_entries.append({'minutes': minutes_var, 'seconds': seconds_var})

    def save_tea_instance(self):
        """保存茶种实例"""
        try:
            # 获取输入数据
            tea_name = self.tea_name_entry.get().strip()
            if not tea_name:
                messagebox.showerror("错误", "请输入茶叶名称！")
                return
            
            water_temp = self.water_temp_entry.get().strip()
            if not water_temp:
                messagebox.showerror("错误", "请输入冲泡水温！")
                return
            
            tea_ware = self.tea_ware_entry.get().strip()
            if not tea_ware:
                messagebox.showerror("错误", "请输入使用的茶具！")
                return
            
            water_amount = self.water_amount_entry.get().strip()
            if not water_amount:
                messagebox.showerror("错误", "请输入水量！")
                return
            
            tea_weight = self.tea_weight_entry.get().strip()
            if not tea_weight:
                messagebox.showerror("错误", "请输入茶叶重量！")
                return
            
            # 获取倒茶时间
            pour_times = []
            for i, time_entry in enumerate(self.time_entries):
                minutes = time_entry['minutes'].get()
                seconds = time_entry['seconds'].get()
                total_seconds = minutes * 60 + seconds
                if total_seconds <= 0:
                    messagebox.showerror("错误", f"第{i+1}次倒茶时间必须大于0！")
                    return
                pour_times.append(total_seconds)
            
            # 创建茶种数据
            tea_data = {
                "name": tea_name,
                "water_temp": water_temp,
                "tea_ware": tea_ware,
                "water_amount": water_amount,
                "tea_weight": tea_weight,
                "add_milk": self.add_milk_var.get(),
                "pour_count": self.pour_count_var.get(),
                "pour_times": pour_times,
                "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 保存到文件
            filename = f"tea_{tea_name.replace(' ', '_')}.json"
            filepath = os.path.join(self.tea_closet_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tea_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", f"茶种 '{tea_name}' 已成功保存到茶柜！")
            self.create_main_interface()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def show_tea_closet_page(self):
        """显示茶柜页面"""
        # 停止所有定时器并清理状态
        self.stop_all_timers()
        
        # 清空窗口
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
        except tk.TclError:
            pass
        
        # 获取当前主题配置
        theme = self.get_theme_config()
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="🗄️ 我的茶柜",
            font=(theme['title_font'], 20, "bold"),
            bg=theme['bg_color'],
            fg=theme['text_color']
        )
        title_label.pack(pady=20)
        
        # 茶种列表框架
        list_frame = tk.Frame(self.root, bg=theme['bg_color'])
        list_frame.pack(padx=50, pady=20, fill='both', expand=True)
        
        # 创建列表框和滚动条
        listbox_frame = tk.Frame(list_frame, bg=theme['bg_color'])
        listbox_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.tea_listbox = tk.Listbox(
            listbox_frame,
            font=(theme['font_family'], 12),
            yscrollcommand=scrollbar.set,
            selectmode='single',
            height=15,
            bg=theme['text_color_3'],
            fg=theme['bg_color']
        )
        self.tea_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.tea_listbox.yview)
        
        # 加载茶种列表
        self.load_tea_list()
        
        # 按钮框架
        button_frame = tk.Frame(self.root, bg=theme['bg_color'])
        button_frame.pack(pady=20)
        
        # 查看详情按钮
        view_button = tk.Button(
            button_frame,
            text="👁️ 查看详情",
            font=(theme['font_family'], 12, "bold"),
            bg=theme['button_color_5'],
            fg='white',
            width=12,
            command=self.view_tea_details
        )
        view_button.pack(side='left', padx=10)
        
        # 开始冲泡按钮
        brew_button = tk.Button(
            button_frame,
            text="☕ 开始冲泡",
            font=(theme['font_family'], 12, "bold"),
            bg=theme['button_color'],
            fg='white',
            width=12,
            command=self.start_brewing
        )
        brew_button.pack(side='left', padx=10)
        
        # 删除茶种按钮
        delete_button = tk.Button(
            button_frame,
            text="🗑️ 删除茶种",
            font=(theme['font_family'], 12, "bold"),
            bg=theme['button_color_4'],
            fg='white',
            width=12,
            command=self.delete_tea
        )
        delete_button.pack(side='left', padx=10)
        
        # 返回按钮
        back_button = tk.Button(
            button_frame,
            text="🔙 返回主页",
            font=(theme['font_family'], 12, "bold"),
            bg=theme['button_color_6'],
            fg='white',
            width=12,
            command=self.create_main_interface
        )
        back_button.pack(side='left', padx=10)

    def load_tea_list(self):
        """加载茶种列表"""
        self.tea_listbox.delete(0, tk.END)
        self.tea_files = []
        
        try:
            for filename in os.listdir(self.tea_closet_path):
                if filename.endswith('.json') and filename.startswith('tea_'):
                    filepath = os.path.join(self.tea_closet_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            tea_data = json.load(f)
                        
                        display_text = f"🍵 {tea_data['name']} - {tea_data['water_temp']}°C - {tea_data['pour_count']}次倒茶"
                        self.tea_listbox.insert(tk.END, display_text)
                        self.tea_files.append(filepath)
                    except Exception as e:
                        print(f"加载茶种文件 {filename} 失败: {e}")
            
            if not self.tea_files:
                self.tea_listbox.insert(tk.END, "暂无茶种，请先创建茶种实例")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载茶柜失败：{str(e)}")

    def view_tea_details(self):
        """查看茶种详情"""
        selection = self.tea_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个茶种！")
            return
        
        try:
            filepath = self.tea_files[selection[0]]
            with open(filepath, 'r', encoding='utf-8') as f:
                tea_data = json.load(f)
            
            # 获取当前主题配置
            theme = self.get_theme_config()
            
            # 创建详情窗口
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"茶种详情 - {tea_data['name']}")
            detail_window.geometry("500x600")
            detail_window.configure(bg=theme['bg_color'])
            # 注册弹窗以支持 ESC 关闭（Toplevel window register）
            self.register_toplevel(detail_window)
            
            # 详情内容
            detail_text = f"""
🍵 茶叶名称: {tea_data['name']}
🌡️ 冲泡水温: {tea_data['water_temp']}°C
🫖 使用茶具: {tea_data['tea_ware']}
💧 水量: {tea_data['water_amount']}ml
⚖️ 茶叶重量: {tea_data.get('tea_weight', '未设置')}g
🥛 是否加奶: {'是' if tea_data['add_milk'] else '否'}
🔢 倒茶次数: {tea_data['pour_count']}次

⏰ 倒茶时间安排:
"""
            
            for i, pour_time in enumerate(tea_data['pour_times']):
                minutes = pour_time // 60
                seconds = pour_time % 60
                if minutes > 0:
                    time_str = f"{minutes}分{seconds}秒" if seconds > 0 else f"{minutes}分"
                else:
                    time_str = f"{seconds}秒"
                detail_text += f"   第{i+1}次: {time_str}后\n"
            
            detail_text += f"\n📅 创建时间: {tea_data['created_time']}"
            
            text_widget = tk.Text(
                detail_window,
                font=(theme['font_family'], 12),
                bg=theme['text_color_3'],
                fg=theme['bg_color'],
                wrap='word',
                padx=20,
                pady=20
            )
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            text_widget.insert('1.0', detail_text)
            text_widget.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("错误", f"查看详情失败：{str(e)}")

    def start_brewing(self):
        """开始冲泡"""
        selection = self.tea_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个茶种！")
            return
        
        try:
            filepath = self.tea_files[selection[0]]
            with open(filepath, 'r', encoding='utf-8') as f:
                tea_data = json.load(f)
            
            # 确认开始冲泡
            result = messagebox.askyesno(
                "开始冲泡",
                f"确定要开始冲泡 '{tea_data['name']}' 吗？\n\n"
                f"水温: {tea_data['water_temp']}°C\n"
                f"茶具: {tea_data['tea_ware']}\n"
                f"水量: {tea_data['water_amount']}ml\n"
                f"倒茶次数: {tea_data['pour_count']}次\n"
                f"是否加奶: {'是' if tea_data['add_milk'] else '否'}"
            )
            
            if result:
                # 停止之前的定时器
                self.stop_all_timers()
                
                # 开始新的冲泡定时器
                self.start_brewing_timers(tea_data)
                messagebox.showinfo("开始冲泡", f"'{tea_data['name']}' 冲泡计时已开始！\n请准备好茶具和热水。")
                
        except Exception as e:
            messagebox.showerror("错误", f"开始冲泡失败：{str(e)}")

    def start_brewing_timers(self, tea_data):
        """启动冲泡定时器"""
        # 更新冲泡状态
        self.brewing_status['is_brewing'] = True
        self.brewing_status['tea_data'] = tea_data
        self.brewing_status['current_pour'] = 1
        self.brewing_status['start_time'] = time.time()
        self.brewing_status['skip_current'] = False
        
        def timer_thread():
            for i, pour_time in enumerate(tea_data['pour_times']):
                # 更新下次倒茶时间
                self.brewing_status['next_pour_time'] = time.time() + pour_time
                self.brewing_status['current_pour'] = i + 1
                
                # 更新边栏显示
                self.root.after(0, self.update_sidebar_display)
                
                # 等待指定时间，但要检查跳过标志
                start_time = time.time()
                while time.time() - start_time < pour_time:
                    if self.brewing_status['skip_current']:
                        # 重置跳过标志
                        self.brewing_status['skip_current'] = False
                        break
                    time.sleep(0.1)  # 短暂休眠，避免CPU占用过高
                
                # 在主线程中显示提醒
                self.root.after(0, lambda i=i: self.show_brewing_reminder(tea_data, i+1))
            
            # 冲泡完成，重置状态
            self.brewing_status['is_brewing'] = False
            self.brewing_status['tea_data'] = None
            self.brewing_status['current_pour'] = 0
            self.brewing_status['next_pour_time'] = None
            self.brewing_status['skip_current'] = False
            self.root.after(0, self.update_sidebar_display)
            
            # 冲泡完成后显示评价界面
            self.root.after(1000, lambda: self.show_tea_evaluation(tea_data))
        
        # 在新线程中运行定时器
        timer = threading.Thread(target=timer_thread, daemon=True)
        timer.start()
        self.active_timers.append(timer)

    def show_brewing_reminder(self, tea_data, pour_number):
        """显示冲泡提醒"""
        # 获取当前主题配置
        theme = self.get_theme_config()
        
        # 创建提醒窗口
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title("冲泡提醒")
        reminder_window.geometry("400x300")
        reminder_window.configure(bg=theme['text_color_2'])
        # 注册弹窗以支持 ESC 关闭（Toplevel window register）
        self.register_toplevel(reminder_window)
        
        # 置顶显示
        reminder_window.attributes('-topmost', True)
        
        # 居中显示
        reminder_window.transient(self.root)
        reminder_window.grab_set()
        
        # 提醒内容
        tk.Label(
            reminder_window,
            text="⏰ 冲泡提醒 ⏰",
            font=(theme['title_font'], 18, "bold"),
            bg=theme['text_color_2'],
            fg=theme['bg_color']
        ).pack(pady=20)
        
        tk.Label(
            reminder_window,
            text=f"🍵 {tea_data['name']}",
            font=(theme['font_family'], 16, "bold"),
            bg=theme['text_color_2'],
            fg=theme['text_color_3']
        ).pack(pady=10)
        
        tk.Label(
            reminder_window,
            text=f"第 {pour_number} 次倒茶",
            font=(theme['font_family'], 20, "bold"),
            bg=theme['text_color_2'],
            fg=theme['button_color_4']
        ).pack(pady=20)
        
        if tea_data['add_milk'] and pour_number == tea_data['pour_count']:
            tk.Label(
                reminder_window,
                text="🥛 记得加奶哦！",
                font=(theme['font_family'], 14),
                bg=theme['text_color_2'],
                fg=theme['button_color_5']
            ).pack(pady=10)
        
        # 确认按钮
        tk.Button(
            reminder_window,
            text="✅ 已完成",
            font=(theme['font_family'], 14, "bold"),
            bg=theme['button_color_3'],
            fg='white',
            width=10,
            command=reminder_window.destroy
        ).pack(pady=20)
        
        # 播放系统提示音
        reminder_window.bell()

    def show_tea_evaluation(self, tea_data):
        """显示茶叶评价界面"""
        theme = self.get_theme_config()
        
        # 创建评价窗口
        eval_window = tk.Toplevel(self.root)
        eval_window.title("茶记评价")
        # 注册弹窗以支持 ESC 关闭（Toplevel window register）
        self.register_toplevel(eval_window)
        
        # 获取屏幕尺寸
        screen_width = eval_window.winfo_screenwidth()
        screen_height = eval_window.winfo_screenheight()
        
        # 设置评价窗口最佳尺寸
        window_width = 600
        window_height = 750
        
        # 计算窗口居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        eval_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置窗口大小限制
        eval_window.minsize(550, 700)
        eval_window.maxsize(700, 850)
        
        eval_window.configure(bg=theme['text_color_2'])
        
        # 设置背景
        self.setup_background(eval_window)
        
        # 置顶显示
        eval_window.attributes('-topmost', True)
        eval_window.transient(self.root)
        eval_window.grab_set()
        
        # 主框架
        main_frame = tk.Frame(eval_window, bg='#F5F5DC', relief='raised', bd=3)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text="🍵 茶记评价",
            font=(theme['title_font'], 20, "bold"),
            bg='#F5F5DC',
            fg='#8B4513'
        )
        title_label.pack(pady=20)
        
        # 茶种信息
        tea_info_label = tk.Label(
            main_frame,
            text=f"茶种：{tea_data['name']}",
            font=(theme['font_family'], 14, "bold"),
            bg='#F5F5DC',
            fg='#2F4F2F'
        )
        tea_info_label.pack(pady=10)
        
        # 美味值评分
        rating_frame = tk.Frame(main_frame, bg='#F5F5DC')
        rating_frame.pack(pady=20)
        
        tk.Label(
            rating_frame,
            text="美味值评分 (1-10星):",
            font=(theme['font_family'], 14, "bold"),
            bg='#F5F5DC',
            fg='#8B4513'
        ).pack()
        
        # 星级评分
        star_frame = tk.Frame(rating_frame, bg='#F5F5DC')
        star_frame.pack(pady=10)
        
        self.rating_var = tk.IntVar(value=5)
        self.star_buttons = []
        
        for i in range(1, 11):
            star_btn = tk.Button(
                star_frame,
                text="⭐",
                font=("Arial", 16),
                bg='#F5F5DC',
                fg='#FFD700' if i <= 5 else '#D3D3D3',
                relief='flat',
                bd=0,
                command=lambda x=i: self.update_rating(x)
            )
            star_btn.pack(side='left', padx=2)
            self.star_buttons.append(star_btn)
        
        # 评分显示
        self.rating_display = tk.Label(
            rating_frame,
            text="当前评分: 5/10",
            font=(theme['font_family'], 12),
            bg='#F5F5DC',
            fg='#8B4513'
        )
        self.rating_display.pack(pady=5)
        
        # 图片上传区域
        image_frame = tk.Frame(main_frame, bg='#F5F5DC')
        image_frame.pack(pady=10, fill='x')
        
        tk.Label(
            image_frame,
            text="茶记图片:",
            font=(theme['font_family'], 14, "bold"),
            bg='#F5F5DC',
            fg='#8B4513'
        ).pack(anchor='w')
        
        # 图片选择按钮
        image_button_frame = tk.Frame(image_frame, bg='#F5F5DC')
        image_button_frame.pack(fill='x', pady=5)
        
        self.selected_image_path = None
        self.image_preview_label = None
        
        select_image_btn = tk.Button(
            image_button_frame,
            text="📷 添加图片",
            font=(theme['font_family'], 12, "bold"),
            bg='#4169E1',
            fg='white',
            activebackground='#6495ED',
            relief='raised',
            bd=2,
            padx=15,
            pady=5,
            command=self.select_image
        )
        select_image_btn.pack(side='left', padx=5)
        
        # 清除图片按钮
        self.clear_image_btn = tk.Button(
            image_button_frame,
            text="🗑️ 清除图片",
            font=(theme['font_family'], 12),
            bg='#DC143C',
            fg='white',
            activebackground='#FF6347',
            relief='raised',
            bd=2,
            padx=15,
            pady=5,
            command=self.clear_selected_image,
            state='disabled'
        )
        self.clear_image_btn.pack(side='left', padx=5)
        
        # 图片预览区域
        self.image_preview_frame = tk.Frame(image_frame, bg='#F5F5DC', relief='sunken', bd=2)
        self.image_preview_frame.pack(fill='x', pady=5)
        
        # 笔记输入
        notes_frame = tk.Frame(main_frame, bg='#F5F5DC')
        notes_frame.pack(pady=10, fill='both', expand=True)
        
        tk.Label(
            notes_frame,
            text="品茶笔记:",
            font=(theme['font_family'], 14, "bold"),
            bg='#F5F5DC',
            fg='#8B4513'
        ).pack(anchor='w')
        
        self.notes_text = tk.Text(
            notes_frame,
            height=6,
            width=50,
            font=(theme['font_family'], 11),
            bg='#FFFAF0',
            fg='#2F4F2F',
            relief='sunken',
            bd=2,
            wrap='word'
        )
        self.notes_text.pack(pady=10, fill='both', expand=True)
        
        # 按钮框架
        button_frame = tk.Frame(main_frame, bg='#F5F5DC')
        button_frame.pack(pady=20)
        
        # 保存按钮
        save_btn = tk.Button(
            button_frame,
            text="💾 保存茶记",
            font=(theme['font_family'], 14, "bold"),
            bg='#228B22',
            fg='white',
            activebackground='#32CD32',
            relief='raised',
            bd=3,
            padx=20,
            pady=10,
            command=lambda: self.save_tea_record(tea_data, eval_window)
        )
        save_btn.pack(side='left', padx=10)
        
        # 取消按钮
        cancel_btn = tk.Button(
            button_frame,
            text="❌ 取消",
            font=(theme['font_family'], 14, "bold"),
            bg='#DC143C',
            fg='white',
            activebackground='#FF6347',
            relief='raised',
            bd=3,
            padx=20,
            pady=10,
            command=eval_window.destroy
        )
        cancel_btn.pack(side='left', padx=10)
    
    def update_rating(self, rating):
        """更新星级评分"""
        self.rating_var.set(rating)
        
        # 更新星星显示
        for i, btn in enumerate(self.star_buttons):
            if i < rating:
                btn.config(fg='#FFD700')  # 金色
            else:
                btn.config(fg='#D3D3D3')  # 灰色
        
        # 更新评分显示
        self.rating_display.config(text=f"当前评分: {rating}/10")
    
    def select_image(self):
        """选择图片文件"""
        file_types = [
            ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("GIF文件", "*.gif"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择茶记图片",
            filetypes=file_types
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.show_image_preview()
            self.clear_image_btn.config(state='normal')
    
    def clear_selected_image(self):
        """清除选中的图片"""
        self.selected_image_path = None
        self.clear_image_preview()
        self.clear_image_btn.config(state='disabled')
    
    def show_image_preview(self):
        """显示图片预览"""
        if not self.selected_image_path:
            return
        
        try:
            # 清除之前的预览
            self.clear_image_preview()
            
            # 加载并调整图片大小
            image = Image.open(self.selected_image_path)
            
            # 计算缩放比例，保持宽高比
            max_width, max_height = 300, 200
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 创建预览标签
            self.image_preview_label = tk.Label(
                self.image_preview_frame,
                image=photo,
                bg='#F5F5DC'
            )
            self.image_preview_label.image = photo  # 保持引用
            self.image_preview_label.pack(pady=10)
            
            # 显示文件名
            filename = os.path.basename(self.selected_image_path)
            filename_label = tk.Label(
                self.image_preview_frame,
                text=f"已选择: {filename}",
                font=('Arial', 10),
                bg='#F5F5DC',
                fg='#666666'
            )
            filename_label.pack()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            self.selected_image_path = None
            self.clear_image_btn.config(state='disabled')
    
    def clear_image_preview(self):
        """清除图片预览"""
        for widget in self.image_preview_frame.winfo_children():
            widget.destroy()
    
    def save_tea_record(self, tea_data, eval_window):
        """保存茶记录"""
        rating = self.rating_var.get()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        if not notes:
            messagebox.showwarning("提示", "请输入品茶笔记！")
            return
        
        # 处理图片保存（Image save）
        # 中文说明：使用 getattr 安全获取 selected_image_path，避免未选择图片时出现 AttributeError。
        # 专业术语：AttributeError, getattr, fallback
        image_filename = None
        selected_image_path = getattr(self, 'selected_image_path', None)
        if selected_image_path:
            try:
                # 生成唯一的图片文件名（timestamp + 原扩展名）
                timestamp = str(int(time.time() * 1000))
                file_extension = os.path.splitext(selected_image_path)[1]
                image_filename = f"tea_image_{timestamp}{file_extension}"
                
                # 复制图片到 images 文件夹（copy2 保留 metadata）
                images_dir = os.path.join(self.record_path, 'images')
                destination_path = os.path.join(images_dir, image_filename)
                shutil.copy2(selected_image_path, destination_path)
            except Exception as e:
                messagebox.showerror("错误", f"保存图片失败: {str(e)}")
                return
        
        # 创建记录（Record create）
        # 中文说明：使用 dict.get 安全读取可能不存在的字段（如 intervals），避免 KeyError 导致无法保存。
        try:
            record = {
                'id': str(int(time.time() * 1000)),  # 使用时间戳作为ID
                'tea_name': tea_data['name'],
                'rating': int(rating) if isinstance(rating, (int, float)) else 0,
                'notes': notes,
                'brewing_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'pour_count': tea_data.get('pour_count', 0),
                'add_milk': tea_data.get('add_milk', False),
                'image_filename': image_filename,  # 添加图片文件名
                'brewing_params': {
                    'pour_times': tea_data.get('pour_times', []),
                    'intervals': tea_data.get('intervals', [])
                }
            }
        except Exception as e:
            messagebox.showerror("错误", f"创建茶记录失败：{str(e)}")
            return
        
        # 读取现有记录
        records = self.load_tea_records()
        records.append(record)
        
        # 保存记录
        try:
            with open(self.tea_records_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", "茶记保存成功！")
            eval_window.destroy()
            # 保存成功后，重置选中的图片路径，避免下次误用（cleanup）╰(°▽°)╯
            try:
                self.selected_image_path = None
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def load_tea_records(self):
        """加载茶记录"""
        if not os.path.exists(self.tea_records_path):
            return []
        
        try:
            with open(self.tea_records_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def show_tea_notes_page(self):
        """显示茶记页面"""
        # 清除现有内容
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 重新加载和设置背景
        self.load_background_image()
        self.setup_background(self.root)
        
        # 获取主题配置
        theme = self.get_theme_config()
        
        # 主容器
        main_container = tk.Frame(self.root, bg='#F5F5DC', relief='raised', bd=3)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 标题框架
        title_frame = tk.Frame(main_container, bg='#DEB887', relief='groove', bd=2)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="📝 茶记管理",
            font=(theme['title_font'], 24, "bold"),
            bg='#DEB887',
            fg='#8B4513',
            pady=15
        )
        title_label.pack()
        
        # 内容框架
        content_frame = tk.Frame(main_container, bg='#F5F5DC')
        content_frame.pack(fill='both', expand=True)
        
        # 左侧：记录列表
        left_frame = tk.Frame(content_frame, bg='#F5F5DC', relief='sunken', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 列表标题
        list_title = tk.Label(
            left_frame,
            text="历史茶记",
            font=(theme['font_family'], 16, "bold"),
            bg='#F5F5DC',
            fg='#8B4513'
        )
        list_title.pack(pady=10)
        
        # 记录列表框架
        list_frame = tk.Frame(left_frame, bg='#F5F5DC')
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # 列表框
        self.records_listbox = tk.Listbox(
            list_frame,
            font=(theme['font_family'], 11),
            bg='#FFFAF0',
            fg='#2F4F2F',
            selectbackground='#DEB887',
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.records_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.records_listbox.yview)
        
        # 右侧：详情和操作
        right_frame = tk.Frame(content_frame, bg='#F5F5DC', relief='sunken', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # 详情标题
        detail_title = tk.Label(
            right_frame,
            text="茶记详情",
            font=(theme['font_family'], 16, "bold"),
            bg='#F5F5DC',
            fg='#8B4513'
        )
        detail_title.pack(pady=10)
        
        # 详情显示区域容器
        detail_container = tk.Frame(right_frame, bg='#F5F5DC')
        detail_container.pack(pady=10, padx=10, fill='both', expand=True)
        
        # 图片显示区域
        self.image_display_frame = tk.Frame(detail_container, bg='#FFFAF0', relief='sunken', bd=2)
        self.image_display_frame.pack(fill='x', pady=(0, 10))
        
        # 文字详情显示区域
        self.detail_text = tk.Text(
            detail_container,
            height=10,
            width=40,
            font=(theme['font_family'], 11),
            bg='#FFFAF0',
            fg='#2F4F2F',
            relief='sunken',
            bd=2,
            wrap='word',
            state='disabled'
        )
        self.detail_text.pack(fill='both', expand=True)
        
        # 操作按钮框架
        button_frame = tk.Frame(right_frame, bg='#F5F5DC')
        button_frame.pack(pady=20)
        
        # 查看趋势按钮
        trend_btn = tk.Button(
            button_frame,
            text="📊 查看趋势",
            font=(theme['font_family'], 12, "bold"),
            bg='#4169E1',
            fg='white',
            activebackground='#6495ED',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=lambda: messagebox.showinfo("功能提示", "趋势分析功能正在开发中...")
        )
        trend_btn.pack(pady=5, fill='x')
        
        # 另存为按钮
        save_as_btn = tk.Button(
            button_frame,
            text="💾 另存为",
            font=(theme['font_family'], 12, "bold"),
            bg='#FF8C00',
            fg='white',
            activebackground='#FFA500',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=self.save_record_as
        )
        save_as_btn.pack(pady=5, fill='x')
        
        # 删除记录按钮
        delete_btn = tk.Button(
            button_frame,
            text="🗑️ 删除记录",
            font=(theme['font_family'], 12, "bold"),
            bg='#DC143C',
            fg='white',
            activebackground='#FF6347',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=self.delete_tea_record
        )
        delete_btn.pack(pady=5, fill='x')
        
        # 生成日报告按钮
        daily_report_btn = tk.Button(
            button_frame,
            text="📊 生成日报告",
            font=(theme['font_family'], 12, "bold"),
            bg='#9370DB',
            fg='white',
            activebackground='#BA55D3',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=self.generate_daily_report
        )
        daily_report_btn.pack(pady=5, fill='x')
        
        # 返回按钮
        back_btn = tk.Button(
            button_frame,
            text="🏠 返回首页",
            font=(theme['font_family'], 12, "bold"),
            bg='#228B22',
            fg='white',
            activebackground='#32CD32',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=self.create_main_interface
        )
        back_btn.pack(pady=5, fill='x')
        
        # 绑定列表选择事件
        self.records_listbox.bind('<<ListboxSelect>>', self.on_record_select)
        
        # 加载茶记录
        self.load_records_list()
    
    def load_records_list(self):
        """加载茶记录列表"""
        self.records_listbox.delete(0, tk.END)
        records = self.load_tea_records()
        
        # 按时间倒序排列
        records.sort(key=lambda x: x['brewing_time'], reverse=True)
        
        for record in records:
            # 格式化显示
            stars = "⭐" * record['rating']
            display_text = f"{record['brewing_time'][:10]} | {record['tea_name']} | {stars} ({record['rating']}/10)"
            self.records_listbox.insert(tk.END, display_text)
        
        # 存储记录数据供后续使用
        self.current_records = records
    
    def on_record_select(self, event):
        """处理记录选择事件"""
        selection = self.records_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index >= len(self.current_records):
            return
        
        record = self.current_records[index]
        self.selected_record = record  # 保存选中的记录
        
        # 清除之前的图片显示
        for widget in self.image_display_frame.winfo_children():
            widget.destroy()
        
        # 显示图片（如果有）
        if record.get('image_filename'):
            self.display_record_image(record['image_filename'])
        
        # 显示详情
        self.detail_text.config(state='normal')
        self.detail_text.delete('1.0', tk.END)
        
        detail_info = f"""茶种名称: {record['tea_name']}
冲泡时间: {record['brewing_time']}
美味评分: {"⭐" * record['rating']} ({record['rating']}/10)
冲泡次数: {record['pour_count']}次
是否加奶: {'是' if record['add_milk'] else '否'}

品茶笔记:
{record['notes']}

冲泡参数:
倒茶时间: {', '.join(map(str, record['brewing_params']['pour_times']))}秒
间隔时间: {', '.join(map(str, record['brewing_params']['intervals']))}秒
"""
        
        self.detail_text.insert('1.0', detail_info)
        self.detail_text.config(state='disabled')
    
    def display_record_image(self, image_filename):
        """显示茶记录中的图片"""
        try:
            image_path = os.path.join(self.record_path, 'images', image_filename)
            if not os.path.exists(image_path):
                return
            
            # 加载并调整图片大小
            image = Image.open(image_path)
            
            # 计算缩放比例，保持宽高比
            max_width, max_height = 250, 150
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 创建图片标签
            image_label = tk.Label(
                self.image_display_frame,
                image=photo,
                bg='#FFFAF0',
                cursor='hand2'
            )
            image_label.image = photo  # 保持引用
            image_label.pack(pady=10)
            
            # 绑定点击事件查看大图
            image_label.bind('<Button-1>', lambda e: self.show_full_image(image_path))
            
            # 添加提示文字
            tip_label = tk.Label(
                self.image_display_frame,
                text="点击图片查看大图",
                font=('Arial', 9),
                bg='#FFFAF0',
                fg='#666666'
            )
            tip_label.pack()
            
        except Exception as e:
            print(f"显示图片失败: {str(e)}")
    
    def show_full_image(self, image_path):
        """显示完整大小的图片"""
        try:
            # 创建新窗口
            image_window = tk.Toplevel(self.root)
            image_window.title("茶记图片")
            image_window.configure(bg='#F5F5DC')
            # 注册弹窗以支持 ESC 关闭（Toplevel window register）
            self.register_toplevel(image_window)
            
            # 加载原始图片
            image = Image.open(image_path)
            
            # 获取屏幕尺寸
            screen_width = image_window.winfo_screenwidth()
            screen_height = image_window.winfo_screenheight()
            
            # 设置图片查看窗口的最大尺寸（屏幕的80%）
            max_width = int(screen_width * 0.8)
            max_height = int(screen_height * 0.8)
            
            # 计算最佳显示尺寸
            display_width = min(image.width, max_width)
            display_height = min(image.height, max_height)
            
            # 如果图片太大，按比例缩放
            if image.width > max_width or image.height > max_height:
                # 计算缩放比例
                width_ratio = max_width / image.width
                height_ratio = max_height / image.height
                scale_ratio = min(width_ratio, height_ratio)
                
                # 计算新尺寸
                new_width = int(image.width * scale_ratio)
                new_height = int(image.height * scale_ratio)
                
                # 调整图片大小
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                display_width = new_width
                display_height = new_height
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 创建图片标签
            image_label = tk.Label(image_window, image=photo, bg='#F5F5DC')
            image_label.image = photo  # 保持引用
            image_label.pack(padx=20, pady=20)
            
            # 设置窗口大小和位置
            window_width = display_width + 40
            window_height = display_height + 40
            
            # 确保窗口不会超出屏幕
            window_width = min(window_width, screen_width - 100)
            window_height = min(window_height, screen_height - 100)
            
            # 计算居中位置
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # 设置窗口大小、位置和限制
            image_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            image_window.minsize(300, 200)  # 最小尺寸
            image_window.maxsize(screen_width - 50, screen_height - 50)  # 最大尺寸
            
        except Exception as e:
            messagebox.showerror("错误", f"无法显示图片: {str(e)}")
    
    def delete_tea_record(self):
        """删除茶记录"""
        selection = self.records_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的记录！")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除这条茶记录吗？\n删除后将无法恢复！"):
            index = selection[0]
            record_to_delete = self.current_records[index]
            
            # 删除关联的图片文件
            if record_to_delete.get('image_filename'):
                try:
                    image_path = os.path.join(self.record_path, 'images', record_to_delete['image_filename'])
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    print(f"删除图片文件失败: {str(e)}")
            
            # 从记录中删除
            records = self.load_tea_records()
            records = [r for r in records if r['id'] != record_to_delete['id']]
            
            # 保存更新后的记录
            try:
                with open(self.tea_records_path, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("成功", "记录删除成功！")
                self.load_records_list()  # 重新加载列表
                
                # 清空详情显示
                self.detail_text.config(state='normal')
                self.detail_text.delete('1.0', tk.END)
                self.detail_text.config(state='disabled')
                
                # 清空图片显示
                for widget in self.image_display_frame.winfo_children():
                    widget.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")
    
    def save_record_as(self):
        """另存为茶记录"""
        if not hasattr(self, 'selected_record') or not self.selected_record:
            messagebox.showwarning("提示", "请先选择要导出的记录！")
            return
        
        # 选择保存格式
        format_choice = messagebox.askyesnocancel(
            "选择格式",
            "选择导出格式：\n是 - 文本格式(.txt)\n否 - JSON格式(.json)\n取消 - 取消操作"
        )
        
        if format_choice is None:  # 用户取消
            return
        
        record = self.selected_record
        
        if format_choice:  # 文本格式
            file_types = [("文本文件", "*.txt"), ("所有文件", "*.*")]
            default_name = f"茶记_{record['tea_name']}_{record['brewing_time'][:10]}.txt"
        else:  # JSON格式
            file_types = [("JSON文件", "*.json"), ("所有文件", "*.*")]
            default_name = f"茶记_{record['tea_name']}_{record['brewing_time'][:10]}.json"
        
        file_path = filedialog.asksaveasfilename(
            title="保存茶记录",
            defaultextension=".txt" if format_choice else ".json",
            filetypes=file_types,
            initialname=default_name
        )
        
        if not file_path:
            return
        
        try:
            if format_choice:  # 文本格式
                content = f"""茶记录导出
================

茶种名称: {record['tea_name']}
冲泡时间: {record['brewing_time']}
美味评分: {"⭐" * record['rating']} ({record['rating']}/10)
冲泡次数: {record['pour_count']}次
是否加奶: {'是' if record['add_milk'] else '否'}

品茶笔记:
{record['notes']}

冲泡参数:
倒茶时间: {', '.join(map(str, record['brewing_params']['pour_times']))}秒
间隔时间: {', '.join(map(str, record['brewing_params']['intervals']))}秒

图片信息: {'有图片' if record.get('image_filename') else '无图片'}
"""
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:  # JSON格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", f"茶记录已保存到：\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def generate_daily_report(self):
        """生成日报告"""
        # 选择日期
        from tkinter import simpledialog
        
        date_str = simpledialog.askstring(
            "选择日期",
            "请输入要生成报告的日期 (格式: YYYY-MM-DD):",
            initialvalue=datetime.now().strftime("%Y-%m-%d")
        )
        
        if not date_str:
            return
        
        try:
            # 验证日期格式
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")
            return
        
        # 筛选指定日期的记录
        records = self.load_tea_records()
        daily_records = [r for r in records if r['brewing_time'].startswith(date_str)]
        
        if not daily_records:
            messagebox.showinfo("提示", f"没有找到 {date_str} 的茶记录")
            return
        
        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            title="保存日报告",
            defaultextension=".jpg",
            filetypes=[("JPEG图片", "*.jpg"), ("PNG图片", "*.png"), ("所有文件", "*.*")],
            initialname=f"茶记日报告_{date_str}.jpg"
        )
        
        if not file_path:
            return
        
        try:
            self.create_daily_report_image(daily_records, date_str, file_path)
            messagebox.showinfo("成功", f"日报告已生成：\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成报告失败：{str(e)}")
    
    def create_daily_report_image(self, records, date_str, output_path):
        """创建日报告图片"""
        from PIL import ImageDraw, ImageFont
        
        # 图片尺寸
        img_width = 800
        img_height = 600 + len(records) * 200  # 根据记录数量调整高度
        
        # 创建白色背景图片
        img = Image.new('RGB', (img_width, img_height), color='#F5F5DC')
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            title_font = ImageFont.truetype("arial.ttf", 32)
            header_font = ImageFont.truetype("arial.ttf", 20)
            text_font = ImageFont.truetype("arial.ttf", 16)
        except:
            # 如果无法加载字体，使用默认字体
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # 绘制标题
        title = f"茶记日报告 - {date_str}"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((img_width - title_width) // 2, 30), title, fill='#8B4513', font=title_font)
        
        # 绘制统计信息
        stats_y = 100
        total_records = len(records)
        avg_rating = sum(r['rating'] for r in records) / total_records if total_records > 0 else 0
        
        stats_text = f"总记录数: {total_records}    平均评分: {avg_rating:.1f}/10"
        draw.text((50, stats_y), stats_text, fill='#2F4F2F', font=header_font)
        
        # 绘制分隔线
        draw.line([(50, stats_y + 40), (img_width - 50, stats_y + 40)], fill='#DEB887', width=2)
        
        # 绘制每条记录
        y_offset = stats_y + 80
        
        for i, record in enumerate(records):
            # 记录背景
            record_bg_y1 = y_offset - 10
            record_bg_y2 = y_offset + 160
            draw.rectangle([(30, record_bg_y1), (img_width - 30, record_bg_y2)], 
                         fill='#FFFAF0', outline='#DEB887', width=2)
            
            # 茶名和时间
            tea_info = f"{record['tea_name']} - {record['brewing_time'][11:16]}"
            draw.text((50, y_offset), tea_info, fill='#8B4513', font=header_font)
            
            # 评分
            stars = "⭐" * record['rating']
            rating_text = f"评分: {stars} ({record['rating']}/10)"
            draw.text((50, y_offset + 30), rating_text, fill='#FF8C00', font=text_font)
            
            # 冲泡信息
            brew_info = f"冲泡次数: {record['pour_count']}次    加奶: {'是' if record['add_milk'] else '否'}"
            draw.text((50, y_offset + 55), brew_info, fill='#2F4F2F', font=text_font)
            
            # 笔记（截取前100个字符）
            notes = record['notes'][:100] + "..." if len(record['notes']) > 100 else record['notes']
            notes_lines = notes.split('\n')[:3]  # 最多显示3行
            
            for j, line in enumerate(notes_lines):
                draw.text((50, y_offset + 80 + j * 20), line, fill='#2F4F2F', font=text_font)
            
            # 如果有图片，显示标识
            if record.get('image_filename'):
                draw.text((img_width - 150, y_offset), "📷 有图片", fill='#4169E1', font=text_font)
            
            y_offset += 180
        
        # 绘制页脚
        footer_text = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=text_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        draw.text(((img_width - footer_width) // 2, img_height - 40), footer_text, fill='#666666', font=text_font)
        
        # 保存图片
        img.save(output_path, 'JPEG', quality=95)

    def delete_tea(self):
        """删除茶种"""
        selection = self.tea_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的茶种！")
            return
        
        try:
            filepath = self.tea_files[selection[0]]
            with open(filepath, 'r', encoding='utf-8') as f:
                tea_data = json.load(f)
            
            result = messagebox.askyesno(
                "确认删除",
                f"确定要删除茶种 '{tea_data['name']}' 吗？\n此操作不可恢复！"
            )
            
            if result:
                os.remove(filepath)
                messagebox.showinfo("删除成功", f"茶种 '{tea_data['name']}' 已删除！")
                self.load_tea_list()  # 重新加载列表
                
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{str(e)}")

    def skip_current_pour(self):
        """提前结束当前倒茶"""
        if not self.brewing_status['is_brewing']:
            return
        
        # 显示确认对话框
        result = messagebox.askyesno(
            "确认提前结束",
            "确定要提前结束本次倒茶吗？\n将立即进入下一次倒茶或结束冲泡。",
            icon='question'
        )
        
        if result:
            # 设置跳过标志
            self.brewing_status['skip_current'] = True
    
    def stop_all_timers(self):
        """停止所有活动的定时器"""
        self.active_timers.clear()
        # 重置冲泡状态
        self.brewing_status['is_brewing'] = False
        self.brewing_status['tea_data'] = None
        self.brewing_status['current_pour'] = 0
        self.brewing_status['next_pour_time'] = None
        self.brewing_status['skip_current'] = False
        # 更新边栏显示
        if hasattr(self, 'sidebar'):
            self.update_sidebar_display()

    def show_settings_page(self):
        """显示设置页面"""
        # 停止所有定时器并清理状态
        self.stop_all_timers()
        
        # 清空窗口
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
        except tk.TclError:
            pass
        
        # 获取当前主题配置
        theme = self.get_theme_config()
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="⚙️ 程序设置",
            font=(theme['title_font'], 20, "bold"),
            bg=theme['bg_color'],
            fg=theme['text_color']
        )
        title_label.pack(pady=30)
        
        # 设置框架
        settings_frame = tk.Frame(self.root, bg=theme['bg_color'])
        settings_frame.pack(padx=50, pady=30, fill='both', expand=True)
        
        # 主题设置标题
        theme_title = tk.Label(
            settings_frame,
            text="🎨 UI主题风格",
            font=(theme['font_family'], 16, "bold"),
            bg=theme['bg_color'],
            fg=theme['text_color']
        )
        theme_title.pack(pady=(0, 20))
        
        # 主题选择框架
        theme_frame = tk.Frame(settings_frame, bg=theme['bg_color'])
        theme_frame.pack(pady=20)
        
        # 主题选择变量
        self.theme_var = tk.StringVar(value=self.current_theme)
        
        # 创建主题选择按钮
        for theme_key, theme_info in self.themes.items():
            theme_button = tk.Radiobutton(
                theme_frame,
                text=f"{theme_info['name']} - {theme_key}",
                variable=self.theme_var,
                value=theme_key,
                font=(theme['font_family'], 14),
                bg=theme['bg_color'],
                fg=theme['text_color_2'],
                selectcolor=theme['button_color'],
                activebackground=theme['bg_color'],
                activeforeground=theme['text_color'],
                command=self.preview_theme
            )
            theme_button.pack(anchor='w', pady=5)
        
        # 主题预览说明
        preview_label = tk.Label(
            settings_frame,
            text="💡 选择主题后会立即预览效果",
            font=(theme['font_family'], 12),
            bg=theme['bg_color'],
            fg=theme['text_color_2']
        )
        preview_label.pack(pady=10)
        
        # 分隔线
        separator1 = tk.Frame(settings_frame, height=2, bg=theme['text_color_2'])
        separator1.pack(fill='x', pady=20)
        
        # 自定义背景设置标题
        custom_bg_title = tk.Label(
            settings_frame,
            text="🖼️ 自定义背景图片",
            font=(theme['font_family'], 16, "bold"),
            bg=theme['bg_color'],
            fg=theme['text_color']
        )
        custom_bg_title.pack(pady=(0, 20))
        
        # 自定义背景框架
        custom_bg_frame = tk.Frame(settings_frame, bg=theme['bg_color'])
        custom_bg_frame.pack(pady=10, fill='x')
        
        # 当前背景显示
        current_bg_label = tk.Label(
            custom_bg_frame,
            text=f"当前背景: {'自定义图片' if self.custom_background_path else '默认背景'}",
            font=(theme['font_family'], 12),
            bg=theme['bg_color'],
            fg=theme['text_color_2']
        )
        current_bg_label.pack(pady=5)
        
        # 背景选择按钮框架
        bg_button_frame = tk.Frame(custom_bg_frame, bg=theme['bg_color'])
        bg_button_frame.pack(pady=10)
        
        # 选择背景图片按钮
        select_bg_button = tk.Button(
            bg_button_frame,
            text="📁 选择背景图片",
            font=(theme['font_family'], 12, "bold"),
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=self.select_custom_background
        )
        select_bg_button.pack(side='left', padx=5)
        
        # 重置背景按钮
        reset_bg_button = tk.Button(
            bg_button_frame,
            text="🔄 重置为默认",
            font=(theme['font_family'], 12, "bold"),
            bg='#FF9800',
            fg='white',
            activebackground='#e68900',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=self.reset_custom_background
        )
        reset_bg_button.pack(side='left', padx=5)
        
        # 预览背景按钮
        preview_bg_button = tk.Button(
            bg_button_frame,
            text="👁️ 预览效果",
            font=(theme['font_family'], 12, "bold"),
            bg='#2196F3',
            fg='white',
            activebackground='#1976D2',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=self.preview_custom_background
        )
        preview_bg_button.pack(side='left', padx=5)
        
        # 分隔线2
        separator2 = tk.Frame(settings_frame, height=2, bg=theme['text_color_2'])
        separator2.pack(fill='x', pady=20)
        
        # 自定义按钮背景设置标题
        custom_btn_title = tk.Label(
            settings_frame,
            text="🎨 自定义按钮样式",
            font=(theme['font_family'], 16, "bold"),
            bg=theme['bg_color'],
            fg=theme['text_color']
        )
        custom_btn_title.pack(pady=(0, 20))
        
        # 自定义按钮框架
        custom_btn_frame = tk.Frame(settings_frame, bg=theme['bg_color'])
        custom_btn_frame.pack(pady=10, fill='x')
        
        # 当前按钮样式显示
        current_btn_label = tk.Label(
            custom_btn_frame,
            text=f"当前按钮样式: {'自定义样式' if self.custom_button_background_path else '默认样式'}",
            font=(theme['font_family'], 12),
            bg=theme['bg_color'],
            fg=theme['text_color_2']
        )
        current_btn_label.pack(pady=5)
        
        # 按钮样式选择按钮框架
        btn_button_frame = tk.Frame(custom_btn_frame, bg=theme['bg_color'])
        btn_button_frame.pack(pady=10)
        
        # 选择按钮背景图片按钮
        select_btn_bg_button = tk.Button(
            btn_button_frame,
            text="🎨 选择按钮背景",
            font=(theme['font_family'], 12, "bold"),
            bg='#9C27B0',
            fg='white',
            activebackground='#7B1FA2',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=self.select_custom_button_background
        )
        select_btn_bg_button.pack(side='left', padx=5)
        
        # 重置按钮样式按钮
        reset_btn_bg_button = tk.Button(
            btn_button_frame,
            text="🔄 重置按钮样式",
            font=(theme['font_family'], 12, "bold"),
            bg='#FF5722',
            fg='white',
            activebackground='#D84315',
            relief='raised',
            bd=3,
            padx=15,
            pady=8,
            command=self.reset_custom_button_background
        )
        reset_btn_bg_button.pack(side='left', padx=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.root, bg=theme['bg_color'])
        button_frame.pack(pady=30)
        
        # 保存设置按钮
        save_button = tk.Button(
            button_frame,
            text="💾 保存设置",
            font=(theme['font_family'], 14, "bold"),
            bg=theme['button_color_3'],
            fg='white',
            width=12,
            height=2,
            command=self.save_theme_settings
        )
        save_button.pack(side='left', padx=10)
        
        # 返回按钮
        back_button = tk.Button(
            button_frame,
            text="🔙 返回主页",
            font=(theme['font_family'], 14, "bold"),
            bg=theme['button_color_4'],
            fg='white',
            width=12,
            height=2,
            command=self.create_main_interface
        )
        back_button.pack(side='left', padx=10)

    def preview_theme(self):
        """预览主题效果"""
        selected_theme = self.theme_var.get()
        if selected_theme != self.current_theme:
            # 临时切换主题进行预览
            old_theme = self.current_theme
            self.current_theme = selected_theme
            self.apply_theme()
            self.show_settings_page()  # 重新显示设置页面以应用新主题

    def save_theme_settings(self):
        """保存主题设置"""
        selected_theme = self.theme_var.get()
        self.current_theme = selected_theme
        self.save_settings()
        self.apply_theme()
        messagebox.showinfo("设置保存", f"主题已切换为：{self.themes[selected_theme]['name']}")
        self.create_main_interface()
    
    def select_custom_background(self):
        """选择自定义背景图片"""
        try:
            # 支持的图片格式
            filetypes = [
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("GIF文件", "*.gif"),
                ("BMP文件", "*.bmp"),
                ("所有文件", "*.*")
            ]
            
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择背景图片",
                filetypes=filetypes,
                initialdir=os.path.expanduser("~")  # 从用户主目录开始
            )
            
            if file_path:
                # 验证图片文件
                try:
                    # 尝试打开图片以验证格式
                    test_image = Image.open(file_path)
                    test_image.close()
                    
                    # 保存自定义背景路径
                    self.custom_background_path = os.path.abspath(file_path)
                    
                    # 立即预览效果
                    self.preview_custom_background()
                    
                    messagebox.showinfo("成功", f"背景图片已选择：\n{os.path.basename(file_path)}")
                    
                except Exception as e:
                    messagebox.showerror("错误", f"无效的图片文件：\n{str(e)}")
                    
        except Exception as e:
            messagebox.showerror("错误", f"选择图片失败：\n{str(e)}")
    
    def reset_custom_background(self):
        """重置为默认背景"""
        try:
            self.custom_background_path = None
            self.load_background_image()
            self.show_settings_page()  # 刷新设置页面
            messagebox.showinfo("成功", "已重置为默认背景")
        except Exception as e:
            messagebox.showerror("错误", f"重置背景失败：\n{str(e)}")
    
    def preview_custom_background(self):
        """预览自定义背景效果"""
        try:
            # 重新加载背景图片
            self.load_background_image()
            # 刷新设置页面以显示新背景
            self.show_settings_page()
        except Exception as e:
            messagebox.showerror("错误", f"预览背景失败：\n{str(e)}")
    
    def select_custom_button_background(self):
        """选择自定义按钮背景图片"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="选择按钮背景图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("GIF文件", "*.gif"),
                ("BMP文件", "*.bmp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 验证图片文件
                from PIL import Image
                with Image.open(file_path) as img:
                    # 检查图片尺寸
                    width, height = img.size
                    if width < 50 or height < 50:
                        messagebox.showwarning("警告", "图片尺寸太小，建议选择至少50x50像素的图片！")
                        return
                    
                    # 保存路径
                    self.custom_button_background_path = file_path
                    messagebox.showinfo("成功", f"按钮背景图片已选择：\n{file_path}")
                    
                    # 立即应用效果
                    self.apply_custom_button_styles()
                    
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片文件：\n{str(e)}")
    
    def reset_custom_button_background(self):
        """重置按钮背景为默认样式"""
        self.custom_button_background_path = None
        messagebox.showinfo("重置", "按钮样式已重置为默认！")
        
        # 重新应用主题样式
        self.apply_theme()
    
    def apply_custom_button_styles(self):
        """应用自定义按钮样式"""
        if not self.custom_button_background_path:
            return
            
        try:
            from PIL import Image, ImageTk
            
            # 加载并处理按钮背景图片
            with Image.open(self.custom_button_background_path) as img:
                # 创建不同尺寸的按钮背景
                button_sizes = [
                    (200, 50),   # 主按钮
                    (150, 40),   # 中等按钮
                    (120, 35),   # 小按钮
                ]
                
                self.custom_button_images = {}
                
                for size_name, (width, height) in zip(['large', 'medium', 'small'], button_sizes):
                    # 调整图片大小
                    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                    
                    # 添加半透明覆盖层以确保文字可读性
                    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
                    resized_img = resized_img.convert('RGBA')
                    combined = Image.alpha_composite(resized_img, overlay)
                    
                    # 转换为PhotoImage
                    self.custom_button_images[size_name] = ImageTk.PhotoImage(combined)
                    
            messagebox.showinfo("成功", "自定义按钮样式已应用！")
            
        except Exception as e:
            messagebox.showerror("错误", f"应用按钮样式时出错：\n{str(e)}")
            self.custom_button_background_path = None

def main():
    """主函数"""
    root = tk.Tk()
    app = TeaBrewingApp(root)
    root.mainloop()

    def show_trend_analysis(self):
        """显示趋势分析"""
        records = self.load_tea_records()
        if not records:
            messagebox.showinfo("提示", "暂无茶记录数据！")
            return
        
        # 创建趋势分析窗口
        trend_window = tk.Toplevel(self.root)
        trend_window.title("美味值趋势分析")
        trend_window.geometry("900x700")
        trend_window.configure(bg='#F5F5DC')
        # 注册弹窗以支持 ESC 关闭（Toplevel window register）
        self.register_toplevel(trend_window)
        
        # 设置背景
        self.setup_background(trend_window)
        
        # 主框架
        main_frame = tk.Frame(trend_window, bg='#F5F5DC', relief='raised', bd=3)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text="📊 美味值趋势分析",
            font=("Arial", 18, "bold"),
            bg='#F5F5DC',
            fg='#8B4513'
        )
        title_label.pack(pady=10)
        
        # 创建图表
        self.create_trend_charts(main_frame, records)
        
        # 关闭按钮
        close_btn = tk.Button(
            main_frame,
            text="关闭",
            font=("Arial", 12, "bold"),
            bg='#DC143C',
            fg='white',
            command=trend_window.destroy
        )
        close_btn.pack(pady=10)

    def create_trend_charts(self, parent, records):
        """创建趋势图表"""
        # 准备数据
        dates = []
        ratings = []
        tea_names = []
        
        for record in records:
            try:
                date = datetime.strptime(record['brewing_time'], "%Y-%m-%d %H:%M:%S")
                dates.append(date)
                ratings.append(record['rating'])
                tea_names.append(record['tea_name'])
            except:
                continue
        
        if not dates:
            tk.Label(parent, text="暂无有效数据", font=("Arial", 14), bg='#F5F5DC').pack(pady=20)
            return
        
        # 创建matplotlib图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.patch.set_facecolor('#F5F5DC')
        
        # 时间趋势图
        ax1.plot(dates, ratings, marker='o', linewidth=2, markersize=6, color='#8B4513')
        ax1.set_title('美味值时间趋势', fontsize=14, fontweight='bold', color='#8B4513')
        ax1.set_ylabel('美味值', fontsize=12, color='#8B4513')
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#FFFAF0')
        
        # 格式化日期显示
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 按茶种统计
        tea_stats = {}
        for tea_name, rating in zip(tea_names, ratings):
            if tea_name not in tea_stats:
                tea_stats[tea_name] = []
            tea_stats[tea_name].append(rating)
        
        # 计算平均值
        tea_avg = {name: np.mean(ratings) for name, ratings in tea_stats.items()}
        
        # 茶种平均美味值柱状图
        names = list(tea_avg.keys())
        avg_ratings = list(tea_avg.values())
        
        bars = ax2.bar(names, avg_ratings, color=['#8B4513', '#2F4F2F', '#B8860B', '#8B008B'][:len(names)])
        ax2.set_title('各茶种平均美味值', fontsize=14, fontweight='bold', color='#8B4513')
        ax2.set_ylabel('平均美味值', fontsize=12, color='#8B4513')
        ax2.set_ylim(0, 10)
        ax2.set_facecolor('#FFFAF0')
        
        # 在柱状图上显示数值
        for bar, avg in zip(bars, avg_ratings):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{avg:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        plt.tight_layout()
        
        # 将图表嵌入到tkinter窗口
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)


def main():
    root = tk.Tk()
    app = TeaBrewingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()