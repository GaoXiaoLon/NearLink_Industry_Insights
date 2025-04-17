import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import logging
import sys
import os
import queue
import time
import threading
from datetime import datetime, timedelta
from PIL import Image, ImageTk

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager
from core.monitor import Monitor
from utils.scheduler import Scheduler
from utils.logger import Logger
from gui.components.config_panel import ConfigPanel
from gui.components.log_panel import LogPanel
from gui.components.widgets import StatusBar, ToolTip, TimePicker

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # 初始化配置
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self.monitor = Monitor(self.config_manager)
        self.scheduler = Scheduler()
        
        # 设置窗口
        self.title("星闪行业洞察")
        self.geometry("800x600")
        
        # 加载logo
        self._load_logo()
        
        # 创建任务队列
        self.task_queue = queue.Queue()
        self.is_processing = False
        
        # 创建界面
        self._create_widgets()
        
        # 启动定时任务
        self._start_scheduler()
        
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 启动任务处理循环
        self._process_tasks()

    def _load_logo(self):
        """加载logo"""
        try:
            # 获取logo文件路径
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'resources', 'logo', 'logo.png')
            
            # 检查文件是否存在
            if not os.path.exists(logo_path):
                self.logger.warning(f"Logo文件不存在: {logo_path}")
                return
                
            # 使用PIL加载图片
            image = Image.open(logo_path)
            
            # 调整大小
            image = image.resize((24, 24), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            self.logo_image = ImageTk.PhotoImage(image)
            
            # 设置窗口图标
            self.iconphoto(True, self.logo_image)
            
        except Exception as e:
            self.logger.error(f"加载logo失败: {str(e)}")

    def _process_tasks(self):
        """处理任务队列中的任务"""
        try:
            if not self.is_processing:
                self.is_processing = True
                while True:
                    try:
                        task = self.task_queue.get_nowait()
                        task()
                    except queue.Empty:
                        break
        finally:
            self.is_processing = False
            # 继续检查任务队列
            self.after(100, self._process_tasks)

    def _add_task(self, task_func: Callable):
        """添加任务到队列"""
        self.task_queue.put(task_func)

    def _create_widgets(self):
        """创建界面组件"""
        # 创建菜单栏
        self._create_menu()
        
        # 创建主面板
        main_panel = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_panel.pack(fill="both", expand=True)
        
        # 创建标题栏
        title_frame = ttk.Frame(main_panel)
        title_frame.pack(fill="x", padx=5, pady=5)
        
        # 创建logo标签
        if hasattr(self, 'logo_image'):
            logo_label = ttk.Label(title_frame, image=self.logo_image)
            logo_label.pack(side="left", padx=5)
        
        # 创建标题标签
        title_label = ttk.Label(
            title_frame,
            text="星闪行业洞察",
            font=("微软雅黑", 12, "bold")
        )
        title_label.pack(side="left", padx=5)
        
        # 创建内容面板
        content_panel = ttk.Frame(main_panel)
        content_panel.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建配置面板
        self.config_panel = ConfigPanel(content_panel, self.config_manager)
        self.config_panel.pack(fill="both", expand=True)
        
        # 创建按钮面板
        button_panel = ttk.Frame(content_panel)
        button_panel.pack(fill="x", pady=5)
        
        # 创建左侧按钮组
        left_button_panel = ttk.Frame(button_panel)
        left_button_panel.pack(side="left", fill="x", expand=True)
        
        # 创建保存配置按钮
        save_button = ttk.Button(
            left_button_panel,
            text="保存配置",
            command=self._on_config_save
        )
        save_button.pack(side="left", padx=5)
        
        # 创建立即执行按钮
        run_button = ttk.Button(
            left_button_panel,
            text="立即执行",
            command=self._run_scheduled_monitor
        )
        run_button.pack(side="left", padx=5)
        
        # 创建测试按钮
        test_button = ttk.Button(
            left_button_panel,
            text="测试采集",
            command=self._run_test_monitor
        )
        test_button.pack(side="left", padx=5)
        
        # 创建日志面板
        self.log_panel = LogPanel(content_panel)
        self.log_panel.pack(fill="both", expand=True)
        
        # 创建状态栏
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x", side="bottom")
        
        # 设置日志处理器
        self._setup_log_handler()

    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="清理旧数据", command=self._cleanup_data)
        tools_menu.add_command(label="测试邮件发送", command=self._test_email)
        menubar.add_cascade(label="工具", menu=tools_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.config(menu=menubar)

    def _setup_log_handler(self):
        """设置日志处理器"""
        class LogHandler(logging.Handler):
            def __init__(self, log_panel):
                super().__init__()
                self.log_panel = log_panel
            
            def emit(self, record):
                self.log_panel.add_log(record.levelname, self.format(record))
        
        handler = LogHandler(self.log_panel)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.logger.addHandler(handler)

    def _start_scheduler(self):
        """启动定时任务"""
        monitor_config = self.config_manager.get('monitor', {})
        schedule = monitor_config.get('schedule', {})
        
        self.scheduler.add_job(
            'monitor',
            self._run_scheduled_monitor,
            schedule.get('hour', 8),
            schedule.get('minute', 0)
        )
        self.scheduler.start()

    def _on_config_save(self):
        """配置保存事件"""
        def save_config():
            try:
                # 保存配置面板中的配置
                self.config_panel._save_config()
                
                # 重新启动定时任务
                self.scheduler.stop()
                self._start_scheduler()
                
                self.logger.info("配置已保存")
                self.status_bar.set_status("配置已保存")
            except Exception as e:
                self.logger.error(f"配置保存失败: {str(e)}")
                self.status_bar.set_status(f"配置保存失败: {str(e)}")
                messagebox.showerror("错误", f"配置保存失败: {str(e)}")
        
        self._add_task(save_config)

    def _run_scheduled_monitor(self):
        """执行定时监控任务"""
        def monitor_task():
            try:
                self.status_bar.set_status("正在执行定时监控任务...")
                self.status_bar.set_progress(0)
                self.logger.info("开始执行定时监控任务")
                
                # 使用线程执行监控任务
                def run_monitor_thread():
                    try:
                        # 获取邮件配置
                        email_config = self.config_manager.get('email', {})
                        receivers = email_config.get('receivers', [])
                        
                        if not receivers:
                            self.status_bar.set_status("未设置收件人邮箱")
                            self.logger.error("未设置收件人邮箱")
                            messagebox.showerror("错误", "未设置收件人邮箱")
                            return
                        
                        self.logger.info("开始监控数据源...")
                        self.status_bar.set_status("正在监控数据源...")
                        self.status_bar.set_progress(30)
                        
                        # 执行监控
                        self.monitor.run_monitor()
                        
                        self.logger.info("监控任务完成")
                        self.status_bar.set_status("监控任务完成")
                        self.status_bar.set_progress(100)
                        messagebox.showinfo("成功", "监控任务执行完成")
                    except Exception as e:
                        error_msg = f"监控任务失败: {str(e)}"
                        self.status_bar.set_status(error_msg)
                        self.logger.error(error_msg)
                        messagebox.showerror("错误", error_msg)
                
                # 启动监控线程
                monitor_thread = threading.Thread(target=run_monitor_thread, daemon=True)
                monitor_thread.start()
                
            except Exception as e:
                error_msg = f"启动监控任务失败: {str(e)}"
                self.status_bar.set_status(error_msg)
                self.logger.error(error_msg)
                messagebox.showerror("错误", error_msg)
        
        self._add_task(monitor_task)

    def _run_test_monitor(self):
        """运行测试采集"""
        def test_task():
            try:
                self.logger.info("开始执行测试采集")
                
                def run_test_thread():
                    try:
                        # 获取配置中的关键词
                        keywords = self.config_manager.get('monitor', {}).get('keywords', [])
                        if not keywords:
                            raise ValueError("未配置关键词")
                            
                        # 获取配置中的数据源
                        sources = self.config_manager.get('monitor', {}).get('sources', [])
                        if not sources:
                            raise ValueError("未配置数据源")
                            
                        self.logger.info("开始测试采集数据...")
                        findings = self.monitor._monitor_sources(sources[:1], keywords)  # 只测试第一个数据源
                        
                        if findings:
                            self.logger.info(f"测试采集成功，找到 {len(findings)} 条结果")
                            for finding in findings:
                                self.logger.info(f"标题: {finding['title']}")
                                self.logger.info(f"链接: {finding['url']}")
                                self.logger.info(f"来源: {finding['source']}")
                                self.logger.info("---")
                        else:
                            self.logger.info("测试采集完成，未找到相关内容")
                            
                    except Exception as e:
                        self.logger.error(f"测试采集失败: {str(e)}")
                        raise
                
                # 启动测试线程
                test_thread = threading.Thread(target=run_test_thread, daemon=True)
                test_thread.start()
                
            except Exception as e:
                error_msg = f"启动测试采集失败: {str(e)}"
                self.status_bar.set_status(error_msg)
                self.logger.error(error_msg)
                messagebox.showerror("错误", error_msg)
        
        self._add_task(test_task)

    def _cleanup_data(self):
        """清理旧数据"""
        def cleanup_task():
            try:
                from services.storage import Storage
                storage = Storage()
                storage.cleanup_old_data()
                
                self.logger.info("旧数据清理完成")
                self.status_bar.set_status("旧数据清理完成")
            except Exception as e:
                self.logger.error(f"清理旧数据失败: {str(e)}")
                self.status_bar.set_status(f"清理旧数据失败: {str(e)}")
        
        self._add_task(cleanup_task)

    def _test_email(self):
        """测试邮件发送功能"""
        def test_email_task():
            try:
                self.status_bar.set_status("正在发送测试邮件...")
                
                # 检查邮件发送器是否初始化
                if not self.monitor.email_sender:
                    messagebox.showerror("错误", "邮件发送器未正确初始化，请检查邮件配置")
                    return
                
                # 获取邮件配置
                email_config = self.config_manager.get('email', {})
                receivers = email_config.get('receivers', [])
                
                if not receivers:
                    messagebox.showerror("错误", "未设置收件人邮箱")
                    return
                
                # 发送测试邮件
                subject = "星闪行业洞察 - 测试邮件"
                content = """
这是一封测试邮件，用于验证邮件发送功能是否正常。

如果您收到这封邮件，说明邮件发送功能工作正常。

星闪行业洞察系统
                """
                
                # 使用monitor中的email_sender发送测试邮件
                self.monitor.email_sender.send_email(
                    receivers=receivers,
                    subject=subject,
                    content=content
                )
                
                self.status_bar.set_status("测试邮件发送成功")
                messagebox.showinfo("成功", "测试邮件发送成功")
                
            except Exception as e:
                self.status_bar.set_status(f"测试邮件发送失败: {str(e)}")
                self.logger.error(f"测试邮件发送失败: {str(e)}")
                messagebox.showerror("错误", f"测试邮件发送失败: {str(e)}")
        
        self._add_task(test_email_task)

    def _show_about(self):
        """显示关于对话框"""
        about_text = """
星闪行业洞察 v1.0

一个用于监控和分析星闪行业信息的工具。

功能：
- 定时监控指定网站
- 关键词匹配和内容提取
- 自动生成分析报告
- 邮件通知

作者：Your Name
        """
        tk.messagebox.showinfo("关于", about_text)

    def _on_closing(self):
        """窗口关闭事件"""
        try:
            self.scheduler.stop()
            self.destroy()
        except Exception as e:
            self.logger.error(f"程序退出失败: {str(e)}")
            self.destroy()
