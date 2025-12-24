# -*- coding: utf-8 -*-
"""
包安全管理器：负责包安全性扫描和分析
"""

import subprocess
import logging
import re
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityScanner:
    """包安全扫描器"""
    
    def __init__(self):
        """初始化安全扫描器"""
        self.known_vulnerable_packages = self._load_vulnerability_database()
        self.suspicious_keywords = [
            'backdoor', 'malware', 'trojan', 'virus', 'rootkit',
            'exploit', 'payload', 'shell', 'reverse', 'bind'
        ]
    
    def _load_vulnerability_database(self):
        """
        加载漏洞数据库（简化版本）
        在实际实现中，这里会连接到CVE数据库或安全源
        """
        # 模拟漏洞数据库，实际中应从外部源获取
        return {
            'openssl': ['CVE-2023-0286', 'CVE-2023-0215'],
            'sudo': ['CVE-2021-3156'],
            'bash': ['CVE-2019-9924'],
            'nginx': ['CVE-2023-31147']
        }
    
    def scan_package(self, package_name, package_info=None):
        """
        扫描单个包的安全风险
        
        Args:
            package_name: 包名
            package_info: 包信息（可选）
            
        Returns:
            dict: 安全扫描结果
        """
        result = {
            'package': package_name,
            'risk_level': 'LOW',
            'vulnerabilities': [],
            'suspicious_files': [],
            'recommendations': [],
            'scan_timestamp': datetime.now().isoformat()
        }
        
        # 检查已知漏洞
        vulnerabilities = self._check_known_vulnerabilities(package_name, package_info)
        if vulnerabilities:
            result['vulnerabilities'] = vulnerabilities
            result['risk_level'] = 'HIGH'
        
        # 检查包描述和文件中是否包含可疑关键词
        suspicious_content = self._check_suspicious_content(package_name, package_info)
        if suspicious_content:
            result['suspicious_files'] = suspicious_content
            result['risk_level'] = 'MEDIUM'
        
        # 检查包来源和可信度
        trustworthiness = self._check_package_trustworthiness(package_name, package_info)
        if not trustworthiness['trusted']:
            result['risk_level'] = 'MEDIUM'
            result['recommendations'].append(f"包来源可能不可信: {trustworthiness['source']}")
        
        # 生成建议
        result['recommendations'].extend(self._generate_recommendations(package_name, result))
        
        return result
    
    def _check_known_vulnerabilities(self, package_name, package_info):
        """检查已知漏洞"""
        vulnerabilities = []
        
        # 检查包名是否在漏洞数据库中
        if package_name.lower() in self.known_vulnerable_packages:
            vulnerabilities.extend(self.known_vulnerable_packages[package_name.lower()])
        
        # 如果有包信息，检查版本特定的漏洞
        if package_info and 'version' in package_info:
            version = package_info['version']
            # 这里可以实现版本特定的漏洞检查
            # 例如：检查特定版本是否受已知CVE影响
            
        return vulnerabilities
    
    def _check_suspicious_content(self, package_name, package_info):
        """检查包内容中的可疑内容"""
        suspicious_files = []
        
        if not package_info:
            return suspicious_files
        
        # 检查描述中是否包含可疑关键词
        description = package_info.get('description', '').lower()
        for keyword in self.suspicious_keywords:
            if keyword in description:
                suspicious_files.append({
                    'file': 'description',
                    'keyword': keyword,
                    'context': description
                })
        
        # 尝试获取包中的文件列表并检查
        try:
            package_files = self._get_package_files(package_name)
            for file_info in package_files:
                file_path = file_info.get('path', '').lower()
                for keyword in self.suspicious_keywords:
                    if keyword in file_path:
                        suspicious_files.append({
                            'file': file_path,
                            'keyword': keyword,
                            'context': '文件名包含可疑关键词'
                        })
        except Exception as e:
            logger.warning(f"无法获取包 {package_name} 的文件列表: {e}")
        
        return suspicious_files
    
    def _get_package_files(self, package_name):
        """获取包中的文件列表"""
        try:
            result = subprocess.run(
                ["dpkg", "-L", package_name],
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            files = []
            for line in result.stdout.splitlines():
                if line.strip():
                    files.append({'path': line.strip()})
            
            return files
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.warning(f"无法获取包 {package_name} 的文件列表: {e}")
            return []
    
    def _check_package_trustworthiness(self, package_name, package_info):
        """检查包的可信度"""
        trustworthiness = {
            'trusted': True,
            'source': 'unknown',
            'signatures': [],
            'verification_status': 'unknown'
        }
        
        # 检查包是否来自官方源
        try:
            result = subprocess.run(
                ["apt-cache", "policy", package_name],
                check=True,
                capture_output=True,
                text=True
            )
            
            if "Candidate:" in result.stdout and "offical" in result.stdout.lower():
                trustworthiness['source'] = 'official'
                trustworthiness['trusted'] = True
            else:
                trustworthiness['source'] = 'third-party'
                trustworthiness['trusted'] = False
                
        except subprocess.CalledProcessError:
            trustworthiness['source'] = 'unknown'
            trustworthiness['trusted'] = False
        
        # 检查包签名（简化版本）
        try:
            sig_result = subprocess.run(
                ["apt-cache", "showsrc", package_name],
                check=True,
                capture_output=True,
                text=True
            )
            
            if "Maintainer:" in sig_result.stdout:
                maintainer = re.search(r'Maintainer: ([^<>]+)', sig_result.stdout)
                if maintainer:
                    trustworthiness['maintainer'] = maintainer.group(1).strip()
        except subprocess.CalledProcessError:
            pass
        
        return trustworthiness
    
    def _generate_recommendations(self, package_name, scan_result):
        """生成安全建议"""
        recommendations = []
        
        if scan_result['vulnerabilities']:
            recommendations.append("该包存在已知安全漏洞，建议立即更新")
            recommendations.append("建议关注相关CVE公告并及时打补丁")
        
        if scan_result['suspicious_files']:
            recommendations.append("包中检测到可疑内容，建议谨慎安装")
            recommendations.append("建议从官方源重新下载包")
        
        if scan_result['risk_level'] == 'HIGH':
            recommendations.append("高风险包，建议在测试环境中先验证")
            recommendations.append("考虑寻找替代包或安全版本")
        
        return recommendations
    
    def batch_scan(self, packages):
        """批量扫描多个包"""
        results = []
        
        for package in packages:
            package_name = package.get('name', '')
            if package_name:
                scan_result = self.scan_package(package_name, package)
                results.append(scan_result)
        
        return results
    
    def get_security_summary(self, scan_results):
        """获取安全扫描摘要"""
        total_packages = len(scan_results)
        high_risk = len([r for r in scan_results if r['risk_level'] == 'HIGH'])
        medium_risk = len([r for r in scan_results if r['risk_level'] == 'MEDIUM'])
        low_risk = total_packages - high_risk - medium_risk
        
        vulnerabilities = sum(len(r['vulnerabilities']) for r in scan_results)
        suspicious_files = sum(len(r['suspicious_files']) for r in scan_results)
        
        return {
            'total_packages': total_packages,
            'risk_distribution': {
                'HIGH': high_risk,
                'MEDIUM': medium_risk,
                'LOW': low_risk
            },
            'total_vulnerabilities': vulnerabilities,
            'total_suspicious_files': suspicious_files,
            'recommendations': self._generate_global_recommendations(scan_results)
        }
    
    def _generate_global_recommendations(self, scan_results):
        """生成全局安全建议"""
        recommendations = []
        
        high_risk_packages = [r for r in scan_results if r['risk_level'] == 'HIGH']
        if high_risk_packages:
            recommendations.append(f"发现 {len(high_risk_packages)} 个高风险包，建议立即处理")
        
        vulnerable_packages = [r for r in scan_results if r['vulnerabilities']]
        if vulnerable_packages:
            recommendations.append(f"发现 {len(vulnerable_packages)} 个包存在漏洞，建议及时更新")
        
        if not recommendations:
            recommendations.append("所有包的安全状态良好")
        
        return recommendations