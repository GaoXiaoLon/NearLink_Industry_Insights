import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime


class LogPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.log_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('Consolas', 10)
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area.config(state=tk.DISABLED)

        # 控制按钮
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        self.clear_btn = ttk.Button(
            btn_frame,
            text="清空日志",
            command=self.clear_log
        )
        self.clear_btn.pack(side=tk.LEFT)

        self.save_btn = ttk.Button(
            btn_frame,
            text="保存日志",
            command=self.save_log
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

    def add_log(self, message, level="INFO"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] [{level}] {message}\n"

        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, formatted_msg)
        self.log_area.config(state=tk.DISABLED)
        self.log_area.see(tk.END)

    def clear_log(self):
        """清空日志"""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)

    def save_log(self):
        """保存日志到文件"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_area.get(1.0, tk.END))
                self.add_log(f"日志已保存到 {file_path}")
            except Exception as e:
                self.add_log(f"保存日志失败: {str(e)}", "ERROR")