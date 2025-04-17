# main.py
import sys
import os
from pathlib import Path

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

from gui.app import SparkMonitorApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = SparkMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()