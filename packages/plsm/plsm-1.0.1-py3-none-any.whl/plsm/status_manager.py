"""
服务状态管理模块
负责服务的状态监控、查询和管理
"""

import subprocess
import time
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class ServiceStatus(Enum):
    """服务状态枚举
    
    Attributes:
        ACTIVE: 服务处于活动状态
        INACTIVE: 服务处于非活动状态
        FAILED: 服务启动失败
        ACTIVATING: 服务正在启动中
        DEACTIVATING: 服务正在停止中
        UNKNOWN: 服务状态未知
    """
    ACTIVE = "active"
    INACTIVE = "inactive" 
    FAILED = "failed"
    ACTIVATING = "activating"
    DEACTIVATING = "deactivating"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """服务详细信息
    
    Attributes:
        name: 服务名称
        status: 服务状态枚举值
        description: 服务描述信息
        loaded: 服务是否已加载
        active: 服务是否处于活跃状态
        running: 服务是否正在运行
        pid: 服务进程ID
        memory_usage: 内存使用量(KB)
        cpu_usage: CPU使用率
        uptime: 服务运行时间(秒)
        last_error: 最后一次错误信息
    """
    name: str
    status: ServiceStatus
    description: str = ""
    loaded: bool = False
    active: bool = False
    running: bool = False
    pid: Optional[int] = None
    memory_usage: Optional[int] = None
    cpu_usage: Optional[float] = None
    uptime: Optional[float] = None
    last_error: str = ""


class ServiceStatusManager:
    """服务状态管理器"""
    
    def __init__(self, sudo: bool = False):
        """
        初始化状态管理器
        
        Args:
            sudo: 是否使用sudo执行特权操作
        """
        self.sudo = sudo
        self._systemctl_cmd = ["systemctl"]
        if sudo:
            self._systemctl_cmd.insert(0, "sudo")
    
    def get_status(self, service_name: str) -> Optional[ServiceInfo]:
        """
        获取服务状态
        
        Args:
            service_name: 服务名称
            
        Returns:
            ServiceInfo: 服务信息对象，如果服务不存在返回None
        """
        try:
            # 使用systemctl show获取详细信息
            result = subprocess.run(
                self._systemctl_cmd + ["show", service_name, "--no-pager"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            info = self._parse_systemctl_show(result.stdout, service_name)
            
            # 获取进程信息
            self._get_process_info(info)
            
            return info
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return None
    
    def _parse_systemctl_show(self, output: str, service_name: str) -> ServiceInfo:
        """解析systemctl show输出"""
        info = ServiceInfo(name=service_name, status=ServiceStatus.UNKNOWN)
        
        for line in output.strip().split('\n'):
            if '=' not in line:
                continue
            
            key, value = line.split('=', 1)
            
            if key == "LoadState":
                info.loaded = (value == "loaded")
            elif key == "ActiveState":
                info.active = (value == "active")
                info.status = self._map_status(value)
            elif key == "SubState":
                info.running = (value == "running")
            elif key == "Description":
                info.description = value
            elif key == "MainPID":
                if value.isdigit() and int(value) > 0:
                    info.pid = int(value)
            
        return info
    
    def _map_status(self, state: str) -> ServiceStatus:
        """映射状态字符串到枚举"""
        status_map = {
            "active": ServiceStatus.ACTIVE,
            "inactive": ServiceStatus.INACTIVE,
            "failed": ServiceStatus.FAILED,
            "activating": ServiceStatus.ACTIVATING,
            "deactivating": ServiceStatus.DEACTIVATING,
        }
        return status_map.get(state, ServiceStatus.UNKNOWN)
    
    def _get_process_info(self, info: ServiceInfo):
        """获取进程详细信息"""
        if not info.pid:
            return
        
        try:
            # 获取进程启动时间
            result = subprocess.run(
                ["ps", "-o", "etimes=", "-p", str(info.pid)],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip().isdigit():
                info.uptime = int(result.stdout.strip())
            
            # 获取内存使用情况
            result = subprocess.run(
                ["ps", "-o", "rss=", "-p", str(info.pid)],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip().isdigit():
                info.memory_usage = int(result.stdout.strip())  # KB
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
    
    def is_running(self, service_name: str) -> bool:
        """
        检查服务是否正在运行
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否正在运行
        """
        info = self.get_status(service_name)
        return info.running if info else False
    
    def is_active(self, service_name: str) -> bool:
        """
        检查服务是否激活
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否激活
        """
        info = self.get_status(service_name)
        return info.active if info else False
    
    def is_enabled(self, service_name: str) -> bool:
        """
        检查服务是否启用
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否启用
        """
        try:
            result = subprocess.run(
                self._systemctl_cmd + ["is-enabled", service_name],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def list_services(self, filter_status: Optional[ServiceStatus] = None) -> List[ServiceInfo]:
        """
        列出所有服务及其状态
        
        Args:
            filter_status: 过滤状态
            
        Returns:
            List[ServiceInfo]: 服务信息列表
        """
        try:
            result = subprocess.run(
                self._systemctl_cmd + ["list-units", "--type=service", "--no-legend", "--no-pager"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            services = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                # 解析输出格式: UNIT LOAD ACTIVE SUB DESCRIPTION
                parts = line.split()
                if len(parts) >= 4:
                    service_name = parts[0]
                    if service_name.endswith('.service'):
                        service_name = service_name[:-8]
                    
                    status = self._map_status(parts[3])
                    
                    if filter_status is None or status == filter_status:
                        info = ServiceInfo(
                            name=service_name,
                            status=status,
                            description=' '.join(parts[4:]) if len(parts) > 4 else "",
                            loaded=(parts[1] == "loaded"),
                            active=(parts[2] == "active"),
                            running=(parts[3] == "running")
                        )
                        services.append(info)
            
            return services
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return []
    
    def get_failed_services(self) -> List[ServiceInfo]:
        """
        获取失败的服务列表
        
        Returns:
            List[ServiceInfo]: 失败的服务信息列表
        """
        return self.list_services(ServiceStatus.FAILED)
    
    def get_running_services(self) -> List[ServiceInfo]:
        """
        获取正在运行的服务列表
        
        Returns:
            List[ServiceInfo]: 运行中的服务信息列表
        """
        return [s for s in self.list_services() if s.running]
    
    def monitor_service(self, service_name: str, duration: int = 60) -> List[Tuple[float, ServiceInfo]]:
        """
        监控服务状态变化
        
        Args:
            service_name: 服务名称
            duration: 监控时长（秒）
            
        Returns:
            List[Tuple[float, ServiceInfo]]: 时间戳和服务状态的列表
        """
        history = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            info = self.get_status(service_name)
            if info:
                history.append((time.time() - start_time, info))
            time.sleep(1)
        
        return history
    
    def get_service_logs(self, service_name: str, lines: int = 50) -> Optional[str]:
        """
        获取服务日志
        
        Args:
            service_name: 服务名称
            lines: 日志行数
            
        Returns:
            str: 服务日志内容，如果获取失败返回None
        """
        try:
            result = subprocess.run(
                self._systemctl_cmd + ["journalctl", "-u", service_name, "-n", str(lines), "--no-pager"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return None