"""
Python Linux Service Manager (plsm)
专注于Linux系统服务管理的Python库

项目信息：
- 仓库地址: https://gitee.com/liumou_site/plsm
- 最新版本: v1.0.0
- 支持Python: 3.7+
- 许可证: MIT

主要功能：
- 服务配置管理
- 服务状态管理
- 服务启动/停止/重启
- 服务状态监控

特性：
- 模块化设计，配置管理和状态管理分离
- 自动检测系统服务状态和配置信息
- 完整的服务操作API
- 完善的错误处理和异常管理
"""

from .config_manager import ServiceConfig, ServiceConfigManager
from .status_manager import ServiceStatus, ServiceInfo, ServiceStatusManager
from .service_manager import ServiceManager

__version__ = "1.0.0"
__author__ = "坐公交也用券"
__email__ = "liumou.site@qq.com"
__url__ = "https://gitee.com/liumou_site/plsm"
__license__ = "MIT"

__all__ = [
    "ServiceConfig",
    "ServiceConfigManager",
    "ServiceStatus", 
    "ServiceInfo",
    "ServiceStatusManager", 
    "ServiceManager",
]