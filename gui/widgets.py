# gui/widgets.py

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from typing import Optional, Callable
from utils.logger import get_logger

logger = get_logger("widgets")


class LabelInput(ttk.Frame):
    """带有标签的输入控件组合"""

    def __init__(
            self,
            parent,
            label_text: str,
            input_class=ttk.Entry,
            input_var: Optional[tk.Variable] = None,
            input_args: Optional[dict] = None,
            label_args: Optional[dict] = None,
            **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.input_args = input_args or {}
        self.label_args = label_args or {}

        # 创建变量（如果没有提供）
        if input_var:
            self.variable = input_var
        else:
            if input_class in (ttk.Checkbutton, ttk.Radiobutton):
                self.variable = tk.BooleanVar()
            else:
                self.variable = tk.StringVar()

        # 创建标签
        self.label = ttk.Label(self, text=label_text, **self.label_args)
        self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))

        # 创建输入控件
        if input_class == ttk.OptionMenu:
            self.input = ttk.OptionMenu(
                self,
                self.variable,
                *self.input_args.get('options', [])
            )
        elif input_class == ttk.Button:
            self.input = ttk.Button(
                self,
                text=self.input_args.get('text', ''),
                command=self.input_args.get('command', None)
            )
        else:
            self.input = input_class(self, textvariable=self.variable, **self.input_args)

        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))

        self.columnconfigure(0, weight=1)

    def grid(self, **kwargs):
        """覆盖默认grid方法，添加默认的padx/pady"""
        kwargs.setdefault('padx', 5)
        kwargs.setdefault('pady', 5)
        super().grid(**kwargs)

    def get(self):
        """获取输入值"""
        try:
            return self.variable.get()
        except (TypeError, tk.TclError):
            return None

    def set(self, value):
        """设置输入值"""
        self.variable.set(value)


class ToolTip:
    """创建工具提示"""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self._delay = 500  # 毫秒
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event=None):
        """显示工具提示"""
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=1)

    def hidetip(self, event=None):
        """隐藏工具提示"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class ScrollableFrame(ttk.Frame):
    """可滚动的Frame容器"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # 创建Canvas和滚动条
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # 配置Canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        self.scrollable_frame.bind("<Enter>", self._bind_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class ValidatedEntry(ttk.Entry):
    """带验证的输入框"""

    def __init__(
            self,
            parent,
            validator: Callable[[str], bool],
            invalid_bg='#ffdddd',
            **kwargs
    ):
        self.validator = validator
        self.invalid_bg = invalid_bg
        self.valid = True

        self.var = tk.StringVar()
        super().__init__(parent, textvariable=self.var, **kwargs)

        self.default_bg = self['style'] if 'style' in kwargs else self.cget('background')
        self.var.trace_add('write', self._validate)

    def _validate(self, *args):
        value = self.var.get()
        if self.validator(value):
            self.config(style='TEntry' if 'style' in self.keys() else None)
            self.valid = True
        else:
            self.config(style='Invalid.TEntry' if 'style' in self.keys() else None)
            self.valid = False

    def get_validated(self):
        """获取验证后的值，如果无效返回None"""
        return self.var.get() if self.valid else None


class PathInput(LabelInput):
    """路径选择输入组件"""

    def __init__(
            self,
            parent,
            label_text,
            dialog_title="选择文件",
            dialog_type='open',  # 'open' 或 'save'
            file_types=(("All files", "*.*"),),
            **kwargs
    ):
        super().__init__(
            parent,
            label_text,
            input_class=ttk.Entry,
            **kwargs
        )

        self.dialog_title = dialog_title
        self.dialog_type = dialog_type
        self.file_types = file_types

        # 添加浏览按钮
        self.browse_button = ttk.Button(
            self,
            text="浏览...",
            command=self._on_browse
        )
        self.browse_button.grid(row=1, column=1, sticky=tk.W)

    def _on_browse(self):
        """打开文件对话框"""
        if self.dialog_type == 'open':
            path = filedialog.askopenfilename(
                title=self.dialog_title,
                filetypes=self.file_types
            )
        else:
            path = filedialog.asksaveasfilename(
                title=self.dialog_title,
                filetypes=self.file_types,
                defaultextension=self.file_types[0][1] if self.file_types else ''
            )

        if path:
            self.set(path)


class StatusBar(ttk.Frame):
    """状态栏组件"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.status_var = tk.StringVar()
        self.status_var.set("就绪")

        self.label = ttk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.label.pack(fill=tk.X)

    def set_status(self, text):
        """设置状态文本"""
        self.status_var.set(text)
        self.update_idletasks()

    def clear_status(self):
        """清除状态文本"""
        self.set_status("")


class ToggledFrame(ttk.Frame):
    """可折叠的面板"""

    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, **kwargs)

        self.show = tk.BooleanVar(value=False)
        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill=tk.X, expand=1)

        ttk.Label(self.title_frame, text=text).pack(side=tk.LEFT, fill=tk.X, expand=1)

        self.toggle_button = ttk.Checkbutton(
            self.title_frame,
            width=2,
            text='+',
            command=self._toggle,
            variable=self.show,
            style='Toolbutton'
        )
        self.toggle_button.pack(side=tk.LEFT)

        self.sub_frame = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)

    def _toggle(self):
        """切换折叠状态"""
        if self.show.get():
            self.sub_frame.pack(fill=tk.X, expand=1)
            self.toggle_button.configure(text='-')
        else:
            self.sub_frame.forget()
            self.toggle_button.configure(text='+')

    def add_widgets(self, *widgets):
        """向子框架添加控件"""
        for widget in widgets:
            widget.pack(in_=self.sub_frame, fill=tk.X, expand=1, pady=2)