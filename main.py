# main.py

import tkinter as tk
from gui.app import SparkMonitorApp
import logging
from utils.logger import get_logger


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(level=logging.INFO)
    logger = get_logger("main")
    logger.info("应用程序初始化")


def main():
    # 初始化日志
    setup_logging()

    # 创建主窗口
    root = tk.Tk()

    try:
        # 设置窗口图标 (如果有)
        try:
            root.iconbitmap('assets/icon.ico')  # 替换为您的图标路径
        except:
            pass

        # 创建应用实例
        app = SparkMonitorApp(root)

        # 启动主循环
        root.mainloop()

    except Exception as e:
        get_logger("main").error(f"应用程序错误: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()