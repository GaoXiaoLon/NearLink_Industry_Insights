import tkinter as tk
from tkinter import ttk
from typing import Callable
from gui.components.widgets import LabeledEntry, TimePicker, ToolTip
from datetime import datetime, timedelta

class ConfigPanel(ttk.Frame):
    def __init__(self, master, config_manager, on_save: Callable = None):
        super().__init__(master)
        self.config_manager = config_manager
        self.on_save = on_save
        
        self._create_widgets()
        self._load_config()

    def _create_widgets(self):
        """创建配置界面组件"""
        # 创建笔记本
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 邮件配置标签页
        email_frame = ttk.Frame(notebook)
        notebook.add(email_frame, text="邮件配置")
        self._create_email_tab(email_frame)
        
        # 监控配置标签页
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="监控配置")
        self._create_monitor_tab(monitor_frame)

    def _create_email_tab(self, parent):
        """创建邮件配置标签页"""
        # SMTP服务器配置
        self.smtp_server = LabeledEntry(parent, "SMTP服务器:")
        self.smtp_server.pack(fill="x", padx=5, pady=2)
        ToolTip(self.smtp_server, "邮件服务器地址，例如：smtp.example.com")
        
        self.smtp_port = LabeledEntry(parent, "SMTP端口:")
        self.smtp_port.pack(fill="x", padx=5, pady=2)
        ToolTip(self.smtp_port, "邮件服务器端口，例如：587")
        
        self.email_username = LabeledEntry(parent, "邮箱账号:")
        self.email_username.pack(fill="x", padx=5, pady=2)
        ToolTip(self.email_username, "发送邮件的邮箱账号")
        
        self.email_password = LabeledEntry(parent, "邮箱密码:", show="*")
        self.email_password.pack(fill="x", padx=5, pady=2)
        ToolTip(self.email_password, "邮箱密码或授权码")
        
        self.sender = LabeledEntry(parent, "发件人:")
        self.sender.pack(fill="x", padx=5, pady=2)
        ToolTip(self.sender, "发件人邮箱地址")
        
        # 收件人列表
        ttk.Label(parent, text="收件人列表:").pack(anchor="w", padx=5, pady=2)
        self.receivers = tk.Text(parent, height=5)
        self.receivers.pack(fill="x", padx=5, pady=2)
        ToolTip(self.receivers, "每行一个收件人邮箱地址")
        
        # 执行时间设置
        time_frame = ttk.LabelFrame(parent, text="执行时间设置")
        time_frame.pack(fill="x", padx=5, pady=5)
        
        # 创建时间设置框架
        time_setting_frame = ttk.Frame(time_frame)
        time_setting_frame.pack(fill="x", padx=5, pady=5)
        
        # 创建时间选择器
        time_picker_frame = ttk.Frame(time_setting_frame)
        time_picker_frame.pack(side="left", padx=5)
        
        ttk.Label(time_picker_frame, text="执行时间:").pack()
        self.time_picker = TimePicker(time_picker_frame)
        self.time_picker.pack(pady=5)
        
        # 创建执行频率设置
        frequency_frame = ttk.Frame(time_setting_frame)
        frequency_frame.pack(side="left", padx=20)
        
        ttk.Label(frequency_frame, text="执行频率:").pack()
        self.frequency_var = tk.StringVar(value="daily")
        frequency_options = ["daily", "weekly", "monthly"]
        frequency_menu = ttk.OptionMenu(
            frequency_frame,
            self.frequency_var,
            self.frequency_var.get(),
            *frequency_options
        )
        frequency_menu.pack(pady=5)
        
        # 创建执行状态显示
        status_frame = ttk.Frame(time_setting_frame)
        status_frame.pack(side="left", padx=20)
        
        ttk.Label(status_frame, text="下次执行时间:").pack()
        self.next_run_label = ttk.Label(status_frame, text="")
        self.next_run_label.pack(pady=5)

    def _create_monitor_tab(self, parent):
        """创建监控配置标签页"""
        # 关键词列表
        keyword_frame = ttk.LabelFrame(parent, text="监控关键词")
        keyword_frame.pack(fill="x", padx=5, pady=5)
        
        self.keywords = tk.Text(keyword_frame, height=5)
        self.keywords.pack(fill="x", padx=5, pady=2)
        ToolTip(self.keywords, "每行一个关键词")
        
        # 监控来源列表
        source_frame = ttk.LabelFrame(parent, text="监控来源")
        source_frame.pack(fill="x", padx=5, pady=5)
        
        self.sources = tk.Text(source_frame, height=5)
        self.sources.pack(fill="x", padx=5, pady=2)
        ToolTip(self.sources, "每行一个监控网站URL")

    def _load_config(self):
        """加载配置"""
        # 加载邮件配置
        email_config = self.config_manager.get('email', {})
        self.smtp_server.set(email_config.get('smtp_server', ''))
        self.smtp_port.set(str(email_config.get('smtp_port', '')))
        self.email_username.set(email_config.get('username', ''))
        self.email_password.set(email_config.get('password', ''))
        self.sender.set(email_config.get('sender', ''))
        self.receivers.delete(1.0, tk.END)
        self.receivers.insert(tk.END, '\n'.join(email_config.get('receivers', [])))
        
        # 加载监控配置
        monitor_config = self.config_manager.get('monitor', {})
        schedule = monitor_config.get('schedule', {})
        self.time_picker.set_time(schedule.get('hour', 8), schedule.get('minute', 0))
        self.frequency_var.set(schedule.get('frequency', 'daily'))
        self._update_next_run_time()
        
        # 加载关键词和来源
        self.keywords.delete(1.0, tk.END)
        self.keywords.insert(tk.END, '\n'.join(monitor_config.get('keywords', [])))
        self.sources.delete(1.0, tk.END)
        self.sources.insert(tk.END, '\n'.join(monitor_config.get('sources', [])))

    def _update_next_run_time(self):
        """更新下次执行时间显示"""
        try:
            monitor_config = self.config_manager.get('monitor', {})
            schedule = monitor_config.get('schedule', {})
            hour = schedule.get('hour', 8)
            minute = schedule.get('minute', 0)
            frequency = schedule.get('frequency', 'daily')
            
            # 计算下次执行时间
            now = datetime.now()
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if frequency == 'daily':
                if now > next_run:
                    next_run += timedelta(days=1)
            elif frequency == 'weekly':
                if now > next_run:
                    next_run += timedelta(days=7)
            elif frequency == 'monthly':
                if now > next_run:
                    next_run = next_run.replace(day=1) + timedelta(days=32)
                    next_run = next_run.replace(day=1)
            
            self.next_run_label.config(text=next_run.strftime("%Y-%m-%d %H:%M"))
        except Exception as e:
            self.next_run_label.config(text="未知")

    def _save_config(self):
        """保存配置"""
        try:
            # 保存邮件配置
            email_config = {
                'smtp_server': self.smtp_server.get(),
                'smtp_port': int(self.smtp_port.get()),
                'username': self.email_username.get(),
                'password': self.email_password.get(),
                'sender': self.sender.get(),
                'receivers': [r.strip() for r in self.receivers.get(1.0, tk.END).split('\n') if r.strip()]
            }
            self.config_manager.set('email', email_config)
            
            # 保存监控配置
            hour, minute = self.time_picker.get_time()
            monitor_config = {
                'schedule': {
                    'hour': hour,
                    'minute': minute,
                    'frequency': self.frequency_var.get()
                },
                'keywords': [k.strip() for k in self.keywords.get(1.0, tk.END).split('\n') if k.strip()],
                'sources': [s.strip() for s in self.sources.get(1.0, tk.END).split('\n') if s.strip()]
            }
            self.config_manager.set('monitor', monitor_config)
            
            if self.on_save:
                self.on_save()
                
        except Exception as e:
            tk.messagebox.showerror("错误", f"保存配置失败: {str(e)}")
