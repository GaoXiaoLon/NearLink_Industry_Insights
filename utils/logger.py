import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    def __init__(self, log_dir: str = "logs"):
        """初始化日志器"""
        self.logger = logging.getLogger("星闪行业洞察")
        self.logger.setLevel(logging.DEBUG)
        
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 设置日志文件名
        log_file = os.path.join(log_dir, f"insight_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 记录启动信息
        self.info("日志系统初始化完成")
        self.info(f"日志文件: {log_file}")

    def debug(self, message: str, exc_info: bool = False):
        """记录调试信息"""
        self.logger.debug(message, exc_info=exc_info)

    def info(self, message: str, exc_info: bool = False):
        """记录一般信息"""
        self.logger.info(message, exc_info=exc_info)

    def warning(self, message: str, exc_info: bool = False):
        """记录警告信息"""
        self.logger.warning(message, exc_info=exc_info)

    def error(self, message: str, exc_info: bool = False):
        """记录错误信息"""
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False):
        """记录严重错误信息"""
        self.logger.critical(message, exc_info=exc_info)

    def set_level(self, level: int):
        """设置日志级别"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)
