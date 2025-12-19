"""
配置管理器测试
"""

import pytest
import tempfile
import os
from pathlib import Path
from plsm.config_manager import ServiceConfigManager, ServiceConfig


class TestServiceConfigManager:
    """服务配置管理器测试类"""
    
    def setup_method(self):
        """测试方法前置设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ServiceConfigManager(systemd_dir=self.temp_dir)
    
    def teardown_method(self):
        """测试方法后置清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_list_services_empty(self):
        """测试空目录下列出服务"""
        services = self.manager.list_services()
        assert services == []
    
    def test_service_exists_false(self):
        """测试不存在的服务"""
        assert not self.manager.service_exists("nonexistent")
    
    def test_create_and_read_config(self):
        """测试创建和读取配置"""
        config = ServiceConfig(
            name="test-service",
            description="Test Service",
            exec_start="/usr/bin/python3 -m http.server",
            working_directory="/tmp"
        )
        
        # 创建配置
        result = self.manager.create_config(config)
        assert result is True
        
        # 检查服务存在
        assert self.manager.service_exists("test-service")
        
        # 读取配置
        read_config = self.manager.read_config("test-service")
        assert read_config is not None
        assert read_config.name == "test-service"
        assert read_config.description == "Test Service"
        assert read_config.exec_start == "/usr/bin/python3 -m http.server"
        assert read_config.working_directory == "/tmp"
    
    def test_create_config_overwrite(self):
        """测试配置覆盖"""
        config1 = ServiceConfig(
            name="test-service",
            description="First Description"
        )
        
        config2 = ServiceConfig(
            name="test-service", 
            description="Second Description"
        )
        
        # 第一次创建
        result1 = self.manager.create_config(config1)
        assert result1 is True
        
        # 第二次创建（不覆盖）
        result2 = self.manager.create_config(config2, overwrite=False)
        assert result2 is False
        
        # 第三次创建（覆盖）
        result3 = self.manager.create_config(config2, overwrite=True)
        assert result3 is True
        
        # 验证配置被覆盖
        read_config = self.manager.read_config("test-service")
        assert read_config.description == "Second Description"
    
    def test_remove_config(self):
        """测试删除配置"""
        config = ServiceConfig(name="test-service")
        
        # 创建配置
        self.manager.create_config(config)
        assert self.manager.service_exists("test-service")
        
        # 删除配置
        result = self.manager.remove_config("test-service")
        assert result is True
        assert not self.manager.service_exists("test-service")
        
        # 删除不存在的配置
        result = self.manager.remove_config("nonexistent")
        assert result is False
    
    def test_validate_config(self):
        """测试配置验证"""
        # 验证不存在的服务
        results = self.manager.validate_config("nonexistent")
        assert "existence" in results
        assert results["existence"] == "服务不存在"
        
        # 创建不完整的配置
        config = ServiceConfig(name="test-service")
        self.manager.create_config(config)
        
        # 验证配置
        results = self.manager.validate_config("test-service")
        assert "existence" in results
        assert results["existence"] == "服务存在"
        assert "exec_start" in results
        assert results["exec_start"] == "缺少ExecStart配置"
    
    def test_backup_config(self):
        """测试配置备份"""
        config = ServiceConfig(name="test-service")
        self.manager.create_config(config)
        
        # 创建备份目录
        backup_dir = os.path.join(self.temp_dir, "backup")
        
        # 备份配置
        result = self.manager.backup_config("test-service", backup_dir)
        assert result is True
        
        # 检查备份文件是否存在
        backup_file = Path(backup_dir) / "test-service.service.backup"
        assert backup_file.exists()
        
        # 备份不存在的服务
        result = self.manager.backup_config("nonexistent", backup_dir)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])