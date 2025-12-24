# -*- coding: utf-8 -*-
"""
依赖分析器：负责包依赖关系分析和可视化
"""

import subprocess
import logging
import json
from collections import defaultdict, deque
import networkx as nx

logger = logging.getLogger(__name__)

class DependencyAnalyzer:
    """包依赖分析器"""
    
    def __init__(self):
        """初始化依赖分析器"""
        self.dependency_cache = {}
        self.reverse_dependency_cache = {}
    
    def analyze_package_dependencies(self, package_name, max_depth=3):
        """
        分析指定包的依赖关系
        
        Args:
            package_name: 包名
            max_depth: 最大分析深度
            
        Returns:
            dict: 依赖分析结果
        """
        logger.info(f"分析包 {package_name} 的依赖关系...")
        
        result = {
            'package': package_name,
            'direct_dependencies': [],
            'indirect_dependencies': [],
            'reverse_dependencies': [],
            'dependency_graph': {},
            'circular_dependencies': [],
            'orphaned_dependencies': [],
            'analysis_depth': max_depth,
            'total_dependencies': 0
        }
        
        # 获取直接依赖
        direct_deps = self._get_direct_dependencies(package_name)
        result['direct_dependencies'] = direct_deps
        
        # 构建依赖图
        dependency_graph = self._build_dependency_graph(package_name, max_depth)
        result['dependency_graph'] = dependency_graph
        
# 分析间接依赖
        all_deps = set()
        for level_deps in dependency_graph.values():
            all_deps.update(level_deps)
        
        # 获取直接依赖的包名集合
        direct_dep_names = {dep['name'] for dep in direct_deps}
        result['indirect_dependencies'] = list(all_deps - direct_dep_names)
        
        # 获取反向依赖（依赖当前包的其他包）
        result['reverse_dependencies'] = self._get_reverse_dependencies(package_name)
        
        # 检测循环依赖
        result['circular_dependencies'] = self._detect_circular_dependencies(dependency_graph)
        
        # 识别孤立依赖
        result['orphaned_dependencies'] = self._find_orphaned_dependencies(package_name, all_deps)
        
        # 统计总数
        result['total_dependencies'] = len(all_deps)
        
        return result
    
    def _get_direct_dependencies(self, package_name):
        """获取包直接依赖"""
        try:
            result = subprocess.run(
                ["apt-cache", "depends", package_name],
                check=True,
                capture_output=True,
                text=True
            )
            
            dependencies = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("Depends:"):
                    dep_name = line.replace("Depends:", "").strip()
                    # 移除版本限制和其他复杂标记
                    dep_name = dep_name.split()[0] if dep_name.split() else dep_name
                    dependencies.append({
                        'name': dep_name,
                        'type': 'depends'
                    })
                elif line.startswith("Recommends:"):
                    dep_name = line.replace("Recommends:", "").strip()
                    dep_name = dep_name.split()[0] if dep_name.split() else dep_name
                    dependencies.append({
                        'name': dep_name,
                        'type': 'recommends'
                    })
                elif line.startswith("Suggests:"):
                    dep_name = line.replace("Suggests:", "").strip()
                    dep_name = dep_name.split()[0] if dep_name.split() else dep_name
                    dependencies.append({
                        'name': dep_name,
                        'type': 'suggests'
                    })
            
            return dependencies
        except subprocess.CalledProcessError as e:
            logger.warning(f"无法获取包 {package_name} 的依赖信息: {e}")
            return []
    
    def _build_dependency_graph(self, package_name, max_depth):
        """构建依赖关系图"""
        graph = defaultdict(set)
        visited = set()
        queue = deque([(package_name, 0)])
        
        while queue:
            current_package, depth = queue.popleft()
            
            if current_package in visited or depth >= max_depth:
                continue
                
            visited.add(current_package)
            
            # 获取当前包的直接依赖
            direct_deps = self._get_direct_dependencies(current_package)
            
            for dep in direct_deps:
                dep_name = dep['name']
                graph[current_package].add(dep_name)
                
                if dep_name not in visited and depth + 1 < max_depth:
                    queue.append((dep_name, depth + 1))
        
        return dict(graph)
    
    def _get_reverse_dependencies(self, package_name):
        """获取反向依赖（依赖当前包的其他包）"""
        try:
            # 使用apt-rdepends获取反向依赖（如果可用）
            result = subprocess.run(
                ["apt-rdepends", "-r", package_name],
                check=False,  # 允许命令失败
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                reverse_deps = []
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if line and line != package_name:
                        reverse_deps.append(line)
                return reverse_deps
            else:
                # 如果apt-rdepends不可用，使用dpkg查询
                return self._get_reverse_dependencies_fallback(package_name)
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("apt-rdepends 不可用，使用备用方法")
            return self._get_reverse_dependencies_fallback(package_name)
    
    def _get_reverse_dependencies_fallback(self, package_name):
        """备用反向依赖查询方法"""
        try:
            result = subprocess.run(
                ["dpkg", "--audit"],
                check=False,
                capture_output=True,
                text=True
            )
            
            # 这是一个简化的实现，实际中需要更复杂的查询
            # 返回空列表，因为完整的反向依赖查询需要索引
            return []
        except subprocess.CalledProcessError:
            return []
    
    def _detect_circular_dependencies(self, dependency_graph):
        """检测循环依赖"""
        circular_deps = []
        
        # 使用NetworkX检测循环（如果可用）
        try:
            import networkx as nx
            G = nx.DiGraph()
            
            for package, deps in dependency_graph.items():
                for dep in deps:
                    G.add_edge(package, dep)
            
            cycles = list(nx.simple_cycles(G))
            for cycle in cycles:
                cycle_str = " -> ".join(cycle + [cycle[0]])
                circular_deps.append({
                    'cycle': cycle,
                    'description': cycle_str
                })
                
        except ImportError:
            # 如果没有NetworkX，使用简化的循环检测
            circular_deps = self._detect_circular_dependencies_simple(dependency_graph)
        
        return circular_deps
    
    def _detect_circular_dependencies_simple(self, dependency_graph):
        """简单的循环依赖检测"""
        def has_cycle_dfs(node, path, visited, rec_stack):
            visited[node] = True
            rec_stack[node] = True
            path.append(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle_dfs(neighbor, path[:], visited, rec_stack):
                        return True
                elif rec_stack.get(neighbor, False):
                    # 发现循环
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    return cycle
            
            rec_stack[node] = False
            return False
        
        visited = {}
        rec_stack = {}
        cycles = []
        
        for node in dependency_graph.keys():
            if node not in visited:
                cycle = has_cycle_dfs(node, [], visited, rec_stack)
                if cycle:
                    cycles.append({
                        'cycle': cycle,
                        'description': " -> ".join(cycle + [cycle[0]])
                    })
        
        return cycles
    
    def _find_orphaned_dependencies(self, root_package, all_dependencies):
        """查找孤立依赖（没有其他包依赖的依赖）"""
        orphaned = []
        
        try:
            # 获取系统中所有已安装的包
            result = subprocess.run(
                ["dpkg", "--get-selections"],
                check=True,
                capture_output=True,
                text=True
            )
            
            installed_packages = set()
            for line in result.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2 and parts[1] == 'install':
                    installed_packages.add(parts[0])
            
            # 检查每个依赖是否被其他已安装的包需要
            for dep in all_dependencies:
                if dep not in installed_packages:
                    continue
                    
                # 检查是否有其他已安装的包依赖这个包
                is_needed = False
                for pkg in installed_packages:
                    if pkg == root_package or pkg == dep:
                        continue
                    
                    deps = self._get_direct_dependencies(pkg)
                    if any(d['name'] == dep for d in deps):
                        is_needed = True
                        break
                
                if not is_needed:
                    orphaned.append(dep)
                    
        except subprocess.CalledProcessError as e:
            logger.warning(f"无法获取已安装包列表: {e}")
        
        return orphaned
    
    def analyze_dependency_tree(self, package_name, format='text'):
        """
        分析依赖树并生成可视化结果
        
        Args:
            package_name: 包名
            format: 输出格式 ('text', 'json', 'dot')
            
        Returns:
            str: 格式化的依赖树
        """
        result = self.analyze_package_dependencies(package_name)
        
        if format == 'json':
            return json.dumps(result, indent=2, ensure_ascii=False)
        elif format == 'dot':
            return self._generate_dot_graph(result)
        else:
            return self._generate_text_tree(result)
    
    def _generate_text_tree(self, analysis_result):
        """生成文本格式的依赖树"""
        lines = []
        package = analysis_result['package']
        
        lines.append(f"依赖分析: {package}")
        lines.append("=" * 50)
        
        # 直接依赖
        if analysis_result['direct_dependencies']:
            lines.append("\n直接依赖:")
            for dep in analysis_result['direct_dependencies']:
                lines.append(f"  ├── {dep['name']} ({dep['type']})")
        
        # 统计信息
        lines.append(f"\n统计信息:")
        lines.append(f"  总依赖数: {analysis_result['total_dependencies']}")
        lines.append(f"  直接依赖: {len(analysis_result['direct_dependencies'])}")
        lines.append(f"  间接依赖: {len(analysis_result['indirect_dependencies'])}")
        lines.append(f"  反向依赖: {len(analysis_result['reverse_dependencies'])}")
        
        # 循环依赖
        if analysis_result['circular_dependencies']:
            lines.append(f"\n循环依赖: {len(analysis_result['circular_dependencies'])}")
            for cycle in analysis_result['circular_dependencies']:
                lines.append(f"  - {cycle['description']}")
        
        # 孤立依赖
        if analysis_result['orphaned_dependencies']:
            lines.append(f"\n孤立依赖: {len(analysis_result['orphaned_dependencies'])}")
            for orphan in analysis_result['orphaned_dependencies']:
                lines.append(f"  - {orphan}")
        
        return "\n".join(lines)
    
    def _generate_dot_graph(self, analysis_result):
        """生成Graphviz DOT格式的依赖图"""
        lines = []
        lines.append("digraph dependencies {")
        lines.append("  rankdir=LR;")
        lines.append("  node [shape=box];")
        
        # 添加包节点
        package = analysis_result['package']
        lines.append(f'  "{package}" [style=filled, fillcolor=lightblue];')
        
        # 添加依赖关系
        for level, deps in analysis_result['dependency_graph'].items():
            for dep in deps:
                lines.append(f'  "{level}" -> "{dep}";')
        
        lines.append("}")
        return "\n".join(lines)
    
    def compare_dependency_changes(self, before_packages, after_packages):
        """比较包依赖变化"""
        changes = {
            'new_dependencies': [],
            'removed_dependencies': [],
            'dependency_updates': []
        }
        
        # 比较每个包的依赖变化
        for package_name in set(before_packages.keys()) | set(after_packages.keys()):
            before_deps = self._get_direct_dependencies(package_name) if package_name in before_packages else []
            after_deps = self._get_direct_dependencies(package_name) if package_name in after_packages else []
            
            before_names = {d['name'] for d in before_deps}
            after_names = {d['name'] for d in after_deps}
            
            # 新增依赖
            new_deps = after_names - before_names
            if new_deps:
                changes['new_dependencies'].append({
                    'package': package_name,
                    'dependencies': list(new_deps)
                })
            
            # 移除依赖
            removed_deps = before_names - after_names
            if removed_deps:
                changes['removed_dependencies'].append({
                    'package': package_name,
                    'dependencies': list(removed_deps)
                })
        
        return changes