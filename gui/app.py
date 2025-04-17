import tkinter as tk
from tkinter import ttk, messagebox
from ..config.config_manager import ConfigManager
from ..monitor import SparkIndustryMonitor
from .config_panel import ConfigPanel
from .log_panel import LogPanel
import threading
from utils.logger import get_logger


class SparkMonitorApp:
    def __init__(self, root):
        self.root = root
        self.config_manager = ConfigManager()
        self.monitor = None
        self.monitor_thread = None
        self.logger = get_logger("gui")
        self._setup_ui()

    def _setup_ui(self):
        self.root.title("星闪行业监测系统")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 创建主容器
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建笔记本式布局
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 添加配置标签页
        self.config_panel = ConfigPanel(
            self.notebook,
            self.config_manager,
            self.on_config_save
        )
        self.notebook.add(self.config_panel, text="配置")

        # 添加日志标签页
        self.log_panel = LogPanel(self.notebook)
        self.notebook.add(self.log_panel, text="日志")

        # 控制按钮面板
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=(10, 0))

        self.start_btn = ttk.Button(
            self.control_frame,
            text="启动监测",
            command=self.start_monitoring
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            self.control_frame,
            text="停止监测",
            command=self.stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.test_email_btn = ttk.Button(
            self.control_frame,
            text="测试邮件",
            command=self.send_test_email
        )
        self.test_email_btn.pack(side=tk.LEFT, padx=5)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")

        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def on_config_save(self, new_config):
        """配置保存回调"""
        try:
            self.config_manager.update_config(new_config)
            self.status_var.set("配置保存成功")
            self.logger.info("配置已更新")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            self.logger.error(f"保存配置失败: {str(e)}")

    def start_monitoring(self):
        """启动监测服务"""
        if self.monitor is not None and self.monitor.running:
            messagebox.showwarning("警告", "监测服务已在运行中")
            return

        try:
            config = self.config_manager.get_config()
            self.monitor = SparkIndustryMonitor(config)

            self.monitor_thread = threading.Thread(
                target=self.monitor.start_service,
                daemon=True
            )
            self.monitor_thread.start()

            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_var.set("监测服务已启动")
            self.logger.info("监测服务启动")

        except Exception as e:
            messagebox.showerror("错误", f"启动监测失败: {str(e)}")
            self.logger.error(f"启动监测失败: {str(e)}")

    def stop_monitoring(self):
        """停止监测服务"""
        if self.monitor is None or not self.monitor.running:
            messagebox.showwarning("警告", "监测服务未运行")
            return

        try:
            self.monitor.stop_service()
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_var.set("监测服务已停止")
            self.logger.info("监测服务停止")
        except Exception as e:
            messagebox.showerror("错误", f"停止监测失败: {str(e)}")
            self.logger.error(f"停止监测失败: {str(e)}")

    def send_test_email(self):
        """发送测试邮件"""
        try:
            config = self.config_manager.get_config()
            if not config.get('email'):
                messagebox.showwarning("警告", "邮件配置未设置")
                return

            email_sender = EmailSender(config)
            test_html = "<h1>星闪行业监测系统测试邮件</h1><p>这是一封测试邮件，用于验证邮件发送功能是否正常。</p>"

            success = email_sender.send(test_html)
            if success:
                messagebox.showinfo("成功", "测试邮件发送成功")
                self.logger.info("测试邮件发送成功")
            else:
                messagebox.showerror("失败", "测试邮件发送失败")
                self.logger.error("测试邮件发送失败")
        except Exception as e:
            messagebox.showerror("错误", f"发送测试邮件失败: {str(e)}")
            self.logger.error(f"发送测试邮件失败: {str(e)}")

    def on_close(self):
        """关闭窗口事件处理"""
        if self.monitor is not None and self.monitor.running:
            if messagebox.askokcancel("退出", "监测服务仍在运行，确定要退出吗？"):
                self.monitor.stop_service()
                self.root.destroy()
        else:
            self.root.destroy()