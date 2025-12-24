# -*- coding: utf-8 -*-
"""
风险评估器：负责综合包风险评估和分析
"""

import logging
import json
import math
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class RiskAssessor:
    """包风险评估器"""
    
    def __init__(self):
        """初始化风险评估器"""
        self.risk_weights = {
            'security': 0.4,      # 安全风险权重
            'dependency': 0.25,   # 依赖风险权重
            'stability': 0.2,     # 稳定性风险权重
            'maintenance': 0.15   # 维护风险权重
        }
        
        self.package_reputation_db = self._load_reputation_database()
        self.critical_packages = self._load_critical_packages()
    
    def _load_reputation_database(self):
        """加载包信誉数据库"""
        # 模拟包信誉数据，实际中应从外部源获取
        return {
            'openssl': {'reputation_score': 9.5, 'maintainer_trust': 9.0},
            'bash': {'reputation_score': 9.0, 'maintainer_trust': 9.0},
            'sudo': {'reputation_score': 8.5, 'maintainer_trust': 8.5},
            'nginx': {'reputation_score': 8.0, 'maintainer_trust': 8.0},
            'python3': {'reputation_score': 9.0, 'maintainer_trust': 9.0}
        }
    
    def _load_critical_packages(self):
        """加载关键系统包列表"""
        return [
            'bash', 'coreutils', 'glibc', 'openssl', 'sudo', 'systemd',
            'util-linux', 'procps', 'sed', 'grep', 'tar', 'gzip'
        ]
    
    def assess_package_risk(self, package_name, package_info=None, security_scan=None, dependency_analysis=None):
        """
        评估单个包的风险
        
        Args:
            package_name: 包名
            package_info: 包基本信息
            security_scan: 安全扫描结果
            dependency_analysis: 依赖分析结果
            
        Returns:
            dict: 风险评估结果
        """
        logger.info(f"评估包 {package_name} 的风险...")
        
        # 基础风险评估
        base_risk = self._assess_base_risk(package_name, package_info)
        
        # 安全风险评估
        security_risk = self._assess_security_risk(package_name, security_scan)
        
        # 依赖风险评估
        dependency_risk = self._assess_dependency_risk(package_name, dependency_analysis)
        
        # 稳定性风险评估
        stability_risk = self._assess_stability_risk(package_name, package_info)
        
        # 维护风险评估
        maintenance_risk = self._assess_maintenance_risk(package_name, package_info)
        
        # 综合风险评分
        overall_risk_score = (
            security_risk['score'] * self.risk_weights['security'] +
            dependency_risk['score'] * self.risk_weights['dependency'] +
            stability_risk['score'] * self.risk_weights['stability'] +
            maintenance_risk['score'] * self.risk_weights['maintenance']
        )
        
        # 确定风险等级
        risk_level = self._calculate_risk_level(overall_risk_score)
        
        # 生成风险因子
        risk_factors = self._identify_risk_factors(
            base_risk, security_risk, dependency_risk, stability_risk, maintenance_risk
        )
        
        # 生成建议
        recommendations = self._generate_risk_recommendations(package_name, risk_level, risk_factors)
        
        return {
            'package': package_name,
            'risk_level': risk_level,
            'risk_score': round(overall_risk_score, 2),
            'risk_factors': risk_factors,
            'assessment_details': {
                'base_risk': base_risk,
                'security_risk': security_risk,
                'dependency_risk': dependency_risk,
                'stability_risk': stability_risk,
                'maintenance_risk': maintenance_risk
            },
            'recommendations': recommendations,
            'assessment_timestamp': datetime.now().isoformat()
        }
    
    def _assess_base_risk(self, package_name, package_info):
        """评估基础风险"""
        risk = {
            'score': 0.0,
            'factors': [],
            'description': '基础风险评估'
        }
        
        # 检查是否为关键系统包
        if package_name in self.critical_packages:
            risk['score'] += 0.3
            risk['factors'].append('关键系统包')
        
        # 检查包大小（较大的包可能有更多风险）
        if package_info and 'installed_size' in package_info:
            try:
                size_kb = int(package_info['installed_size'])
                if size_kb > 100 * 1024:  # 100MB以上
                    risk['score'] += 0.1
                    risk['factors'].append('包体积较大')
            except (ValueError, TypeError):
                pass
        
        # 检查包描述
        if package_info and 'description' in package_info:
            description = package_info['description'].lower()
            if any(keyword in description for keyword in ['experimental', 'beta', 'unstable']):
                risk['score'] += 0.2
                risk['factors'].append('包状态不稳定')
        
        return risk
    
    def _assess_security_risk(self, package_name, security_scan):
        """评估安全风险"""
        risk = {
            'score': 0.0,
            'factors': [],
            'description': '安全风险评估'
        }
        
        if not security_scan:
            risk['score'] = 0.5  # 默认中等风险
            risk['factors'].append('无安全扫描数据')
            return risk
        
        # 根据风险等级评分
        risk_level = security_scan.get('risk_level', 'LOW')
        if risk_level == 'HIGH':
            risk['score'] = 0.9
            risk['factors'].append('高安全风险')
        elif risk_level == 'MEDIUM':
            risk['score'] = 0.6
            risk['factors'].append('中等安全风险')
        else:
            risk['score'] = 0.2
            risk['factors'].append('低安全风险')
        
        # 根据漏洞数量调整
        vulnerabilities = security_scan.get('vulnerabilities', [])
        if vulnerabilities:
            risk['score'] = min(1.0, risk['score'] + len(vulnerabilities) * 0.1)
            risk['factors'].append(f'存在{len(vulnerabilities)}个已知漏洞')
        
        # 根据可疑文件调整
        suspicious_files = security_scan.get('suspicious_files', [])
        if suspicious_files:
            risk['score'] = min(1.0, risk['score'] + len(suspicious_files) * 0.1)
            risk['factors'].append(f'检测到{len(suspicious_files)}个可疑文件')
        
        return risk
    
    def _assess_dependency_risk(self, package_name, dependency_analysis):
        """评估依赖风险"""
        risk = {
            'score': 0.0,
            'factors': [],
            'description': '依赖风险评估'
        }
        
        if not dependency_analysis:
            risk['score'] = 0.3
            risk['factors'].append('无依赖分析数据')
            return risk
        
        # 根据依赖数量评分
        total_deps = dependency_analysis.get('total_dependencies', 0)
        if total_deps > 50:
            risk['score'] += 0.4
            risk['factors'].append('依赖数量过多')
        elif total_deps > 20:
            risk['score'] += 0.2
            risk['factors'].append('依赖数量较多')
        
        # 检查循环依赖
        circular_deps = dependency_analysis.get('circular_dependencies', [])
        if circular_deps:
            risk['score'] += 0.3
            risk['factors'].append(f'存在{len(circular_deps)}个循环依赖')
        
        # 检查孤立依赖
        orphaned_deps = dependency_analysis.get('orphaned_dependencies', [])
        if orphaned_deps:
            risk['score'] += 0.2
            risk['factors'].append(f'存在{len(orphaned_deps)}个孤立依赖')
        
        # 检查是否有反向依赖（被很多包依赖）
        reverse_deps = dependency_analysis.get('reverse_dependencies', [])
        if len(reverse_deps) > 10:
            risk['score'] += 0.2
            risk['factors'].append('被多个包依赖，更新影响面大')
        
        return risk
    
    def _assess_stability_risk(self, package_name, package_info):
        """评估稳定性风险"""
        risk = {
            'score': 0.0,
            'factors': [],
            'description': '稳定性风险评估'
        }
        
        # 检查包版本信息
        if package_info and 'version' in package_info:
            version = package_info['version']
            
            # 检查版本号中的稳定性标识
            if any(marker in version.lower() for marker in ['rc', 'alpha', 'beta', 'dev']):
                risk['score'] += 0.4
                risk['factors'].append('版本包含不稳定标识')
            elif '~' in version:  # Debian/Ubuntu的本地版本
                risk['score'] += 0.2
                risk['factors'].append('本地修改版本')
        
        # 检查包描述中的稳定性信息
        if package_info and 'description' in package_info:
            description = package_info['description'].lower()
            stability_keywords = ['stable', 'testing', 'unstable', 'experimental']
            
            if 'unstable' in description or 'experimental' in description:
                risk['score'] += 0.3
                risk['factors'].append('描述中提及不稳定')
            elif 'testing' in description:
                risk['score'] += 0.2
                risk['factors'].append('描述中提及测试版本')
        
        return risk
    
    def _assess_maintenance_risk(self, package_name, package_info):
        """评估维护风险"""
        risk = {
            'score': 0.0,
            'factors': [],
            'description': '维护风险评估'
        }
        
        # 检查包信誉
        if package_name in self.package_reputation_db:
            reputation = self.package_reputation_db[package_name]
            reputation_score = reputation['reputation_score']
            maintainer_trust = reputation['maintainer_trust']
            
            # 根据信誉评分调整风险
            if reputation_score < 5.0:
                risk['score'] += 0.4
                risk['factors'].append('包信誉较低')
            elif reputation_score < 7.0:
                risk['score'] += 0.2
                risk['factors'].append('包信誉一般')
            
            if maintainer_trust < 5.0:
                risk['score'] += 0.3
                risk['factors'].append('维护者可信度较低')
        
        # 检查包维护者信息
        if package_info:
            # 这里可以添加维护者相关的检查
            # 例如：检查维护者的其他包的质量等
            
            # 暂时基于包名长度和复杂性进行简单评估
            if len(package_name) > 20 or '_' in package_name or '-' in package_name:
                risk['score'] += 0.1
                risk['factors'].append('包名复杂，可能为第三方包')
        
        return risk
    
    def _calculate_risk_level(self, risk_score):
        """根据风险评分计算风险等级"""
        if risk_score >= 0.8:
            return 'CRITICAL'
        elif risk_score >= 0.6:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        elif risk_score >= 0.2:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _identify_risk_factors(self, base_risk, security_risk, dependency_risk, stability_risk, maintenance_risk):
        """识别主要风险因子"""
        all_factors = []
        
        # 收集所有风险因子
        for risk_category in [base_risk, security_risk, dependency_risk, stability_risk, maintenance_risk]:
            all_factors.extend(risk_category.get('factors', []))
        
        # 去重并按风险严重程度排序
        unique_factors = list(set(all_factors))
        
        # 风险因子严重程度排序（简化版本）
        priority_order = {
            '高安全风险': 1,
            '中等安全风险': 2,
            '存在已知漏洞': 3,
            '关键系统包': 4,
            '循环依赖': 5,
            '包信誉较低': 6
        }
        
        sorted_factors = sorted(unique_factors, 
                              key=lambda x: next((i for i, p in enumerate(priority_order) if p in x), 999))
        
        return sorted_factors
    
    def _generate_risk_recommendations(self, package_name, risk_level, risk_factors):
        """生成风险建议"""
        recommendations = []
        
        if risk_level == 'CRITICAL':
            recommendations.append("⚠️  关键风险包，建议立即进行安全评估")
            recommendations.append("在生产环境部署前必须在测试环境中充分验证")
            recommendations.append("考虑寻找安全替代方案")
        elif risk_level == 'HIGH':
            recommendations.append("🔍 高风险包，建议谨慎安装")
            recommendations.append("在安装前进行详细的安全和稳定性检查")
            recommendations.append("准备回滚计划")
        elif risk_level == 'MEDIUM':
            recommendations.append("⚡ 中等风险包，建议评估后安装")
            recommendations.append("监控安装后的系统状态")
        elif risk_level == 'LOW':
            recommendations.append("✅ 低风险包，可以正常安装")
        else:
            recommendations.append("🎯 最小风险包，安全安装")
        
        # 基于具体风险因子的建议
        if '存在已知漏洞' in risk_factors:
            recommendations.append("及时更新到安全版本")
            recommendations.append("关注相关CVE公告")
        
        if '循环依赖' in risk_factors:
            recommendations.append("检查并修复循环依赖关系")
            recommendations.append("考虑重新设计依赖结构")
        
        if '包信誉较低' in risk_factors:
            recommendations.append("验证包来源的可靠性")
            recommendations.append("考虑使用官方源中的替代包")
        
        return recommendations
    
    def batch_assess_risk(self, packages, security_scans=None, dependency_analyses=None):
        """批量风险评估"""
        results = []
        
        # 创建索引以便快速查找
        security_index = {s['package']: s for s in (security_scans or [])}
        dependency_index = {d['package']: d for d in (dependency_analyses or [])}
        
        for package in packages:
            package_name = package.get('name', '')
            if not package_name:
                continue
            
            security_scan = security_index.get(package_name)
            dependency_analysis = dependency_index.get(package_name)
            
            risk_assessment = self.assess_package_risk(
                package_name, package, security_scan, dependency_analysis
            )
            results.append(risk_assessment)
        
        return results
    
    def get_risk_summary(self, risk_assessments):
        """获取风险评估摘要"""
        total_packages = len(risk_assessments)
        
        if total_packages == 0:
            return {
                'total_packages': 0,
                'risk_distribution': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'MINIMAL': 0},
                'average_risk_score': 0.0,
                'top_risk_packages': [],
                'overall_recommendation': '无包需要评估'
            }
        
        # 风险分布统计
        risk_distribution = defaultdict(int)
        total_score = 0.0
        high_risk_packages = []
        
        for assessment in risk_assessments:
            risk_level = assessment['risk_level']
            risk_score = assessment['risk_score']
            
            risk_distribution[risk_level] += 1
            total_score += risk_score
            
            # 收集高风险包
            if risk_level in ['CRITICAL', 'HIGH']:
                high_risk_packages.append({
                    'package': assessment['package'],
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'factors': assessment['risk_factors'][:3]  # 只取前3个风险因子
                })
        
        # 按风险评分排序
        high_risk_packages.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # 生成整体建议
        overall_recommendation = self._generate_overall_recommendation(risk_distribution, total_packages)
        
        return {
            'total_packages': total_packages,
            'risk_distribution': dict(risk_distribution),
            'average_risk_score': round(total_score / total_packages, 2),
            'top_risk_packages': high_risk_packages[:10],  # 前10个高风险包
            'overall_recommendation': overall_recommendation
        }
    
    def _generate_overall_recommendation(self, risk_distribution, total_packages):
        """生成整体风险建议"""
        critical_count = risk_distribution.get('CRITICAL', 0)
        high_count = risk_distribution.get('HIGH', 0)
        
        if critical_count > 0:
            return f"发现{critical_count}个关键风险包，需要立即处理"
        elif high_count > 0:
            return f"发现{high_count}个高风险包，建议谨慎评估"
        elif total_packages > 0:
            return "包风险整体可控，可以正常部署"
        else:
            return "无风险包需要关注"