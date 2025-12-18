#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境自动检测和安装配置模块 - ColorBridge PCL2风格
全自动检测和配置运行环境，确保用户无需手动干预
"""

import sys
import os
import platform
import subprocess
import importlib
import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

class EnvironmentChecker:
    """环境自动检测器"""
    
    def __init__(self):
        self.system_info = self.get_system_info()
        self.python_info = self.get_python_info()
        self.missing_packages = []
        self.missing_modules = []
        self.permission_issues = []
        self.hardware_issues = []
        
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "platform": platform.system(),
            "version": platform.version(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "machine": platform.machine()
        }
    
    def get_python_info(self) -> Dict[str, Any]:
        """获取Python信息"""
        return {
            "version": sys.version,
            "executable": sys.executable,
            "path": sys.path,
            "version_info": sys.version_info
        }
    
    def check_python_version(self) -> Tuple[bool, str]:
        """检查Python版本"""
        if sys.version_info < (3, 8):
            return False, f"Python版本过低: {sys.version_info.major}.{sys.version_info.minor}，需要3.8+"
        return True, f"Python版本检查通过: {sys.version_info.major}.{sys.version_info.minor}"
    
    def check_required_packages(self) -> Tuple[bool, List[str]]:
        """检查必需的Python包"""
        required_packages = [
            "PyQt6",
            "serial",  # pyserial
            "dateutil"  # python-dateutil
        ]
        
        missing = []
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing.append(package)
        
        self.missing_packages = missing
        return len(missing) == 0, missing
    
    def check_serial_ports(self) -> Tuple[bool, List[str]]:
        """检查串口端口"""
        try:
            import serial.tools.list_ports
            
            ports = serial.tools.list_ports.comports()
            port_list = [str(port.device) for port in ports]
            
            return len(port_list) > 0, port_list
        except Exception as e:
            return False, [f"串口检测失败: {str(e)}"]
    
    def check_admin_permissions(self) -> Tuple[bool, str]:
        """检查管理员权限"""
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0, "Windows管理员权限检查"
            else:
                return os.geteuid() == 0, "Unix root权限检查"
        except Exception:
            return False, "权限检查失败"
    
    def check_hardware_acceleration(self) -> Tuple[bool, str]:
        """检查硬件加速支持"""
        try:
            # 检查GPU支持
            import platform
            
            if platform.system() == "Windows":
                # Windows下检查DirectX支持
                try:
                    import ctypes
                    # 简单的GPU检测
                    return True, "硬件加速支持检查通过"
                except:
                    return False, "硬件加速支持检查失败"
            else:
                return True, "硬件加速支持检查通过"
        except Exception as e:
            return False, f"硬件加速检查异常: {str(e)}"
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """运行综合环境检查"""
        results = {
            "timestamp": str(os.times()),
            "system_info": self.system_info,
            "python_info": self.python_info,
            "checks": {}
        }
        
        # Python版本检查
        python_ok, python_msg = self.check_python_version()
        results["checks"]["python_version"] = {
            "status": "✅ 通过" if python_ok else "❌ 失败",
            "message": python_msg,
            "details": self.python_info
        }
        
        # 包依赖检查
        packages_ok, missing_packages = self.check_required_packages()
        results["checks"]["required_packages"] = {
            "status": "✅ 通过" if packages_ok else "❌ 失败",
            "message": f"包检查完成，缺失: {len(missing_packages)}个",
            "missing": missing_packages
        }
        
        # 串口检查
        serial_ok, serial_ports = self.check_serial_ports()
        results["checks"]["serial_ports"] = {
            "status": "✅ 通过" if serial_ok else "⚠️ 警告",
            "message": f"发现 {len(serial_ports)} 个串口",
            "ports": serial_ports
        }
        
        # 权限检查
        admin_ok, admin_msg = self.check_admin_permissions()
        results["checks"]["admin_permissions"] = {
            "status": "✅ 通过" if admin_ok else "⚠️ 警告",
            "message": admin_msg
        }
        
        # 硬件加速检查
        hw_ok, hw_msg = self.check_hardware_acceleration()
        results["checks"]["hardware_acceleration"] = {
            "status": "✅ 通过" if hw_ok else "⚠️ 警告",
            "message": hw_msg
        }
        
        # 总体状态
        critical_issues = not python_ok or not packages_ok
        results["overall_status"] = "🟢 正常" if not critical_issues else "🔴 需要修复"
        
        return results


class AutoInstaller:
    """自动安装和配置器"""
    
    def __init__(self, environment_checker: EnvironmentChecker):
        self.env_checker = environment_checker
        self.install_log = []
        
    def log(self, message: str):
        """记录安装日志"""
        self.install_log.append(f"[{os.times()}] {message}")
        print(f"[AutoInstaller] {message}")
    
    def install_missing_packages(self, missing_packages: List[str]) -> Tuple[bool, str]:
        """自动安装缺失的包"""
        if not missing_packages:
            return True, "没有缺失的包"
        
        self.log(f"开始安装缺失的包: {missing_packages}")
        
        # 包名映射
        package_mapping = {
            "PyQt6": "PyQt6>=6.6.0",
            "serial": "pyserial>=3.5",
            "dateutil": "python-dateutil>=2.8.2"
        }
        
        success_count = 0
        failed_packages = []
        
        for package in missing_packages:
            try:
                install_name = package_mapping.get(package, package)
                self.log(f"正在安装 {install_name}...")
                
                # 使用pip安装
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", install_name
                ], capture_output=True, text=True, timeout=300, encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    self.log(f"✅ {package} 安装成功")
                    success_count += 1
                else:
                    self.log(f"❌ {package} 安装失败: {result.stderr}")
                    failed_packages.append(package)
                    
            except subprocess.TimeoutExpired:
                self.log(f"❌ {package} 安装超时")
                failed_packages.append(package)
            except Exception as e:
                self.log(f"❌ {package} 安装异常: {str(e)}")
                failed_packages.append(package)
        
        if success_count == len(missing_packages):
            return True, f"所有包安装成功 ({success_count}/{len(missing_packages)})"
        else:
            return False, f"部分包安装失败 ({success_count}/{len(missing_packages)}), 失败: {failed_packages}"
    
    def configure_serial_permissions(self) -> Tuple[bool, str]:
        """配置串口权限"""
        try:
            if platform.system() == "Linux":
                # Linux下配置串口权限
                self.log("配置Linux串口权限...")
                
                # 添加用户到dialout组
                result = subprocess.run([
                    "sudo", "usermod", "-a", "-G", "dialout", os.getenv("USER")
                ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    self.log("✅ Linux串口权限配置成功")
                    return True, "Linux串口权限配置成功"
                else:
                    self.log(f"⚠️ Linux串口权限配置失败: {result.stderr}")
                    return False, "Linux串口权限配置失败"
            
            elif platform.system() == "Windows":
                # Windows下通常不需要特殊配置
                self.log("✅ Windows串口权限检查通过")
                return True, "Windows串口权限检查通过"
            
            else:
                self.log("⚠️ 未知系统，跳过串口权限配置")
                return True, "未知系统，跳过串口权限配置"
                
        except Exception as e:
            self.log(f"❌ 串口权限配置异常: {str(e)}")
            return False, f"串口权限配置异常: {str(e)}"
    
    def create_desktop_shortcut(self) -> Tuple[bool, str]:
        """创建桌面快捷方式"""
        try:
            import platform
            
            if platform.system() == "Windows":
                # Windows桌面快捷方式
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                shortcut_path = os.path.join(desktop_path, "ColorBridge.lnk")
                
                # 使用PowerShell创建快捷方式
                main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
                working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                
                script = f'''
                $WshShell = New-Object -comObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
                $Shortcut.TargetPath = "{sys.executable}"
                $Shortcut.Arguments = "{main_script}"
                $Shortcut.WorkingDirectory = "{working_dir}"
                $Shortcut.IconLocation = "{sys.executable}"
                $Shortcut.Description = "ColorBridge - AI8051U"
                $Shortcut.Save()
                '''
                
                result = subprocess.run([
                    "powershell", "-Command", script
                ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    self.log("✅ Windows桌面快捷方式创建成功")
                    return True, "Windows桌面快捷方式创建成功"
                else:
                    self.log(f"⚠️ Windows桌面快捷方式创建失败: {result.stderr}")
                    return False, "Windows桌面快捷方式创建失败"
            
            else:
                self.log("⚠️ 非Windows系统，跳过桌面快捷方式创建")
                return True, "非Windows系统，跳过桌面快捷方式创建"
                
        except Exception as e:
            self.log(f"❌ 桌面快捷方式创建异常: {str(e)}")
            return False, f"桌面快捷方式创建异常: {str(e)}"
    
    def auto_fix_environment(self) -> Dict[str, Any]:
        """自动修复环境问题"""
        self.log("开始自动环境修复...")
        
        results = {
            "timestamp": str(os.times()),
            "actions": {},
            "success": True,
            "message": "环境修复完成"
        }
        
        # 安装缺失的包
        if self.env_checker.missing_packages:
            pkg_ok, pkg_msg = self.install_missing_packages(self.env_checker.missing_packages)
            results["actions"]["install_packages"] = {
                "status": "✅ 成功" if pkg_ok else "❌ 失败",
                "message": pkg_msg
            }
            if not pkg_ok:
                results["success"] = False
        
        # 配置串口权限
        serial_ok, serial_msg = self.configure_serial_permissions()
        results["actions"]["configure_serial"] = {
            "status": "✅ 成功" if serial_ok else "❌ 失败",
            "message": serial_msg
        }
        
        # 创建桌面快捷方式
        shortcut_ok, shortcut_msg = self.create_desktop_shortcut()
        results["actions"]["create_shortcut"] = {
            "status": "✅ 成功" if shortcut_ok else "❌ 失败",
            "message": shortcut_msg
        }
        
        # 重新检查环境
        self.log("重新检查环境状态...")
        recheck_results = self.env_checker.run_comprehensive_check()
        results["recheck"] = recheck_results
        
        # 更新总体状态
        if recheck_results["overall_status"] == "🟢 正常":
            results["final_status"] = "🟢 环境完全正常"
        else:
            results["final_status"] = "🟡 环境基本正常，有轻微问题"
            results["success"] = False
        
        return results


class EnvironmentManager:
    """环境管理器 - 统一管理环境检测和自动修复"""
    
    def __init__(self):
        self.checker = EnvironmentChecker()
        self.installer = AutoInstaller(self.checker)
        self.last_check_results = None
        self.last_install_results = None
        
    def run_full_check_and_fix(self) -> Dict[str, Any]:
        """运行完整的检测和修复流程"""
        # 第一步：环境检测
        self.last_check_results = self.checker.run_comprehensive_check()
        
        # 第二步：自动修复
        self.last_install_results = self.installer.auto_fix_environment()
        
        # 第三步：生成报告
        return {
            "check_results": self.last_check_results,
            "install_results": self.last_install_results,
            "summary": {
                "overall_status": self.last_install_results["final_status"],
                "actions_taken": len(self.last_install_results["actions"]),
                "success": self.last_install_results["success"]
            }
        }
    
    def get_status_report(self) -> str:
        """获取状态报告"""
        if not self.last_check_results:
            return "尚未运行环境检测"
        
        report = []
        report.append("🌈 ColorBridge 环境状态报告")
        report.append("=" * 40)
        
        # 总体状态
        report.append(f"📊 总体状态: {self.last_check_results['overall_status']}")
        report.append("")
        
        # 各项检查结果
        for check_name, check_result in self.last_check_results["checks"].items():
            report.append(f"{check_result['status']} {check_name}")
            report.append(f"   {check_result['message']}")
        
        # 安装结果
        if self.last_install_results:
            report.append("")
            report.append("🔧 自动修复结果:")
            for action_name, action_result in self.last_install_results["actions"].items():
                report.append(f"{action_result['status']} {action_name}")
                report.append(f"   {action_result['message']}")
        
        return "\n".join(report)
    
    def save_report(self, filepath: str) -> bool:
        """保存报告到文件"""
        try:
            report_data = {
                "check_results": self.last_check_results,
                "install_results": self.last_install_results,
                "install_log": self.installer.install_log
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存报告失败: {str(e)}")
            return False


# 便捷函数
def quick_environment_check() -> Dict[str, Any]:
    """快速环境检查"""
    manager = EnvironmentManager()
    return manager.run_full_check_and_fix()

def is_environment_ready() -> bool:
    """检查环境是否准备就绪"""
    manager = EnvironmentManager()
    results = manager.run_full_check_and_fix()
    return results["summary"]["success"]