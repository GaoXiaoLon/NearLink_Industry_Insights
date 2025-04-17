# utils/scheduler.py

import schedule
import time
import threading
from utils.logger import get_logger


class Scheduler:
    def __init__(self):
        self.logger = get_logger("scheduler")
        self._running = False
        self._thread = None

    def add_daily_job(self, time_str, job_func):
        """添加每日定时任务"""
        schedule.every().day.at(time_str).do(job_func)
        self.logger.info(f"已添加每日任务，执行时间: {time_str}")

    def add_hourly_job(self, job_func, minute=0):
        """添加每小时定时任务"""
        schedule.every().hour.at(f":{minute:02d}").do(job_func)
        self.logger.info(f"已添加每小时任务，在 {minute} 分执行")

    def start(self):
        """启动调度器"""
        if self._running:
            self.logger.warning("调度器已在运行中")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.logger.info("调度器已启动")

    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        self.logger.info("调度器已停止")

    def _run(self):
        """调度器运行循环"""
        while self._running:
            schedule.run_pending()
            time.sleep(1)

    def clear(self):
        """清除所有任务"""
        schedule.clear()
        self.logger.info("已清除所有定时任务")