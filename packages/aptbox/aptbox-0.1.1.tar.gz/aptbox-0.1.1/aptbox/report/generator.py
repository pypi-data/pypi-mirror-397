# -*- coding: utf-8 -*-
"""
报告生成模块：负责生成可读的变更报告
"""

import os
import sys
import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportGenerator:
    """报告生成器，负责生成可读的变更报告"""
    
    def __init__(self, report_dir="/var/lib/aptbox/reports"):
        """
        初始化报告生成器
        
        Args:
            report_dir: 报告存储目录
        """
        self.report_dir = Path(report_dir)
        self._ensure_dir_exists()
    
    def _ensure_dir_exists(self):
        """确保报告目录存在"""
        try:
            os.makedirs(self.report_dir, exist_ok=True)
        except PermissionError:
            logger.error(f"无权限创建目录: {self.report_dir}")
            logger.error("请使用sudo运行或指定一个有写入权限的目录")
            sys.exit(1)
    
    def generate_report(self, comparison_result):
        """
        根据比较结果生成报告
        
        Args:
            comparison_result: 快照比较结果
            
        Returns:
            tuple: (报告内容, 报告文件路径)
        """
        logger.info("生成变更报告...")
        
        # 获取时间信息
        before_time = self._format_timestamp(comparison_result["before_timestamp"])
        after_time = self._format_timestamp(comparison_result["after_timestamp"])
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 生成报告内容
        report = []
        report.append("# APT软件包变更报告")
        report.append(f"生成时间: {current_time}")
        report.append("")
        
        # 添加摘要信息
        summary = comparison_result["summary"]
        report.append("## 摘要")
        report.append(f"- 更新前软件包总数: {summary['total_before']}")
        report.append(f"- 更新后软件包总数: {summary['total_after']}")
        report.append(f"- 新增软件包: {summary['new_count']}")
        report.append(f"- 删除软件包: {summary['removed_count']}")
        report.append(f"- 更新软件包: {summary['updated_count']}")
        report.append("")
        
        # 添加时间信息
        report.append("## 时间信息")
        report.append(f"- 更新前快照时间: {before_time}")
        report.append(f"- 更新后快照时间: {after_time}")
        report.append(f"- 报告生成时间: {current_time}")
        report.append("")
        
        # 添加包大小统计信息
        if "size_stats" in comparison_result:
            report.extend(self._format_size_stats(comparison_result["size_stats"]))
        
        # 添加更新的软件包信息
        if comparison_result["updated_packages"]:
            report.append("## 更新的软件包")
            for pkg in comparison_result["updated_packages"]:
                name = pkg["name"]
                old_ver = pkg["before"]["version"]
                new_ver = pkg["after"]["version"]
                report.append(f"- {name}: {old_ver} -> {new_ver}")
            report.append("")
        
        # 添加新增的软件包信息
        if comparison_result["new_packages"]:
            report.append("## 新增的软件包")
            for pkg in comparison_result["new_packages"]:
                name = pkg["name"]
                ver = pkg["version"]
                report.append(f"- {name}: {ver}")
            report.append("")
        
        # 添加删除的软件包信息
        if comparison_result["removed_packages"]:
            report.append("## 删除的软件包")
            for pkg in comparison_result["removed_packages"]:
                name = pkg["name"]
                ver = pkg["version"]
                report.append(f"- {name}: {ver}")
            report.append("")
        
        # 生成报告文件
        report_content = "\n".join(report)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"apt_report_{timestamp}.md"
        report_path = self.report_dir / report_filename
        
        self.save_report(report_content, report_path)
        
        return report_content, report_path
    
    def _format_size_stats(self, size_stats):
        """
        格式化包大小统计信息
        
        Args:
            size_stats: 包大小统计字典
            
        Returns:
            list: 报告行列表
        """
        report = []
        report.append("## 包大小统计")
        
        before_size_mb = size_stats["before_total_size"] / 1024
        after_size_mb = size_stats["after_total_size"] / 1024
        change_mb = size_stats["size_change"] / 1024
        new_size_mb = size_stats["new_packages_size"] / 1024
        removed_size_mb = size_stats["removed_packages_size"] / 1024
        updated_increase_mb = size_stats["updated_size_increase"] / 1024
        
        report.append(f"- 更新前总大小: {before_size_mb:.2f} MB")
        report.append(f"- 更新后总大小: {after_size_mb:.2f} MB")
        
        change_str = f"+{change_mb:.2f}" if change_mb >= 0 else f"{change_mb:.2f}"
        report.append(f"- 大小变化: {change_str} MB")
        report.append("")
        
        report.append("### 新增包总大小")
        report.append(f"- {new_size_mb:.2f} MB")
        if size_stats["largest_new_packages"]:
            report.append("  最大的新增包:")
            for pkg in size_stats["largest_new_packages"]:
                pkg_size_mb = pkg.get("installed_size", 0) / 1024
                report.append(f"  - {pkg['name']}: {pkg_size_mb:.2f} MB")
        report.append("")
        
        report.append("### 删除包总大小")
        report.append(f"- {removed_size_mb:.2f} MB")
        if size_stats["largest_removed_packages"]:
            report.append("  最大的删除包:")
            for pkg in size_stats["largest_removed_packages"]:
                pkg_size_mb = pkg.get("installed_size", 0) / 1024
                report.append(f"  - {pkg['name']}: {pkg_size_mb:.2f} MB")
        report.append("")
        
        if size_stats["largest_updated_packages"]:
            report.append("### 大小变化最大的更新包")
            for pkg in size_stats["largest_updated_packages"]:
                change_mb = pkg["size_change"] / 1024
                change_str = f"+{change_mb:.2f}" if change_mb >= 0 else f"{change_mb:.2f}"
                report.append(f"- {pkg['name']}: {change_str} MB ({pkg['before']['version']} -> {pkg['after']['version']})")
            report.append("")
        
        return report
    
    def save_report(self, report, path):
        """
        将报告保存到文件
        
        Args:
            report: 报告内容
            path: 文件路径
        """
        try:
            with open(path, 'w') as f:
                f.write(report)
            logger.info(f"报告已保存到: {path}")
        except PermissionError:
            logger.error(f"无权限写入文件: {path}")
            logger.error("请使用sudo运行或指定一个有写入权限的目录")
            sys.exit(1)
    
    def _format_timestamp(self, timestamp):
        """
        格式化时间戳
        
        Args:
            timestamp: ISO格式的时间戳
            
        Returns:
            str: 格式化后的时间字符串
        """
        try:
            dt = datetime.datetime.fromisoformat(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return timestamp