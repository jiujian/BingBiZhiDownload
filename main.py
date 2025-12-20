#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
必应每日壁纸下载器 - GUI版本
支持下载指定日期范围、不同分辨率、多线程下载等功能
"""

import os
import json
import re
import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from pathlib import Path


class BingWallpaperDownloader:
    """必应壁纸下载器主类"""
    
    # 必应API基础URL
    API_BASE_URL = "https://www.bing.com/HPImageArchive.aspx"
    
    # 支持的分辨率选项
    RESOLUTION_OPTIONS = {
        "1920x1080": "_1920x1080",
        "UHD (4K)": "_UHD",
        "1366x768": "_1366x768",
        "1024x768": "_1024x768",
        "800x600": "_800x600",
        "原始尺寸": ""
    }
    
    # 支持的区域市场
    MARKET_OPTIONS = {
        "中国 (zh-CN)": "zh-CN",
        "美国 (en-US)": "en-US",
        "日本 (ja-JP)": "ja-JP",
        "英国 (en-GB)": "en-GB",
        "德国 (de-DE)": "de-DE",
        "法国 (fr-FR)": "fr-FR"
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("必应每日壁纸下载器")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 下载状态
        self.downloading = False
        self.log_lock = Lock()
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # 日期选择区
        date_frame = ttk.LabelFrame(main_frame, text="日期选择", padding="10")
        date_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        date_frame.columnconfigure(1, weight=1)
        row += 1
        
        self.date_mode = tk.StringVar(value="recent")
        
        ttk.Radiobutton(date_frame, text="下载最近", variable=self.date_mode, 
                       value="recent", command=self.on_date_mode_change).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.recent_days = tk.StringVar(value="7")
        ttk.Entry(date_frame, textvariable=self.recent_days, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Label(date_frame, text="天的壁纸").grid(row=0, column=2, sticky=tk.W)
        
        ttk.Radiobutton(date_frame, text="指定单日", variable=self.date_mode, 
                       value="single", command=self.on_date_mode_change).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.single_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.single_date, width=15).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(date_frame, text="格式: YYYY-MM-DD").grid(row=1, column=2, sticky=tk.W)
        
        ttk.Radiobutton(date_frame, text="日期范围", variable=self.date_mode, 
                       value="range", command=self.on_date_mode_change).grid(row=2, column=0, sticky=tk.W, padx=5)
        self.date_start = tk.StringVar(value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        self.date_end = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.date_start, width=15).grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Label(date_frame, text="至").grid(row=2, column=2, sticky=tk.W, padx=5)
        ttk.Entry(date_frame, textvariable=self.date_end, width=15).grid(row=2, column=3, sticky=tk.W, padx=5)
        
        # 高级选项区
        options_frame = ttk.LabelFrame(main_frame, text="高级选项", padding="10")
        options_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        options_frame.columnconfigure(1, weight=1)
        row += 1
        
        # 输出目录
        ttk.Label(options_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        ttk.Entry(options_frame, textvariable=self.output_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(options_frame, text="浏览", command=self.browse_output_path).grid(row=0, column=2, padx=5)
        
        # 线程数
        ttk.Label(options_frame, text="线程数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.thread_count = tk.StringVar(value="5")
        thread_frame = ttk.Frame(options_frame)
        thread_frame.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Spinbox(thread_frame, from_=1, to=20, textvariable=self.thread_count, width=10).grid(row=0, column=0)
        ttk.Label(thread_frame, text="(1-20)").grid(row=0, column=1, padx=5)
        
        # 分辨率
        ttk.Label(options_frame, text="分辨率:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.resolution = tk.StringVar(value="1920x1080")
        resolution_combo = ttk.Combobox(options_frame, textvariable=self.resolution, 
                                       values=list(self.RESOLUTION_OPTIONS.keys()), 
                                       state="readonly", width=20)
        resolution_combo.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # 区域市场
        ttk.Label(options_frame, text="区域市场:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.market = tk.StringVar(value="中国 (zh-CN)")
        market_combo = ttk.Combobox(options_frame, textvariable=self.market, 
                                   values=list(self.MARKET_OPTIONS.keys()), 
                                   state="readonly", width=20)
        market_combo.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # 归档选项
        self.archive_by_date = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="按年月归档 (创建 年份/月份 子目录)", 
                       variable=self.archive_by_date).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 操作区
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        self.download_button = ttk.Button(button_frame, text="开始下载", command=self.start_download, width=15)
        self.download_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出程序", command=self.root.quit, width=15).pack(side=tk.LEFT, padx=5)
        
        # 日志显示区
        log_frame = ttk.LabelFrame(main_frame, text="下载日志", padding="10")
        log_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始化日志
        self.log("欢迎使用必应每日壁纸下载器！")
        self.log(f"当前输出目录: {self.output_path.get()}")
        
    def on_date_mode_change(self):
        """日期模式改变时的处理"""
        pass
        
    def browse_output_path(self):
        """浏览输出路径"""
        path = filedialog.askdirectory(initialdir=self.output_path.get(), title="选择输出目录")
        if path:
            self.output_path.set(path)
            self.log(f"输出目录已更改为: {path}")
    
    def log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        with self.log_lock:
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            self.root.update_idletasks()
    
    def get_bing_wallpaper_info(self, date, market):
        """获取指定日期的必应壁纸信息"""
        try:
            params = {
                "format": "js",
                "idx": "0",
                "n": "1",
                "mkt": market
            }
            
            # 计算日期差（idx表示从今天往前推的天数）
            # idx=0 表示今天，idx=1 表示昨天，以此类推
            today = datetime.now().date()
            target_date = date.date()
            
            # 如果目标日期是未来，使用今天
            if target_date > today:
                target_date = today
            
            # 计算天数差
            days_diff = (today - target_date).days
            params["idx"] = str(days_diff)
            
            # 必应API最多只能获取最近约15-20天的壁纸
            if days_diff > 15:
                self.log(f"警告: {date.strftime('%Y-%m-%d')} 的壁纸可能无法获取（超过15天）")
            
            response = requests.get(self.API_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("images") and len(data["images"]) > 0:
                image_info = data["images"][0]
                
                # 验证返回的日期是否匹配（可选，API返回的日期格式可能不同）
                # 这里我们使用用户请求的日期，因为API可能返回不同的日期格式
                
                return {
                    "url": image_info.get("url", ""),
                    "title": image_info.get("title", ""),
                    "copyright": image_info.get("copyright", ""),
                    "date": datetime.combine(target_date, datetime.min.time())  # 使用计算后的日期
                }
            return None
            
        except Exception as e:
            self.log(f"获取 {date.strftime('%Y-%m-%d')} 壁纸信息失败: {str(e)}")
            return None
    
    def get_image_url(self, url_base, resolution):
        """构建完整的图片URL"""
        if not url_base:
            return None
        
        # 获取分辨率后缀
        resolution_suffix = self.RESOLUTION_OPTIONS.get(resolution, "")
        
        # 如果选择原始尺寸，直接使用原始URL
        if not resolution_suffix:
            if url_base.startswith("http"):
                return url_base
            elif url_base.startswith("/"):
                return f"https://www.bing.com{url_base}"
            else:
                return f"https://www.bing.com/{url_base}"
        
        # 处理分辨率替换
        # 必应URL格式通常为: /th?id=OHR.xxx_1920x1080.jpg&rf=... 或 /th?id=OHR.xxx.jpg&rf=...
        
        # 移除开头的斜杠以便处理
        url_work = url_base.lstrip("/")
        
        # 尝试匹配并替换现有分辨率标识（格式: _1920x1080 或 _UHD 等）
        # 匹配模式: _数字x数字 或 _UHD 等
        pattern = r'_(\d+x\d+|UHD|HD|SD)'
        
        if re.search(pattern, url_work):
            # 替换现有分辨率
            url_work = re.sub(pattern, resolution_suffix, url_work, count=1)
        else:
            # 在文件扩展名之前添加分辨率后缀
            # 查找 ?id= 参数后的文件名
            if '?' in url_work:
                parts = url_work.split('?', 1)
                query_part = parts[1]
                path_part = parts[0]
                
                # 在文件名和扩展名之间插入分辨率
                if '.' in path_part:
                    name, ext = path_part.rsplit('.', 1)
                    path_part = f"{name}{resolution_suffix}.{ext}"
                    url_work = f"{path_part}?{query_part}"
            else:
                # 简单情况，直接在扩展名前添加分辨率
                if '.' in url_work:
                    name, ext = url_work.rsplit('.', 1)
                    url_work = f"{name}{resolution_suffix}.{ext}"
        
        # 构建完整URL
        if url_work.startswith("http"):
            return url_work
        else:
            return f"https://www.bing.com/{url_work}"
    
    def download_image(self, image_info, output_dir, resolution, archive_by_date):
        """下载单张图片"""
        try:
            date = image_info["date"]
            title = image_info["title"]
            
            # 构建保存路径
            if archive_by_date:
                year_month_dir = os.path.join(output_dir, date.strftime("%Y"), date.strftime("%m"))
                os.makedirs(year_month_dir, exist_ok=True)
                save_dir = year_month_dir
            else:
                save_dir = output_dir
            
            # 构建文件名（清理标题中的非法字符）
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.')).strip()
            safe_title = safe_title.replace(' ', '_')[:50]  # 限制长度
            filename = f"{date.strftime('%Y-%m-%d')}_{safe_title}.jpg"
            filepath = os.path.join(save_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(filepath):
                self.log(f"跳过: {filename} (文件已存在)")
                return {"success": True, "skipped": True, "filename": filename}
            
            # 获取图片URL
            image_url = self.get_image_url(image_info["url"], resolution)
            if not image_url:
                raise Exception("无法构建图片URL")
            
            # 下载图片
            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # 保存文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(filepath)
            self.log(f"✓ 下载成功: {filename} ({file_size / 1024:.1f} KB)")
            return {"success": True, "skipped": False, "filename": filename}
            
        except Exception as e:
            self.log(f"✗ 下载失败: {image_info.get('title', '未知')} - {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_date_list(self):
        """根据选择的日期模式获取日期列表"""
        date_list = []
        
        mode = self.date_mode.get()
        
        if mode == "recent":
            try:
                days = int(self.recent_days.get())
                if days <= 0:
                    raise ValueError("天数必须大于0")
                for i in range(days):
                    date = datetime.now() - timedelta(days=i)
                    date_list.append(date)
            except ValueError as e:
                messagebox.showerror("错误", f"最近天数输入错误: {str(e)}")
                return []
                
        elif mode == "single":
            try:
                date = datetime.strptime(self.single_date.get(), "%Y-%m-%d")
                date_list.append(date)
            except ValueError:
                messagebox.showerror("错误", "日期格式错误，请使用 YYYY-MM-DD 格式")
                return []
                
        elif mode == "range":
            try:
                start_date = datetime.strptime(self.date_start.get(), "%Y-%m-%d")
                end_date = datetime.strptime(self.date_end.get(), "%Y-%m-%d")
                
                if start_date > end_date:
                    messagebox.showerror("错误", "开始日期不能晚于结束日期")
                    return []
                
                current = start_date
                while current <= end_date:
                    date_list.append(current)
                    current += timedelta(days=1)
            except ValueError:
                messagebox.showerror("错误", "日期格式错误，请使用 YYYY-MM-DD 格式")
                return []
        
        return date_list
    
    def start_download(self):
        """开始下载"""
        if self.downloading:
            messagebox.showwarning("警告", "下载正在进行中，请等待完成")
            return
        
        # 验证输出目录
        output_dir = self.output_path.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建输出目录: {str(e)}")
            return
        
        # 获取日期列表
        date_list = self.get_date_list()
        if not date_list:
            return
        
        # 验证线程数
        try:
            thread_count = int(self.thread_count.get())
            if thread_count < 1 or thread_count > 20:
                raise ValueError("线程数必须在1-20之间")
        except ValueError as e:
            messagebox.showerror("错误", f"线程数设置错误: {str(e)}")
            return
        
        # 获取其他参数
        resolution = self.resolution.get()
        market_code = self.MARKET_OPTIONS.get(self.market.get(), "zh-CN")
        archive_by_date = self.archive_by_date.get()
        
        # 开始下载
        self.downloading = True
        self.download_button.config(state="disabled", text="下载中...")
        self.log("=" * 60)
        self.log(f"开始下载任务: 共 {len(date_list)} 天的壁纸")
        self.log(f"分辨率: {resolution}, 区域市场: {self.market.get()}, 线程数: {thread_count}")
        self.log("=" * 60)
        
        # 在新线程中执行下载，避免阻塞GUI
        import threading
        download_thread = threading.Thread(
            target=self.download_worker,
            args=(date_list, output_dir, resolution, market_code, archive_by_date, thread_count),
            daemon=True
        )
        download_thread.start()
    
    def download_worker(self, date_list, output_dir, resolution, market_code, archive_by_date, thread_count):
        """下载工作线程"""
        try:
            # 第一步：获取所有壁纸信息
            self.log("正在获取壁纸信息...")
            image_info_list = []
            
            for date in date_list:
                info = self.get_bing_wallpaper_info(date, market_code)
                if info:
                    image_info_list.append(info)
                else:
                    self.log(f"跳过 {date.strftime('%Y-%m-%d')} (无法获取壁纸信息)")
            
            if not image_info_list:
                self.log("没有可下载的壁纸")
                self.root.after(0, self.download_complete)
                return
            
            self.log(f"共找到 {len(image_info_list)} 张壁纸，开始下载...")
            
            # 第二步：使用线程池下载
            success_count = 0
            skip_count = 0
            fail_count = 0
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                future_to_info = {
                    executor.submit(self.download_image, info, output_dir, resolution, archive_by_date): info
                    for info in image_info_list
                }
                
                for future in as_completed(future_to_info):
                    result = future.result()
                    if result.get("success"):
                        if result.get("skipped"):
                            skip_count += 1
                        else:
                            success_count += 1
                    else:
                        fail_count += 1
            
            # 下载完成
            self.log("=" * 60)
            self.log(f"下载完成！成功: {success_count}, 跳过: {skip_count}, 失败: {fail_count}")
            self.log("=" * 60)
            
        except Exception as e:
            self.log(f"下载过程中发生错误: {str(e)}")
            messagebox.showerror("错误", f"下载失败: {str(e)}")
        finally:
            self.root.after(0, self.download_complete)
    
    def download_complete(self):
        """下载完成后的回调"""
        self.downloading = False
        self.download_button.config(state="normal", text="开始下载")
        # messagebox.showinfo("完成", "下载任务已完成！")


def main():
    """主函数"""
    root = tk.Tk()
    app = BingWallpaperDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()

