import tkinter as tk
from tkinter import ttk
from gui.components.widgets import LogViewer, ToolTip

class LogPanel(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._create_widgets()

    def _create_widgets(self):
        """创建日志界面组件"""
        # 工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        # 清空按钮
        clear_button = ttk.Button(toolbar, text="清空日志", command=self.clear_logs)
        clear_button.pack(side="left", padx=5)
        ToolTip(clear_button, "清空所有日志记录")
        
        # 导出按钮
        export_button = ttk.Button(toolbar, text="导出日志", command=self.export_logs)
        export_button.pack(side="left", padx=5)
        ToolTip(export_button, "将日志导出到文件")
        
        # 日志级别选择
        level_frame = ttk.Frame(toolbar)
        level_frame.pack(side="right", padx=5)
        
        ttk.Label(level_frame, text="日志级别:").pack(side="left")
        self.level_var = tk.StringVar(value="ALL")
        level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.level_var,
            values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=10
        )
        level_combo.pack(side="left", padx=5)
        level_combo.bind("<<ComboboxSelected>>", self._on_level_change)
        
        # 日志查看器
        self.log_viewer = LogViewer(self)
        self.log_viewer.pack(fill="both", expand=True, padx=5, pady=5)

    def add_log(self, level: str, message: str):
        """添加日志"""
        self.log_viewer.add_log(level, message)

    def clear_logs(self):
        """清空日志"""
        self.log_viewer.clear()

    def export_logs(self):
        """导出日志"""
        import tkinter.filedialog as filedialog
        import datetime
        
        # 选择保存文件
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("所有文件", "*.*")],
            initialfile=f"logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_viewer.text.get(1.0, tk.END))
                tk.messagebox.showinfo("成功", "日志导出成功")
            except Exception as e:
                tk.messagebox.showerror("错误", f"导出日志失败: {str(e)}")

    def _on_level_change(self, event=None):
        """日志级别改变事件"""
        level = self.level_var.get()
        if level == "ALL":
            # 显示所有日志
            self.log_viewer.text.tag_configure("DEBUG", foreground="gray")
            self.log_viewer.text.tag_configure("INFO", foreground="black")
            self.log_viewer.text.tag_configure("WARNING", foreground="orange")
            self.log_viewer.text.tag_configure("ERROR", foreground="red")
        else:
            # 只显示指定级别及以上的日志
            for tag in ["DEBUG", "INFO", "WARNING", "ERROR"]:
                if self._get_level_value(tag) >= self._get_level_value(level):
                    self.log_viewer.text.tag_configure(tag, foreground="black")
                else:
                    self.log_viewer.text.tag_configure(tag, foreground="gray")

    def _get_level_value(self, level: str) -> int:
        """获取日志级别的数值"""
        levels = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3
        }
        return levels.get(level, 0)
