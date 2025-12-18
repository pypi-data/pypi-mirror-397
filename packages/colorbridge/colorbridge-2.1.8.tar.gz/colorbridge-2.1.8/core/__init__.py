# 核心模块包初始化文件 - ColorBridge v2.1.7

# 导入所有重命名的核心模块
from .colorbridge_serial_manager import ColorBridgeSerialManager
from .colorbridge_message_processor import ColorBridgeMessageProcessor
from .colorbridge_device_info_manager import ColorBridgeDeviceInfoManager
from .colorbridge_logger_manager import LoggerManager
from .colorbridge_monitoring_system import MonitoringSystem
from .colorbridge_error_recovery import ErrorRecoveryManager
from .colorbridge_log_analyzer import LogAnalyzer
from .colorbridge_log_protector import LogProtector
from .colorbridge_environment_manager import EnvironmentManager
from .colorbridge_debug_logger import get_debug_logger

__all__ = [
    'ColorBridgeSerialManager',
    'ColorBridgeMessageProcessor', 
    'ColorBridgeDeviceInfoManager',
    'LoggerManager',
    'MonitoringSystem',
    'ErrorRecoveryManager',
    'LogAnalyzer',
    'LogProtector',
    'EnvironmentManager',
    'get_debug_logger'
]

# 版本信息
__version__ = '2.1.7'
__author__ = 'ColorBridge开发团队'
__description__ = 'ColorBridge 核心模块包 v2.1.7 - 台球游戏彩蛋版本，包含2D模仿3D台球游戏、UI样式修复、母球重置修复等核心功能'