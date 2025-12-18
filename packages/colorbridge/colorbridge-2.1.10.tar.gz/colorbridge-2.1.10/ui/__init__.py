# UI模块初始化 - ColorBridge v2.1.10

# 核心UI组件
from .colorbridge_main_window import ColorBridgeMainWindow
from .colorbridge_settings_dialog import SettingsDialog

# UI组件
from .colorbridge_theme_manager import ThemeManager
from .colorbridge_notification_manager import EnhancedNotificationManager

__all__ = [
    # 核心组件
    'ColorBridgeMainWindow',
    'SettingsDialog',
    
    # UI组件
    'ThemeManager',
    'EnhancedNotificationManager'
]

# 版本信息
__version__ = '2.1.10'
__author__ = 'ColorBridge开发团队'
__description__ = 'ColorBridge UI模块 v2.1.10 - PyPI发布修复版本，解决文件名重用问题，包含Bug修复、着色优化和终端消息打印机打印功能，包含2D模仿3D台球游戏UI、修复的串口设备样式、增强的游戏界面等'