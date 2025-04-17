import sys
import os
import traceback
import logging

# 设置基本日志配置
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)
logging.debug(f"项目根目录: {root_dir}")
logging.debug(f"Python路径: {sys.path}")

try:
    logging.debug("正在导入必要的模块...")
    from gui.app import App
    from utils.logger import Logger
    logging.debug("模块导入成功")
except Exception as e:
    logging.error(f"导入模块失败: {str(e)}")
    logging.error(f"错误堆栈: {traceback.format_exc()}")
    sys.exit(1)

def main():
    """程序入口"""
    try:
        # 初始化日志
        logger = Logger()
        logger.info("程序启动")
        logger.debug(f"Python路径: {sys.path}")
        logger.debug(f"当前工作目录: {os.getcwd()}")
        
        # 创建应用
        logger.debug("正在创建应用...")
        app = App()
        logger.debug("应用创建完成")
        
        # 运行主循环
        logger.debug("开始运行主循环...")
        app.mainloop()
        logger.debug("主循环结束")
        
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"程序运行错误: {str(e)}")
            logger.error(f"错误堆栈: {traceback.format_exc()}")
        else:
            logging.error(f"程序运行错误: {str(e)}")
            logging.error(f"错误堆栈: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()