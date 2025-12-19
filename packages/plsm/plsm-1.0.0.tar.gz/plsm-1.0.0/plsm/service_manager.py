"""
主服务管理类
整合配置管理和状态管理，提供完整的服务管理功能
"""

import subprocess
import time
from typing import Dict, List, Optional, Tuple
from .config_manager import ServiceConfigManager, ServiceConfig
from .status_manager import ServiceStatusManager, ServiceStatus, ServiceInfo


class ServiceManager:
    """主服务管理器"""
    
    def __init__(self, sudo: bool = False, systemd_dir: str = "/etc/systemd/system"):
        """
        初始化服务管理器
        
        Args:
            sudo: 是否使用sudo执行特权操作
            systemd_dir: systemd服务文件目录
        """
        self.sudo = sudo
        self.config_manager = ServiceConfigManager(systemd_dir)
        self.status_manager = ServiceStatusManager(sudo)
        
        # 特权命令前缀
        self._sudo_cmd = ["sudo"] if sudo else []
    
    def start_service(self, service_name: str, timeout: int = 30) -> bool:
        """
        启动服务
        
        Args:
            service_name: 服务名称
            timeout: 启动超时时间（秒）
            
        Returns:
            bool: 是否启动成功
        """
        if not self.config_manager.service_exists(service_name):
            return False
        
        try:
            result = subprocess.run(
                self._sudo_cmd + ["systemctl", "start", service_name],
                capture_output=True, text=True, timeout=timeout
            )
            
            if result.returncode == 0:
                # 等待服务进入运行状态
                return self._wait_for_status(service_name, ServiceStatus.ACTIVE, timeout)
            else:
                return False
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def stop_service(self, service_name: str, timeout: int = 30) -> bool:
        """
        停止服务
        
        Args:
            service_name: 服务名称
            timeout: 停止超时时间（秒）
            
        Returns:
            bool: 是否停止成功
        """
        if not self.config_manager.service_exists(service_name):
            return False
        
        try:
            result = subprocess.run(
                self._sudo_cmd + ["systemctl", "stop", service_name],
                capture_output=True, text=True, timeout=timeout
            )
            
            if result.returncode == 0:
                # 等待服务进入停止状态
                return self._wait_for_status(service_name, ServiceStatus.INACTIVE, timeout)
            else:
                return False
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def restart_service(self, service_name: str, timeout: int = 60) -> bool:
        """
        重启服务
        
        Args:
            service_name: 服务名称
            timeout: 重启超时时间（秒）
            
        Returns:
            bool: 是否重启成功
        """
        if not self.config_manager.service_exists(service_name):
            return False
        
        try:
            result = subprocess.run(
                self._sudo_cmd + ["systemctl", "restart", service_name],
                capture_output=True, text=True, timeout=timeout
            )
            
            if result.returncode == 0:
                # 等待服务重新进入运行状态
                return self._wait_for_status(service_name, ServiceStatus.ACTIVE, timeout)
            else:
                return False
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def reload_service(self, service_name: str, timeout: int = 30) -> bool:
        """
        重载服务配置
        
        Args:
            service_name: 服务名称
            timeout: 重载超时时间（秒）
            
        Returns:
            bool: 是否重载成功
        """
        if not self.config_manager.service_exists(service_name):
            return False
        
        try:
            # 先重载systemd配置
            subprocess.run(
                self._sudo_cmd + ["systemctl", "daemon-reload"],
                capture_output=True, timeout=10
            )
            
            # 重载服务
            result = subprocess.run(
                self._sudo_cmd + ["systemctl", "reload", service_name],
                capture_output=True, text=True, timeout=timeout
            )
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def enable_service(self, service_name: str) -> bool:
        """
        启用服务（开机自启）
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 是否启用成功
        """
        if not self.config_manager.service_exists(service_name):
            return False
        
        try:
            result = subprocess.run(
                self._sudo_cmd + ["systemctl", "enable", service_name],
                capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def disable_service(self, service_name: str) -> bool:
        """
        禁用服务（取消开机自启）
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 是否禁用成功
        """
        if not self.config_manager.service_exists(service_name):
            return False
        
        try:
            result = subprocess.run(
                self._sudo_cmd + ["systemctl", "disable", service_name],
                capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def _wait_for_status(self, service_name: str, target_status: ServiceStatus, timeout: int) -> bool:
        """
        等待服务进入指定状态
        
        Args:
            service_name: 服务名称
            target_status: 目标状态
            timeout: 超时时间（秒）
            
        Returns:
            bool: 是否在超时前进入目标状态
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            info = self.status_manager.get_status(service_name)
            if info and info.status == target_status:
                return True
            time.sleep(1)
        
        return False
    
    def create_service(self, config: ServiceConfig, start_after_create: bool = False) -> bool:
        """
        创建并配置服务
        
        Args:
            config: 服务配置
            start_after_create: 创建后是否启动服务
            
        Returns:
            bool: 是否创建成功
        """
        # 创建配置文件
        if not self.config_manager.create_config(config, overwrite=True):
            return False
        
        # 重载systemd配置
        try:
            subprocess.run(
                self._sudo_cmd + ["systemctl", "daemon-reload"],
                capture_output=True, timeout=10
            )
        except subprocess.TimeoutExpired:
            pass
        
        # 可选：启动服务
        if start_after_create:
            return self.start_service(config.name)
        
        return True
    
    def remove_service(self, service_name: str, stop_before_remove: bool = True) -> bool:
        """
        移除服务
        
        Args:
            service_name: 服务名称
            stop_before_remove: 移除前是否停止服务
            
        Returns:
            bool: 是否移除成功
        """
        # 可选：先停止服务
        if stop_before_remove:
            self.stop_service(service_name)
        
        # 禁用服务
        self.disable_service(service_name)
        
        # 删除配置文件
        return self.config_manager.remove_config(service_name)
    
    def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """
        获取服务的完整信息
        
        Args:
            service_name: 服务名称
            
        Returns:
            ServiceInfo: 服务信息对象，如果服务不存在返回None
        """
        return self.status_manager.get_status(service_name)
    
    def validate_service(self, service_name: str) -> Dict[str, str]:
        """
        验证服务的完整状态
        
        Args:
            service_name: 服务名称
            
        Returns:
            Dict[str, str]: 验证结果
        """
        results = {}
        
        # 配置验证
        config_results = self.config_manager.validate_config(service_name)
        results.update(config_results)
        
        # 状态验证
        info = self.status_manager.get_status(service_name)
        if info:
            results["status"] = f"服务状态: {info.status.value}"
            results["running"] = "服务正在运行" if info.running else "服务未运行"
            results["enabled"] = "服务已启用" if self.status_manager.is_enabled(service_name) else "服务未启用"
        else:
            results["status"] = "无法获取服务状态"
        
        return results
    
    def list_all_services(self) -> List[ServiceInfo]:
        """
        列出所有服务
        
        Returns:
            List[ServiceInfo]: 所有服务的信息列表
        """
        return self.status_manager.list_services()
    
    def get_failed_services(self) -> List[ServiceInfo]:
        """
        获取失败的服务列表
        
        Returns:
            List[ServiceInfo]: 失败的服务信息列表
        """
        return self.status_manager.get_failed_services()
    
    def get_running_services(self) -> List[ServiceInfo]:
        """
        获取正在运行的服务列表
        
        Returns:
            List[ServiceInfo]: 运行中的服务信息列表
        """
        return self.status_manager.get_running_services()
    
    def monitor_service_health(self, service_name: str, duration: int = 300) -> List[Tuple[float, ServiceInfo]]:
        """
        监控服务健康状态
        
        Args:
            service_name: 服务名称
            duration: 监控时长（秒）
            
        Returns:
            List[Tuple[float, ServiceInfo]]: 监控历史记录
        """
        return self.status_manager.monitor_service(service_name, duration)
    
    def get_service_logs(self, service_name: str, lines: int = 50) -> Optional[str]:
        """
        获取服务日志
        
        Args:
            service_name: 服务名称
            lines: 日志行数
            
        Returns:
            str: 服务日志内容，如果获取失败返回None
        """
        return self.status_manager.get_service_logs(service_name, lines)
    
    def backup_service(self, service_name: str, backup_dir: str) -> bool:
        """
        备份服务配置
        
        Args:
            service_name: 服务名称
            backup_dir: 备份目录
            
        Returns:
            bool: 是否备份成功
        """
        return self.config_manager.backup_config(service_name, backup_dir)
    
    def is_service_healthy(self, service_name: str) -> bool:
        """
        检查服务是否健康
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否健康（运行中且无错误）
        """
        info = self.status_manager.get_status(service_name)
        if not info:
            return False
        
        return info.running and info.status != ServiceStatus.FAILED