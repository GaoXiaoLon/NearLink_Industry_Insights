import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import datetime
import logging
import queue

logger = logging.getLogger(__name__)

class ScrolledText(tk.Text):
    """带滚动条的文本框"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.yview)
        self.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.pack(side="left", fill="both", expand=True)

class LabeledEntry(ttk.Frame):
    """带标签的输入框"""
    def __init__(self, master, label: str, **kwargs):
        super().__init__(master)
        self.label = ttk.Label(self, text=label)
        self.entry = ttk.Entry(self, **kwargs)
        self.label.pack(side="left", padx=5)
        self.entry.pack(side="left", fill="x", expand=True, padx=5)

    def get(self) -> str:
        return self.entry.get()

    def set(self, value: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)

class TimePicker(ttk.Frame):
    """时间选择器"""
    def __init__(self, master, **kwargs):
        super().__init__(master)
        
        # 小时选择
        self.hour_var = tk.StringVar(value="00")
        self.hour_spinbox = ttk.Spinbox(
            self,
            from_=0,
            to=23,
            width=2,
            textvariable=self.hour_var,
            format="%02.0f"
        )
        
        # 分钟选择
        self.minute_var = tk.StringVar(value="00")
        self.minute_spinbox = ttk.Spinbox(
            self,
            from_=0,
            to=59,
            width=2,
            textvariable=self.minute_var,
            format="%02.0f"
        )
        
        # 布局
        self.hour_spinbox.pack(side="left", padx=2)
        ttk.Label(self, text=":").pack(side="left")
        self.minute_spinbox.pack(side="left", padx=2)

    def get_time(self) -> tuple[int, int]:
        """获取选择的时间"""
        return int(self.hour_var.get()), int(self.minute_var.get())

    def set_time(self, hour: int, minute: int) -> None:
        """设置时间"""
        self.hour_var.set(f"{hour:02d}")
        self.minute_var.set(f"{minute:02d}")

class StatusBar(ttk.Frame):
    """状态栏"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.pack(side="left", padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            mode='determinate'
        )
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=5)

    def set_status(self, text: str) -> None:
        """设置状态文本"""
        self.status_var.set(text)

    def set_progress(self, value: float) -> None:
        """设置进度"""
        self.progress_var.set(value)

class LogViewer(ttk.Frame):
    """日志查看器"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # 创建文本框
        self.text = ScrolledText(self, wrap=tk.WORD, state='disabled')
        self.text.pack(fill="both", expand=True)
        
        # 创建标签
        self.tags = {
            'INFO': {'foreground': 'black'},
            'WARNING': {'foreground': 'orange'},
            'ERROR': {'foreground': 'red'},
            'DEBUG': {'foreground': 'gray'}
        }
        
        for tag, config in self.tags.items():
            self.text.tag_configure(tag, **config)
            
        # 创建消息队列
        self.msg_queue = queue.Queue()
        
        # 启动消息处理
        self.process_messages()

    def process_messages(self):
        """处理消息队列中的消息"""
        try:
            while True:
                try:
                    level, message = self.msg_queue.get_nowait()
                    self._add_log_internal(level, message)
                except queue.Empty:
                    break
        finally:
            # 继续检查消息队列
            self.after(100, self.process_messages)

    def add_log(self, level: str, message: str) -> None:
        """添加日志（线程安全）"""
        self.msg_queue.put((level, message))

    def _add_log_internal(self, level: str, message: str) -> None:
        """内部添加日志（非线程安全）"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.text.configure(state='normal')
        self.text.insert(tk.END, log_entry)
        self.text.tag_add(level, "end-2c linestart", "end-1c")
        self.text.see(tk.END)
        self.text.configure(state='disabled')

    def clear(self) -> None:
        """清空日志"""
        self.text.configure(state='normal')
        self.text.delete(1.0, tk.END)
        self.text.configure(state='disabled')

class ToolTip:
    """工具提示"""
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        """鼠标进入时显示提示"""
        try:
            # 获取鼠标位置
            x = self.widget.winfo_rootx() + 10
            y = self.widget.winfo_rooty() + 20
            
            # 创建提示窗口
            self.tw = tk.Toplevel(self.widget)
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(self.tw, text=self.text, justify=tk.LEFT,
                           background="#ffffe0", relief=tk.SOLID, borderwidth=1)
            label.pack(ipadx=1)
            
        except Exception as e:
            logger.error(f"显示工具提示失败: {str(e)}")

    def leave(self, event=None):
        """鼠标离开时隐藏提示"""
        if hasattr(self, 'tw') and self.tw:
            self.tw.destroy()
            self.tw = None
