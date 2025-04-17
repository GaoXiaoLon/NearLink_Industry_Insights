import tkinter as tk
from tkinter import ttk


class ConfigPanel(ttk.Frame):
    def __init__(self, parent, config_manager, save_callback):
        super().__init__(parent)
        self.config_manager = config_manager
        self.save_callback = save_callback
        self._setup_ui()

    def _setup_ui(self):
        # 创建滚动条
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 配置表单
        self._create_email_config()
        self._create_monitor_config()

        # 保存按钮
        self.save_btn = ttk.Button(
            self.scrollable_frame,
            text="保存配置",
            command=self._save_config
        )
        self.save_btn.pack(pady=10)

    def _create_email_config(self):
        """创建邮件配置部分"""
        email_frame = ttk.LabelFrame(self.scrollable_frame, text="邮件配置")
        email_frame.pack(fill=tk.X, padx=5, pady=5)

        config = self.config_manager.get_config('email') or {}

        # SMTP服务器
        ttk.Label(email_frame, text="SMTP服务器:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.smtp_server = ttk.Entry(email_frame)
        self.smtp_server.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.smtp_server.insert(0, config.get('smtp_server', ''))

        # SMTP端口
        ttk.Label(email_frame, text="SMTP端口:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.smtp_port = ttk.Entry(email_frame)
        self.smtp_port.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        self.smtp_port.insert(0, config.get('smtp_port', '587'))

        # 用户名
        ttk.Label(email_frame, text="用户名:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.email_username = ttk.Entry(email_frame)
        self.email_username.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        self.email_username.insert(0, config.get('username', ''))

        # 密码
        ttk.Label(email_frame, text="密码:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.email_password = ttk.Entry(email_frame, show="*")
        self.email_password.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)
        self.email_password.insert(0, config.get('password', ''))

        # 发件人
        ttk.Label(email_frame, text="发件人:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.email_sender = ttk.Entry(email_frame)
        self.email_sender.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)
        self.email_sender.insert(0, config.get('sender', ''))

        # 收件人
        ttk.Label(email_frame, text="收件人:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.email_recipient = ttk.Entry(email_frame)
        self.email_recipient.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=2)
        self.email_recipient.insert(0, config.get('recipient', ''))

        # 邮件主题
        ttk.Label(email_frame, text="邮件主题:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.email_subject = ttk.Entry(email_frame)
        self.email_subject.grid(row=6, column=1, sticky=tk.EW, padx=5, pady=2)
        self.email_subject.insert(0, config.get('subject', '星闪行业日报'))

        email_frame.columnconfigure(1, weight=1)

    def _create_monitor_config(self):
        """创建监测配置部分"""
        monitor_frame = ttk.LabelFrame(self.scrollable_frame, text="监测配置")
        monitor_frame.pack(fill=tk.X, padx=5, pady=5)

        config = self.config_manager.get_config('monitor') or {}

        # 执行时间
        ttk.Label(monitor_frame, text="执行时间:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.schedule_time = ttk.Entry(monitor_frame)
        self.schedule_time.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.schedule_time.insert(0, config.get('schedule_time', '09:00'))

        # 关键词
        ttk.Label(monitor_frame, text="关键词(用逗号分隔):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.keywords = ttk.Entry(monitor_frame)
        self.keywords.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        self.keywords.insert(0, ",".join(config.get('keywords', ['星闪'])))

        # 数据来源
        ttk.Label(monitor_frame, text="数据来源:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)

        source_frame = ttk.Frame(monitor_frame)
        source_frame.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        self.baidu_var = tk.BooleanVar(value='baidu' in config.get('sources', []))
        self.sogou_var = tk.BooleanVar(value='sogou' in config.get('sources', []))
        self.bing_var = tk.BooleanVar(value='bing' in config.get('sources', []))

        ttk.Checkbutton(source_frame, text="百度", variable=self.baidu_var).pack(side=tk.LEFT)
        ttk.Checkbutton(source_frame, text="搜狗", variable=self.sogou_var).pack(side=tk.LEFT)
        ttk.Checkbutton(source_frame, text="Bing", variable=self.bing_var).pack(side=tk.LEFT)

        monitor_frame.columnconfigure(1, weight=1)

    def _save_config(self):
        """保存配置"""
        email_config = {
            'smtp_server': self.smtp_server.get(),
            'smtp_port': int(self.smtp_port.get()),
            'username': self.email_username.get(),
            'password': self.email_password.get(),
            'sender': self.email_sender.get(),
            'recipient': self.email_recipient.get(),
            'subject': self.email_subject.get()
        }

        sources = []
        if self.baidu_var.get():
            sources.append('baidu')
        if self.sogou_var.get():
            sources.append('sogou')
        if self.bing_var.get():
            sources.append('bing')

        monitor_config = {
            'schedule_time': self.schedule_time.get(),
            'keywords': [k.strip() for k in self.keywords.get().split(',')],
            'sources': sources
        }

        new_config = {
            'email': email_config,
            'monitor': monitor_config
        }

        self.save_callback(new_config)