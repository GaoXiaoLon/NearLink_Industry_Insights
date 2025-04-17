import schedule
import time
import threading
from typing import Callable, Dict, Any, Optional
from datetime import datetime

class Scheduler:
    def __init__(self):
        self.jobs: Dict[str, schedule.Job] = {}
        self.running = False
        self.thread = None

    def add_job(self, 
                job_id: str, 
                func: Callable, 
                hour: int, 
                minute: int, 
                *args: Any, 
                **kwargs: Any) -> None:
        """添加定时任务"""
        if job_id in self.jobs:
            self.remove_job(job_id)
        
        job = schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(func, *args, **kwargs)
        self.jobs[job_id] = job

    def remove_job(self, job_id: str) -> None:
        """移除定时任务"""
        if job_id in self.jobs:
            schedule.cancel_job(self.jobs[job_id])
            del self.jobs[job_id]

    def get_next_run(self, job_id: str) -> Optional[datetime]:
        """获取任务下次运行时间"""
        if job_id in self.jobs:
            return self.jobs[job_id].next_run
        return None

    def _run_scheduler(self) -> None:
        """运行调度器"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def start(self) -> None:
        """启动调度器"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler)
            self.thread.daemon = True
            self.thread.start()

    def stop(self) -> None:
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None

    def clear(self) -> None:
        """清除所有任务"""
        schedule.clear()
        self.jobs.clear()
