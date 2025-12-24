# -*- coding: utf-8 -*-
"""
APT交互模块：负责执行apt update操作和获取软件包信息
"""

import subprocess
import logging
import re

logger = logging.getLogger(__name__)

class AptManager:
    """APT管理器，负责与APT交互"""
    
    def update_apt(self, dry_run=False):
        """
        执行apt update操作
        
        Args:
            dry_run: 是否模拟运行，不实际执行更新
            
        Returns:
            bool: 更新是否成功
        """
        if dry_run:
            logger.info("模拟运行模式，跳过apt update")
            return True
            
        try:
            logger.info("执行apt update...")
            result = subprocess.run(
                ["apt", "update"], 
                check=True,
                capture_output=True,
                text=True
            )
            logger.info("apt update执行成功")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"apt update执行失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
            return False
    
    def get_package_list(self):
        """
        获取当前APT源中的软件包列表
        
        Returns:
            list: 软件包信息列表
        """
        logger.info("获取软件包列表...")
        
        # 获取可用的软件包信息
        available_pkgs = self._get_available_packages()
        
        # 获取已安装的软件包信息（包含大小）
        installed_pkgs = self._get_installed_packages_with_size()

        # 合并信息
        for pkg_name, pkg_info in installed_pkgs.items():
            if pkg_name in available_pkgs:
                available_pkgs[pkg_name]["status"] = "installed"
                # 如果APT数据中没有大小信息，使用dpkg的大小
                if "installed_size" not in available_pkgs[pkg_name] or available_pkgs[pkg_name]["installed_size"] == 0:
                    available_pkgs[pkg_name]["installed_size"] = pkg_info.get("installed_size", 0)
            
        # 转换为列表格式
        package_list = []
        for name, info in available_pkgs.items():
            package_list.append({
                "name": name,
                "version": info.get("version", ""),
                "architecture": info.get("architecture", ""),
                "description": info.get("description", ""),
                "status": info.get("status", "not-installed"),
                "installed_size": info.get("installed_size", 0)
            })
            
        logger.info(f"共获取到 {len(package_list)} 个软件包信息")
        return package_list
    
    def _get_available_packages(self):
        """
        获取可用的软件包信息
        
        Returns:
            dict: 软件包信息字典，以包名为键
        """
        try:
            result = subprocess.run(
                ["apt-cache", "dumpavail"], 
                check=True,
                capture_output=True,
                text=True
            )
            return self._parse_package_info(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"获取可用软件包信息失败: {e}")
            return {}
    
    def _get_installed_packages(self):
        """
        获取已安装的软件包信息

        Returns:
            dict: 已安装的软件包字典，以包名为键
        """
        try:
            result = subprocess.run(
                ["dpkg", "--get-selections"],
                check=True,
                capture_output=True,
                text=True
            )
            installed = {}
            for line in result.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2 and parts[1] == "install":
                    installed[parts[0]] = {"status": "installed"}
            return installed
        except subprocess.CalledProcessError as e:
            logger.error(f"获取已安装软件包信息失败: {e}")
            return {}

    def _get_installed_packages_with_size(self):
        """
        获取已安装的软件包信息（包含大小）

        Returns:
            dict: 已安装的软件包字典，以包名为键，包含大小信息
        """
        try:
            # 使用dpkg-query获取详细的已安装包信息
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Package}\t${Installed-Size}\n"],
                check=True,
                capture_output=True,
                text=True
            )

            installed = {}
            for line in result.stdout.splitlines():
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        pkg_name = parts[0]
                        try:
                            # dpkg显示的大小是KB，转换为字节
                            size_kb = int(parts[1])
                            size_bytes = size_kb * 1024
                        except (ValueError, TypeError):
                            size_bytes = 0

                        installed[pkg_name] = {
                            "status": "installed",
                            "installed_size": size_bytes
                        }

            logger.debug(f"获取到 {len(installed)} 个已安装包的大小信息")
            return installed

        except subprocess.CalledProcessError as e:
            logger.error(f"获取已安装软件包大小信息失败: {e}")
            # 降级到简单方法
            return self._get_installed_packages()
    
    def _parse_package_info(self, data):
        """
        解析软件包信息
        
        Args:
            data: apt-cache dumpavail的输出
            
        Returns:
            dict: 软件包信息字典，以包名为键
        """
        packages = {}
        current_pkg = None
        
        for line in data.splitlines():
            if not line.strip():
                current_pkg = None
                continue
                
            if line.startswith("Package: "):
                pkg_name = line[9:].strip()
                current_pkg = pkg_name
                packages[current_pkg] = {"name": current_pkg}
            elif current_pkg and ": " in line:
                key, value = line.split(": ", 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == "version":
                    packages[current_pkg]["version"] = value
                elif key == "architecture":
                    packages[current_pkg]["architecture"] = value
                elif key == "description":
                    packages[current_pkg]["description"] = value
                elif key == "installed-size":
                    # 将大小转换为字节数（KB -> bytes）
                    try:
                        size_kb = int(value)
                        packages[current_pkg]["installed_size"] = size_kb * 1024  # KB to bytes
                    except (ValueError, TypeError):
                        packages[current_pkg]["installed_size"] = 0
                    
        return packages