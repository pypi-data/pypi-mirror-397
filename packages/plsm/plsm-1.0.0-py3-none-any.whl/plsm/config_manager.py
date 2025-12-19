"""
服务配置管理模块
负责服务的配置文件读取、解析和管理
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    """服务配置数据类"""
    name: str
    description: str = ""
    exec_start: str = ""
    exec_stop: str = ""
    exec_reload: str = ""
    working_directory: str = ""
    user: str = ""
    group: str = ""
    environment: Dict[str, str] = None
    restart: str = "no"
    wanted_by: str = "multi-user.target"
    
    def __post_init__(self):
        if self.environment is None:
            self.environment = {}


class ServiceConfigManager:
    """服务配置管理器"""
    
    def __init__(self, systemd_dir: str = "/etc/systemd/system"):
        """
        初始化配置管理器
        
        Args:
            systemd_dir: systemd服务文件目录
        """
        self.systemd_dir = Path(systemd_dir)
        self.service_extensions = {'.service'}
    
    def list_services(self) -> List[str]:
        """
        列出所有可用的服务
        
        Returns:
            服务名称列表
        """
        if not self.systemd_dir.exists():
            return []
        
        services = []
        for file_path in self.systemd_dir.iterdir():
            if file_path.is_file() and file_path.suffix in self.service_extensions:
                services.append(file_path.stem)
        
        return sorted(services)
    
    def service_exists(self, service_name: str) -> bool:
        """
        检查服务是否存在
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否存在
        """
        service_file = self.systemd_dir / f"{service_name}.service"
        return service_file.exists()
    
    def read_config(self, service_name: str) -> Optional[ServiceConfig]:
        """
        读取服务配置
        
        Args:
            service_name: 服务名称
            
        Returns:
            ServiceConfig: 服务配置对象，如果服务不存在返回None
        """
        if not self.service_exists(service_name):
            return None
        
        service_file = self.systemd_dir / f"{service_name}.service"
        config = ServiceConfig(name=service_name)
        
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析配置文件
        self._parse_service_file(content, config)
        return config
    
    def _parse_service_file(self, content: str, config: ServiceConfig):
        """解析service文件内容"""
        lines = content.split('\n')
        section = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 检查节头
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1].strip()
                continue
            
            # 解析键值对
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Unit节中的字段
                if section == 'Unit':
                    if key == 'Description':
                        config.description = value
                
                # Service节中的字段
                elif section == 'Service':
                    if key == 'ExecStart':
                        config.exec_start = value
                    elif key == 'ExecStop':
                        config.exec_stop = value
                    elif key == 'ExecReload':
                        config.exec_reload = value
                    elif key == 'WorkingDirectory':
                        config.working_directory = value
                    elif key == 'User':
                        config.user = value
                    elif key == 'Group':
                        config.group = value
                    elif key == 'Restart':
                        config.restart = value
                    elif key.startswith('Environment='):
                        # 处理环境变量
                        env_str = key.replace('Environment=', '')
                        if '=' in env_str:
                            env_key, env_value = env_str.split('=', 1)
                            config.environment[env_key] = env_value
    
    def create_config(self, config: ServiceConfig, overwrite: bool = False) -> bool:
        """
        创建服务配置
        
        Args:
            config: 服务配置对象
            overwrite: 是否覆盖已存在的配置
            
        Returns:
            bool: 是否创建成功
        """
        if self.service_exists(config.name) and not overwrite:
            return False
        
        service_file = self.systemd_dir / f"{config.name}.service"
        
        # 生成配置文件内容
        content = self._generate_service_file(config)
        
        try:
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except (IOError, PermissionError):
            return False
    
    def _generate_service_file(self, config: ServiceConfig) -> str:
        """生成service文件内容"""
        lines = ["[Unit]"]
        if config.description:
            lines.append(f"Description={config.description}")
        
        lines.append("")
        lines.append("[Service]")
        
        if config.exec_start:
            lines.append(f"ExecStart={config.exec_start}")
        if config.exec_stop:
            lines.append(f"ExecStop={config.exec_stop}")
        if config.exec_reload:
            lines.append(f"ExecReload={config.exec_reload}")
        if config.working_directory:
            lines.append(f"WorkingDirectory={config.working_directory}")
        if config.user:
            lines.append(f"User={config.user}")
        if config.group:
            lines.append(f"Group={config.group}")
        if config.restart:
            lines.append(f"Restart={config.restart}")
        
        # 环境变量
        for key, value in config.environment.items():
            lines.append(f"Environment={key}={value}")
        
        lines.append("")
        lines.append("[Install]")
        lines.append(f"WantedBy={config.wanted_by}")
        
        return '\n'.join(lines)
    
    def remove_config(self, service_name: str) -> bool:
        """
        删除服务配置
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 是否删除成功
        """
        if not self.service_exists(service_name):
            return False
        
        service_file = self.systemd_dir / f"{service_name}.service"
        
        try:
            service_file.unlink()
            return True
        except (IOError, PermissionError):
            return False
    
    def backup_config(self, service_name: str, backup_dir: str) -> bool:
        """
        备份服务配置
        
        Args:
            service_name: 服务名称
            backup_dir: 备份目录
            
        Returns:
            bool: 是否备份成功
        """
        if not self.service_exists(service_name):
            return False
        
        service_file = self.systemd_dir / f"{service_name}.service"
        backup_path = Path(backup_dir) / f"{service_name}.service.backup"
        
        try:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(service_file, backup_path)
            return True
        except (IOError, PermissionError):
            return False
    
    def validate_config(self, service_name: str) -> Dict[str, str]:
        """
        验证服务配置
        
        Args:
            service_name: 服务名称
            
        Returns:
            Dict[str, str]: 验证结果，key为检查项，value为结果描述
        """
        config = self.read_config(service_name)
        if not config:
            return {"existence": "服务不存在"}
        
        results = {
            "existence": "服务存在",
            "exec_start": "ExecStart配置正常" if config.exec_start else "缺少ExecStart配置",
            "working_directory": "工作目录配置正常" if config.working_directory else "缺少工作目录配置",
            "user": "用户配置正常" if config.user else "缺少用户配置",
        }
        
        return results