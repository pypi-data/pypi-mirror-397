"""
ColorBridge - 半透明多巴胺配色串口助手
专为 AI8051U USB-CDC 项目设计
作者: 076lik
许可证: GPLV3
版本: 2.1.10 PCL2风格
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 确保当前目录也在路径中
sys.path.insert(0, os.path.abspath('.'))

def main():
    """主函数 - 启动增强稳定版本的ColorBridge"""
    # 解析命令行参数
    debug_mode = "--debug" in sys.argv or "-d" in sys.argv
    quiet_mode = "--quiet" in sys.argv or "-q" in sys.argv
    version_mode = "--version" in sys.argv or "-v" in sys.argv
    help_mode = "--help" in sys.argv or "-h" in sys.argv
    
    # 显示版本信息
    if version_mode:
        print("ColorBridge v2.1.10 - AI8051U串口助手")
        print("作者: 076lik")
        print("许可证: GPLV3")
        return 0
    
    # 显示帮助信息
    if help_mode:
        print("ColorBridge - AI8051U串口助手")
        print("")
        print("用法: python main.py [选项]")
        print("")
        print("选项:")
        print("  -d, --debug    启用调试模式，显示详细调试信息")
        print("  -q, --quiet    静默模式，只显示错误信息")
        print("  -v, --version  显示版本信息")
        print("  -h, --help     显示此帮助信息")
        print("")
        print("示例:")
        print("  python main.py           # 正常启动")
        print("  python main.py --debug   # 调试模式启动")
        print("  python main.py --quiet   # 静默模式启动")
        return 0
    
    # 创建 QApplication 实例
    app = QApplication(sys.argv)
    app.setApplicationName("ColorBridge")
    app.setApplicationVersion("2.1.10")
    app.setOrganizationName("076lik")
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 显示启动模式
    if debug_mode:
        print("🐛 ColorBridge 调试模式启动")
    elif quiet_mode:
        print("🤫 ColorBridge 静默模式启动")
    else:
        print("🌈 ColorBridge 正常模式启动")
    
    # 确保logs目录存在
    import os
    from pathlib import Path
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化日志管理器、保护器和监控系统
    logger_manager = None
    log_protector = None
    monitoring_system = None
    log_analyzer = None
    
    try:
        # 初始化日志管理器（先初始化，这样保护器就知道当前日志文件）
        try:
            from core.colorbridge_logger_manager import init_logger_manager
            logger_manager = init_logger_manager(debug_mode=debug_mode)  # 使用用户指定的调试模式
            logger_manager.log_system_event("SYSTEM", "ColorBridge 启动中...")
        except ImportError as e:
            print(f"❌ 无法导入日志管理器: {e}")
            return 1
        
        # 初始化日志保护器（在日志管理器之后初始化，避免保护当前文件）
        try:
            from core.colorbridge_log_protector import init_log_protector
            log_protector = init_log_protector()
            if logger_manager:
                logger_manager.log_system_event("SYSTEM", "日志保护已启用")
        except ImportError as e:
            print(f"⚠️ 无法导入日志保护器: {e}")
        
        # 初始化监控系统
        try:
            from core.colorbridge_monitoring_system import MonitoringSystem
            from core.colorbridge_log_analyzer import LogAnalyzer
            
            # 创建监控系统
            monitoring_system = MonitoringSystem(debug_mode=debug_mode)
            monitoring_system.start_monitoring()
            
            # 创建日志分析器
            log_analyzer = LogAnalyzer(debug_mode=debug_mode)
            log_analyzer.start_realtime_analysis()
            
            if logger_manager:
                logger_manager.log_system_event("SYSTEM", "监控系统和日志分析器已启动")
            print("✅ 监控系统和日志分析器已启动")
            
        except ImportError as e:
            print(f"⚠️ 无法导入监控系统: {e}")
        except Exception as e:
            print(f"⚠️ 监控系统启动失败: {e}")
        
    except Exception as e:
        print(f"⚠️ 系统初始化失败: {e}")
    
    # 快速环境检测（可选）
    try:
        from core.colorbridge_environment_manager import EnvironmentManager
        manager = EnvironmentManager()
        results = manager.run_full_check_and_fix()
        
        if results["summary"]["success"]:
            print("✅ 环境检测通过，启动主窗口...")
        else:
            print("⚠️ 环境检测有问题，但继续启动...")
    except Exception as e:
        print(f"⚠️ 环境检测跳过: {e}")
    
    # 检查Python环境
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ 需要Python 3.8或更高版本")
            return 1
        print(f"✅ Python环境检查通过: {python_version.major}.{python_version.minor}.{python_version.micro}")
    except Exception as e:
        print(f"⚠️ Python环境检查失败: {e}")
    
    # 启动增强稳定版本的主窗口
    try:
        from ui.colorbridge_main_window import ColorBridgeMainWindow
        
        # 传入监控系统和调试模式
        window = ColorBridgeMainWindow(
            monitoring_system=monitoring_system,
            log_analyzer=log_analyzer,
            debug_mode=debug_mode
        )
        window.show()
        
        # 集成监控信号
        if monitoring_system:
            _setup_monitoring_integration(window, monitoring_system)
        
        if log_analyzer:
            _setup_log_analyzer_integration(window, log_analyzer)
        
        # 显示欢迎通知
        startup_msg = "🌈 ColorBridge 增强稳定版本启动成功！"
        if monitoring_system:
            startup_msg += "\n📊 实时监控系统已启用"
        if log_analyzer:
            startup_msg += "\n🔍 智能日志分析已启用"
            
        window.notification_manager.show_success(startup_msg)
        
        # 运行事件循环
        exit_code = app.exec()
        
        # 清理Qt线程和资源
        _cleanup_qt_resources(app)
        _cleanup_resources(logger_manager, log_protector, monitoring_system, log_analyzer)
        
        return exit_code
        
    except ImportError as e:
        print(f"❌ 无法导入主窗口: {e}")
        return 1
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1

def _setup_monitoring_integration(window, monitoring_system):
    """设置监控系统集成"""
    try:
        # 连接预警信号
        monitoring_system.alert_triggered.connect(
            lambda alert: window.notification_manager.show_warning(
                f"🚨 系统预警: {alert.title}\n{alert.message}"
            )
        )
        
        # 连接性能报告信号
        monitoring_system.performance_report_generated.connect(
            lambda report: _handle_performance_report(window, report)
        )
        
        # 添加系统健康监控
        monitoring_system.system_health_updated.connect(
            lambda health: _handle_system_health_update(window, health)
        )
        
        print("✅ 监控系统集成完成")
        
    except Exception as e:
        print(f"⚠️ 监控系统集成失败: {e}")

def _setup_log_analyzer_integration(window, log_analyzer):
    """设置日志分析器集成"""
    try:
        # 连接错误检测信号
        log_analyzer.error_detected.connect(
            lambda error: _handle_log_error(window, error)
        )
        
        # 连接分析完成信号
        log_analyzer.analysis_completed.connect(
            lambda analysis: _handle_log_analysis(window, analysis)
        )
        
        # 连接建议生成信号
        log_analyzer.recommendation_generated.connect(
            lambda recommendations: _handle_recommendations(window, recommendations)
        )
        
        print("✅ 日志分析器集成完成")
        
    except Exception as e:
        print(f"⚠️ 日志分析器集成失败: {e}")

def _handle_performance_report(window, report):
    """处理性能报告"""
    try:
        # 只在性能有问题时显示通知
        if report.get('active_alerts', 0) > 0:
            window.notification_manager.show_warning(
                f"📊 性能报告: {report['active_alerts']} 个活跃预警"
            )
    except Exception as e:
        print(f"⚠️ 性能报告处理失败: {e}")

def _handle_system_health_update(window, health):
    """处理系统健康更新"""
    try:
        if health.overall_status == "critical":
            window.notification_manager.show_error(
                f"🏥 系统健康状态严重: CPU {health.cpu_usage:.1f}%, 内存 {health.memory_usage:.1f}%"
            )
        elif health.overall_status == "warning":
            window.notification_manager.show_warning(
                f"🏥 系统健康状态警告: CPU {health.cpu_usage:.1f}%, 内存 {health.memory_usage:.1f}%"
            )
    except Exception as e:
        print(f"⚠️ 系统健康更新处理失败: {e}")

def _handle_log_error(window, error):
    """处理日志错误"""
    try:
        if error.severity.value in ["high", "critical"]:
            window.notification_manager.show_error(
                f"🔍 检测到严重错误: {error.category.value}\n{error.message[:100]}..."
            )
    except Exception as e:
        print(f"⚠️ 日志错误处理失败: {e}")

def _handle_log_analysis(window, analysis):
    """处理日志分析结果"""
    try:
        if analysis.total_errors > 10:
            window.notification_manager.show_warning(
                f"🔍 日志分析: 检测到 {analysis.total_errors} 个错误"
            )
    except Exception as e:
        print(f"⚠️ 日志分析处理失败: {e}")

def _handle_recommendations(window, recommendations):
    """处理修复建议"""
    try:
        if recommendations:
            # 显示前3个最重要的建议
            top_recommendations = recommendations[:3]
            rec_text = "\n".join(f"• {rec}" for rec in top_recommendations)
            window.notification_manager.show_info(
                f"💡 系统建议:\n{rec_text}"
            )
    except Exception as e:
        print(f"⚠️ 建议处理失败: {e}")

def _cleanup_qt_resources(app):
    """清理Qt资源，防止程序关闭卡死"""
    try:
        # 快速处理剩余事件，不长时间等待
        for _ in range(1):  # 只处理一次，避免卡死
            try:
                app.processEvents()
            except:
                break  # 如果处理事件失败，立即退出
        
        # 不等待线程清理，直接强制垃圾回收
        # 这样可以避免程序关闭时因等待线程而卡死
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        print("✅ Qt资源快速清理完成")
    except Exception as e:
        print(f"⚠️ Qt资源清理失败: {e}")

def _cleanup_resources(logger_manager, log_protector, monitoring_system, log_analyzer):
    """清理资源"""
    try:
        # 按顺序清理资源，避免依赖问题
        
        # 1. 首先停止监控系统
        if monitoring_system:
            try:
                monitoring_system.stop_monitoring()
                print("✅ 监控系统已停止")
            except Exception as e:
                print(f"⚠️ 监控系统停止失败: {e}")
        
        # 2. 停止日志分析器
        if log_analyzer:
            try:
                log_analyzer.stop_realtime_analysis()
                print("✅ 日志分析器已停止")
            except Exception as e:
                print(f"⚠️ 日志分析器停止失败: {e}")
        
        # 3. 记录关闭事件
        if logger_manager:
            try:
                logger_manager.log_system_event("SYSTEM", "ColorBridge 正在关闭...")
                logger_manager.close()
                print("✅ 日志管理器已关闭")
            except Exception as e:
                print(f"⚠️ 日志管理器关闭失败: {e}")
        
        # 4. 日志保护器保持激活状态
        if log_protector:
            try:
                # 日志保护器会在程序退出时自动保持保护状态
                print("✅ 日志保护保持激活")
            except Exception as e:
                print(f"⚠️ 日志保护器状态检查失败: {e}")
        
        # 5. 强制垃圾回收
        try:
            import gc
            gc.collect()
            print("✅ 垃圾回收完成")
        except Exception as e:
            print(f"⚠️ 垃圾回收失败: {e}")
            
    except Exception as e:
        print(f"⚠️ 资源清理失败: {e}")

if __name__ == "__main__":
    main()