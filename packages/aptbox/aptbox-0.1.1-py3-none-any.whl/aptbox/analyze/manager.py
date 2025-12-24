# -*- coding: utf-8 -*-
"""
包分析管理器：协调安全扫描、依赖分析和风险评估
"""

import logging
import json
import argparse
from pathlib import Path

from .security import SecurityScanner
from .dependency import DependencyAnalyzer
from .risk import RiskAssessor

logger = logging.getLogger(__name__)

class PackageAnalyzer:
    """包分析管理器"""
    
    def __init__(self):
        """初始化包分析管理器"""
        self.security_scanner = SecurityScanner()
        self.dependency_analyzer = DependencyAnalyzer()
        self.risk_assessor = RiskAssessor()
    
    def analyze_package(self, package_name, include_security=True, include_dependencies=True, include_risk=True):
        """
        全面分析单个包
        
        Args:
            package_name: 包名
            include_security: 是否包含安全扫描
            include_dependencies: 是否包含依赖分析
            include_risk: 是否包含风险评估
            
        Returns:
            dict: 完整的包分析结果
        """
        logger.info(f"开始分析包: {package_name}")
        
        result = {
            'package': package_name,
            'analysis_timestamp': None,
            'security_analysis': None,
            'dependency_analysis': None,
            'risk_assessment': None,
            'summary': {}
        }
        
        try:
            # 获取包基本信息
            from aptbox.apt.manager import AptManager
            apt_manager = AptManager()
            package_info = self._get_package_info(package_name, apt_manager)
            
            result['package_info'] = package_info
            
            # 执行安全扫描
            if include_security:
                logger.info("执行安全扫描...")
                security_result = self.security_scanner.scan_package(package_name, package_info)
                result['security_analysis'] = security_result
            
            # 执行依赖分析
            if include_dependencies:
                logger.info("执行依赖分析...")
                dependency_result = self.dependency_analyzer.analyze_package_dependencies(package_name)
                result['dependency_analysis'] = dependency_result
            
            # 执行风险评估
            if include_risk:
                logger.info("执行风险评估...")
                risk_result = self.risk_assessor.assess_package_risk(
                    package_name, 
                    package_info,
                    result.get('security_analysis'),
                    result.get('dependency_analysis')
                )
                result['risk_assessment'] = risk_result
            
            # 生成摘要
            result['summary'] = self._generate_analysis_summary(result)
            result['analysis_timestamp'] = self._get_current_timestamp()
            
        except Exception as e:
            logger.error(f"分析包 {package_name} 时发生错误: {e}")
            result['error'] = str(e)
        
        return result
    
    def _get_package_info(self, package_name, apt_manager):
        """获取包详细信息"""
        try:
            # 使用apt-cache获取包信息
            import subprocess
            result = subprocess.run(
                ["apt-cache", "show", package_name],
                check=True,
                capture_output=True,
                text=True
            )
            
            package_info = {}
            current_field = None
            
            for line in result.stdout.splitlines():
                line = line.strip()
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'package':
                        package_info['name'] = value
                    elif key == 'version':
                        package_info['version'] = value
                    elif key == 'architecture':
                        package_info['architecture'] = value
                    elif key == 'size':
                        package_info['size'] = value
                    elif key == 'installed-size':
                        package_info['installed_size'] = value
                    elif key == 'maintainer':
                        package_info['maintainer'] = value
                    elif key == 'description':
                        package_info['description'] = value
                    elif key == 'homepage':
                        package_info['homepage'] = value
                    elif key == 'section':
                        package_info['section'] = value
                    elif key == 'priority':
                        package_info['priority'] = value
                    
                    current_field = key
            
            # 填充默认值
            package_info.setdefault('name', package_name)
            package_info.setdefault('version', 'unknown')
            package_info.setdefault('architecture', 'unknown')
            package_info.setdefault('description', 'No description available')
            
            return package_info
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"无法获取包 {package_name} 的详细信息: {e}")
            return {
                'name': package_name,
                'version': 'unknown',
                'architecture': 'unknown',
                'description': 'Package information unavailable'
            }
    
    def _generate_analysis_summary(self, analysis_result):
        """生成分析摘要"""
        summary = {
            'package': analysis_result['package'],
            'overall_status': 'unknown'
        }
        
        # 安全状态摘要
        if analysis_result.get('security_analysis'):
            security = analysis_result['security_analysis']
            summary['security_status'] = security.get('risk_level', 'UNKNOWN')
            summary['security_issues'] = len(security.get('vulnerabilities', []))
        
        # 依赖状态摘要
        if analysis_result.get('dependency_analysis'):
            dependency = analysis_result['dependency_analysis']
            summary['dependency_status'] = 'analyzed'
            summary['total_dependencies'] = dependency.get('total_dependencies', 0)
            summary['circular_dependencies'] = len(dependency.get('circular_dependencies', []))
            summary['orphaned_dependencies'] = len(dependency.get('orphaned_dependencies', []))
        
        # 风险状态摘要
        if analysis_result.get('risk_assessment'):
            risk = analysis_result['risk_assessment']
            summary['risk_level'] = risk.get('risk_level', 'UNKNOWN')
            summary['risk_score'] = risk.get('risk_score', 0.0)
            summary['risk_factors'] = len(risk.get('risk_factors', []))
        
        # 总体状态评估
        if analysis_result.get('risk_assessment'):
            risk_level = analysis_result['risk_assessment'].get('risk_level', 'UNKNOWN')
            security_status = analysis_result.get('security_analysis', {}).get('risk_level', 'UNKNOWN')
            
            if risk_level in ['CRITICAL', 'HIGH'] or security_status in ['HIGH']:
                summary['overall_status'] = 'high_risk'
            elif risk_level in ['MEDIUM'] or security_status in ['MEDIUM']:
                summary['overall_status'] = 'medium_risk'
            else:
                summary['overall_status'] = 'low_risk'
        
        return summary
    
    def _get_current_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def batch_analyze(self, package_list, include_security=True, include_dependencies=True, include_risk=True):
        """
        批量分析多个包
        
        Args:
            package_list: 包名列表
            include_security: 是否包含安全扫描
            include_dependencies: 是否包含依赖分析
            include_risk: 是否包含风险评估
            
        Returns:
            dict: 批量分析结果
        """
        logger.info(f"开始批量分析 {len(package_list)} 个包")
        
        results = []
        errors = []
        
        for package_name in package_list:
            try:
                result = self.analyze_package(package_name, include_security, include_dependencies, include_risk)
                if 'error' not in result:
                    results.append(result)
                else:
                    errors.append({'package': package_name, 'error': result['error']})
            except Exception as e:
                error_msg = f"分析包 {package_name} 时发生未预期错误: {e}"
                logger.error(error_msg)
                errors.append({'package': package_name, 'error': error_msg})
        
        # 生成批量分析摘要
        batch_summary = self._generate_batch_summary(results, errors)
        
        return {
            'batch_analysis': {
                'total_packages': len(package_list),
                'successful_analyses': len(results),
                'failed_analyses': len(errors),
                'success_rate': round(len(results) / len(package_list) * 100, 2) if package_list else 0
            },
            'results': results,
            'errors': errors,
            'summary': batch_summary
        }
    
    def _generate_batch_summary(self, results, errors):
        """生成批量分析摘要"""
        if not results:
            return {
                'status': 'no_successful_analyses',
                'message': '所有包分析都失败了'
            }
        
        # 安全分析摘要
        security_summaries = []
        for result in results:
            if result.get('security_analysis'):
                security_summaries.append(result['security_analysis']['risk_level'])
        
        # 风险分析摘要
        risk_summaries = []
        for result in results:
            if result.get('risk_assessment'):
                risk_summaries.append(result['risk_assessment']['risk_level'])
        
        # 依赖分析摘要
        dependency_summaries = []
        for result in results:
            if result.get('dependency_analysis'):
                dependency_summaries.append({
                    'total_deps': result['dependency_analysis'].get('total_dependencies', 0),
                    'circular_deps': len(result['dependency_analysis'].get('circular_dependencies', []))
                })
        
        # 统计各种风险等级的包数量
        risk_distribution = {}
        security_distribution = {}
        
        for risk_level in risk_summaries:
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        
        for security_level in security_summaries:
            security_distribution[security_level] = security_distribution.get(security_level, 0) + 1
        
        return {
            'status': 'completed',
            'risk_distribution': risk_distribution,
            'security_distribution': security_distribution,
            'dependency_stats': {
                'total_analyzed': len(dependency_summaries),
                'average_dependencies': round(sum(d['total_deps'] for d in dependency_summaries) / len(dependency_summaries), 2) if dependency_summaries else 0,
                'packages_with_circular_deps': len([d for d in dependency_summaries if d['circular_deps'] > 0])
            },
            'error_count': len(errors)
        }
    
    def generate_report(self, analysis_result, output_format='text'):
        """
        生成分析报告
        
        Args:
            analysis_result: 分析结果
            output_format: 输出格式 ('text', 'json', 'markdown')
            
        Returns:
            str: 格式化的报告
        """
        if output_format == 'json':
            return json.dumps(analysis_result, indent=2, ensure_ascii=False)
        elif output_format == 'markdown':
            return self._generate_markdown_report(analysis_result)
        else:
            return self._generate_text_report(analysis_result)
    
    def _generate_text_report(self, analysis_result):
        """生成文本格式报告"""
        lines = []
        package_name = analysis_result['package']
        
        lines.append("=" * 60)
        lines.append(f"包分析报告: {package_name}")
        lines.append("=" * 60)
        lines.append("")
        
        # 包基本信息
        if 'package_info' in analysis_result:
            info = analysis_result['package_info']
            lines.append("📦 包基本信息:")
            lines.append(f"  名称: {info.get('name', 'unknown')}")
            lines.append(f"  版本: {info.get('version', 'unknown')}")
            lines.append(f"  架构: {info.get('architecture', 'unknown')}")
            lines.append(f"  维护者: {info.get('maintainer', 'unknown')}")
            if info.get('installed_size'):
                try:
                    size_kb = int(info['installed_size'])
                    if size_kb < 1024:
                        size_str = f"{size_kb} KB"
                    elif size_kb < 1024 * 1024:
                        size_str = f"{size_kb/1024:.2f} MB"
                    else:
                        size_str = f"{size_kb/(1024*1024):.2f} GB"
                    lines.append(f"  大小: {size_str}")
                except (ValueError, TypeError):
                    pass
            lines.append("")
        
        # 安全分析
        if analysis_result.get('security_analysis'):
            security = analysis_result['security_analysis']
            lines.append("🔒 安全分析:")
            lines.append(f"  风险等级: {security.get('risk_level', 'unknown')}")
            
            if security.get('vulnerabilities'):
                lines.append(f"  已知漏洞: {len(security['vulnerabilities'])}")
                for vuln in security['vulnerabilities']:
                    lines.append(f"    - {vuln}")
            
            if security.get('suspicious_files'):
                lines.append(f"  可疑文件: {len(security['suspicious_files'])}")
                for file_info in security['suspicious_files'][:5]:  # 只显示前5个
                    lines.append(f"    - {file_info.get('file', 'unknown')}: {file_info.get('context', '')}")
            
            if security.get('recommendations'):
                lines.append("  安全建议:")
                for rec in security['recommendations']:
                    lines.append(f"    - {rec}")
            lines.append("")
        
        # 依赖分析
        if analysis_result.get('dependency_analysis'):
            dependency = analysis_result['dependency_analysis']
            lines.append("🔗 依赖分析:")
            lines.append(f"  总依赖数: {dependency.get('total_dependencies', 0)}")
            lines.append(f"  直接依赖: {len(dependency.get('direct_dependencies', []))}")
            lines.append(f"  间接依赖: {len(dependency.get('indirect_dependencies', []))}")
            lines.append(f"  反向依赖: {len(dependency.get('reverse_dependencies', []))}")
            
            if dependency.get('circular_dependencies'):
                lines.append(f"  循环依赖: {len(dependency['circular_dependencies'])}")
                for cycle in dependency['circular_dependencies'][:3]:  # 只显示前3个
                    lines.append(f"    - {cycle.get('description', 'unknown')}")
            
            if dependency.get('orphaned_dependencies'):
                lines.append(f"  孤立依赖: {len(dependency['orphaned_dependencies'])}")
                for orphan in dependency['orphaned_dependencies'][:5]:  # 只显示前5个
                    lines.append(f"    - {orphan}")
            lines.append("")
        
        # 风险评估
        if analysis_result.get('risk_assessment'):
            risk = analysis_result['risk_assessment']
            lines.append("⚠️  风险评估:")
            lines.append(f"  风险等级: {risk.get('risk_level', 'unknown')}")
            lines.append(f"  风险评分: {risk.get('risk_score', 0.0)}/1.0")
            
            if risk.get('risk_factors'):
                lines.append("  风险因子:")
                for factor in risk['risk_factors']:
                    lines.append(f"    - {factor}")
            
            if risk.get('recommendations'):
                lines.append("  风险建议:")
                for rec in risk['recommendations']:
                    lines.append(f"    - {rec}")
            lines.append("")
        
        # 总体摘要
        if analysis_result.get('summary'):
            summary = analysis_result['summary']
            lines.append("📊 分析摘要:")
            lines.append(f"  总体状态: {summary.get('overall_status', 'unknown')}")
            lines.append(f"  安全状态: {summary.get('security_status', 'unknown')}")
            lines.append(f"  风险等级: {summary.get('risk_level', 'unknown')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self, analysis_result):
        """生成Markdown格式报告"""
        lines = []
        package_name = analysis_result['package']
        
        lines.append(f"# 包分析报告: {package_name}")
        lines.append("")
        lines.append(f"**分析时间**: {analysis_result.get('analysis_timestamp', 'unknown')}")
        lines.append("")
        
        # 包基本信息
        if 'package_info' in analysis_result:
            info = analysis_result['package_info']
            lines.append("## 📦 包基本信息")
            lines.append("")
            lines.append("| 字段 | 值 |")
            lines.append("|------|----|")
            lines.append(f"| 名称 | {info.get('name', 'unknown')} |")
            lines.append(f"| 版本 | {info.get('version', 'unknown')} |")
            lines.append(f"| 架构 | {info.get('architecture', 'unknown')} |")
            lines.append(f"| 维护者 | {info.get('maintainer', 'unknown')} |")
            if info.get('section'):
                lines.append(f"| 分类 | {info.get('section')} |")
            if info.get('priority'):
                lines.append(f"| 优先级 | {info.get('priority')} |")
            lines.append("")
        
        # 安全分析
        if analysis_result.get('security_analysis'):
            security = analysis_result['security_analysis']
            lines.append("## 🔒 安全分析")
            lines.append("")
            lines.append(f"**风险等级**: {security.get('risk_level', 'unknown')}")
            lines.append("")
            
            if security.get('vulnerabilities'):
                lines.append("### 已知漏洞")
                lines.append("")
                for vuln in security['vulnerabilities']:
                    lines.append(f"- {vuln}")
                lines.append("")
            
            if security.get('suspicious_files'):
                lines.append("### 可疑文件")
                lines.append("")
                for file_info in security['suspicious_files']:
                    lines.append(f"- **{file_info.get('file', 'unknown')}**: {file_info.get('context', '')}")
                lines.append("")
            
            if security.get('recommendations'):
                lines.append("### 安全建议")
                lines.append("")
                for rec in security['recommendations']:
                    lines.append(f"- {rec}")
                lines.append("")
        
        # 风险评估
        if analysis_result.get('risk_assessment'):
            risk = analysis_result['risk_assessment']
            lines.append("## ⚠️ 风险评估")
            lines.append("")
            lines.append(f"**风险等级**: {risk.get('risk_level', 'unknown')}")
            lines.append(f"**风险评分**: {risk.get('risk_score', 0.0)}/1.0")
            lines.append("")
            
            if risk.get('risk_factors'):
                lines.append("### 风险因子")
                lines.append("")
                for factor in risk['risk_factors']:
                    lines.append(f"- {factor}")
                lines.append("")
            
            if risk.get('recommendations'):
                lines.append("### 风险建议")
                lines.append("")
                for rec in risk['recommendations']:
                    lines.append(f"- {rec}")
                lines.append("")
        
        # 依赖分析
        if analysis_result.get('dependency_analysis'):
            dependency = analysis_result['dependency_analysis']
            lines.append("## 🔗 依赖分析")
            lines.append("")
            lines.append("| 类型 | 数量 |")
            lines.append("|------|------|")
            lines.append(f"| 总依赖 | {dependency.get('total_dependencies', 0)} |")
            lines.append(f"| 直接依赖 | {len(dependency.get('direct_dependencies', []))} |")
            lines.append(f"| 间接依赖 | {len(dependency.get('indirect_dependencies', []))} |")
            lines.append(f"| 反向依赖 | {len(dependency.get('reverse_dependencies', []))} |")
            lines.append("")
            
            if dependency.get('circular_dependencies'):
                lines.append("### 循环依赖")
                lines.append("")
                for cycle in dependency['circular_dependencies']:
                    lines.append(f"- {cycle.get('description', 'unknown')}")
                lines.append("")
            
            if dependency.get('orphaned_dependencies'):
                lines.append("### 孤立依赖")
                lines.append("")
                for orphan in dependency['orphaned_dependencies']:
                    lines.append(f"- {orphan}")
                lines.append("")
        
        # 总体摘要
        if analysis_result.get('summary'):
            summary = analysis_result['summary']
            lines.append("## 📊 分析摘要")
            lines.append("")
            lines.append("| 方面 | 状态 |")
            lines.append("|------|------|")
            lines.append(f"| 总体状态 | {summary.get('overall_status', 'unknown')} |")
            lines.append(f"| 安全状态 | {summary.get('security_status', 'unknown')} |")
            lines.append(f"| 风险等级 | {summary.get('risk_level', 'unknown')} |")
            if summary.get('security_issues') is not None:
                lines.append(f"| 安全问题 | {summary.get('security_issues')} |")
            lines.append("")
        
        return "\n".join(lines)