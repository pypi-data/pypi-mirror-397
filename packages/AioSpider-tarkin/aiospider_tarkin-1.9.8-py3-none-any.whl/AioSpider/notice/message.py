import psutil
import socket
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

# 影响范围 数据质量可能受到影响
# 建议操作 检查数据源，更新字段映射
# 管理链接 http://监控面板链接
# 重试次数 3/5
# 最后成功运行 2024-08-17 14:30:00

def get_performance_metrics():
    """
    计算CPU、内存、磁盘使用率
    """
    try:
        # CPU 使用率
        cpu = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory = memory.percent
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk = disk.percent
    except Exception as e:
        cpu = '-'
        memory = '-'
        disk = '-'

    return f"CPU: {cpu}, MEM: {memory}, DISK: {disk}"


def get_server_ip():
    """
    获取服务器IP
    """
    return socket.gethostbyname(socket.gethostname())


def get_env():
    from AioSpider import settings
    return '调试环境' if settings.DEBUG else '生产环境'


@dataclass(frozen=True, slots=True, unsafe_hash=True, kw_only=True)
class NoticeMessage:
    notice_time: str
    spider_name: str
    level: str
    message: str
    env: str = field(default_factory=get_env)
    server_ip: str = field(default_factory=get_server_ip)
    task_id: Optional[str] = field(default=None)
    exception_stack: Optional[str] = field(default=None)
    impact_range: Optional[str] = field(default=None)
    suggestion: Optional[str] = field(default=None)
    performance_info: str = field(default_factory=get_performance_metrics)
    contact_list: Optional[List[str]] = field(default=None)
    admin_url: Optional[str] = field(default=None)

    def convert_level(self):
        level_map = {
            'LEVEL1': '轻微',
            'LEVEL2': '调试', 
            'LEVEL3': '信息',
            'LEVEL4': '警告',
            'LEVEL5': '错误',
            'LEVEL6': '严重',
            'LEVEL7': '崩溃'
        }
        if self.level not in level_map:
            raise ValueError(f'日志级别错误: {self.level}')
        return f"{self.level} - {level_map[self.level]}"

    def get_data(self):
        return {
            "预警时间": self.notice_time,
            "爬虫名称": self.spider_name,
            "预警级别": self.convert_level(),
            "预警消息": self.message,
            "环境信息": self.env,
            "服务器IP": self.server_ip,
            "任务ID": self.task_id,
            "异常堆栈": self.exception_stack,
            "影响范围": self.impact_range,
            "建议操作": self.suggestion,
            "管理链接": self.admin_url,
            "性能指标": self.performance_info,
            "联系人": ' '.join(self.contact_list)
        }
    
    def get_notice_data(self):
        return {
            "notice_time": self.notice_time,
            "spider_name": self.spider_name,
            "level": self.level,
            "message": self.message,
            "env": self.env,
            "server_ip": self.server_ip,
            "task_id": self.task_id,
            "exception_stack": self.exception_stack,
            "impact_range": self.impact_range,
            "suggestion": self.suggestion,
            "performance_info": self.performance_info,
        }

    def __str__(self):
        mapping = self.get_data()
        return "\n".join([f"{key}\t\t{value}" for key, value in mapping.items() if value is not None])

