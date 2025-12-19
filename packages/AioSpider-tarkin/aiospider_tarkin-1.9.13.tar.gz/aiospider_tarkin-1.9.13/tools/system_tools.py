import os
import re
import socket
import subprocess
import psutil

from typing import List, Optional
from AioSpider import logger

__all__ = [
    'get_ipv4',
    'is_port_in_use',
    'execute_command',
    'run_python_script',
    'kill_process_by_port',
    'get_process_info',
    'list_python_processes',
    'monitor_system_resources',
    'create_process_snapshot'
]


def get_ipv4() -> str:
    """获取本机IPv4地址"""
    try:
        return socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        logger.error("无法获取本机IP地址")
        return ""

def is_port_in_use(port: int) -> bool:
    """检查指定端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def execute_command(command: str, keep_window: bool = False) -> Optional[int]:
    """执行命令行指令"""
    try:
        if keep_window:
            process = subprocess.Popen(f'start cmd /k {command}', shell=True)
        else:
            process = subprocess.Popen(f'start cmd /c {command}', shell=True)
        return process.pid
    except subprocess.SubprocessError as e:
        logger.error(f"执行命令失败: {e}")
        return None


def run_python_script(script_path: str, keep_window: bool = False) -> Optional[int]:
    """在后台运行Python脚本"""
    return execute_command(f'python "{script_path}"', keep_window)


def kill_process_by_port(port: int) -> None:
    """通过端口号终止进程"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            try:
                process = psutil.Process(conn.pid)
                process.terminate()
                logger.info(f"已终止使用端口 {port} 的进程 (PID: {conn.pid})")
            except psutil.NoSuchProcess:
                logger.warning(f"进程 {conn.pid} 不存在")


def get_process_info(pid: int) -> Optional[dict]:
    """获取指定PID的进程信息"""
    try:
        process = psutil.Process(pid)
        return {
            "pid": pid,
            "name": process.name(),
            "status": process.status(),
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent()
        }
    except psutil.NoSuchProcess:
        logger.warning(f"进程 {pid} 不存在")
        return None


def list_python_processes() -> List[dict]:
    """列出所有Python进程"""
    return [get_process_info(p.pid) for p in psutil.process_iter(['pid', 'name']) if 'python' in p.name().lower()]


def monitor_system_resources() -> dict:
    """监控系统资源使用情况"""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }


def create_process_snapshot() -> List[dict]:
    """创建当前进程快照"""
    return [get_process_info(p.pid) for p in psutil.process_iter(['pid', 'name', 'status'])]
