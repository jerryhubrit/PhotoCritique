#!/usr/bin/env python3
"""
分析报告格式化工具
功能：将智能体生成的分析内容格式化为标准报告
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List


class PhotoAnalysisReport:
    """照片分析报告类"""
    
    def __init__(self, photo_info: Dict[str, Any] = None):
        """
        初始化报告
        
        Args:
            photo_info: 照片基础信息（从photo_analyzer.py获取）
        """
        self.photo_info = photo_info or {}
        self.analysis = {}
        self.scores = {}
        self.suggestions = []
        self.practice_plan = {}
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def set_analysis(self, category: str, content: str):
        """
        设置分析内容
        
        Args:
            category: 分析类别（如composition, lighting, color等）
            content: 分析内容
        """
        self.analysis[category] = content
    
    def set_scores(self, scores: Dict[str, int]):
        """
        设置评分
        
        Args:
            scores: 评分字典，如 {'composition': 85, 'lighting': 75}
        """
        self.scores = scores
        self.scores['overall'] = round(sum(scores.values()) / len(scores), 1)
    
    def add_suggestion(self, priority: str, suggestion: str):
        """
        添加建议
        
        Args:
            priority: 优先级（high/medium/low）
            suggestion: 建议内容
        """
        self.suggestions.append({
            'priority': priority,
            'content': suggestion
        })
    
    def set_practice_plan(self, plan: Dict[str, Any]):
        """
        设置练习方案
        
        Args:
            plan: 练习方案字典
        """
        self.practice_plan = plan
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            完整的报告字典
        """
        return {
            'photo_info': self.photo_info,
            'analysis': self.analysis,
            'scores': self.scores,
            'suggestions': self.suggestions,
            'practice_plan': self.practice_plan,
            'created_at': self.created_at
        }
    
    def to_markdown(self) -> str:
        """
        转换为Markdown格式
        
        Returns:
            Markdown格式的报告
        """
        md = []
        
        # 标题
        md.append("# 📷 摄影学习分析报告\n")
        md.append(f"**生成时间**: {self.created_at}\n")
        
        # 照片信息
        if self.photo_info:
            md.append("## 📸 照片信息")
            md.append(f"- **文件名**: {self.photo_info.get('file_name', 'N/A')}")
            md.append(f"- **分辨率**: {self.photo_info.get('resolution', 'N/A')}")
            md.append(f"- **格式**: {self.photo_info.get('format', 'N/A')}")
            
            if 'aperture' in self.photo_info:
                md.append(f"- **光圈**: {self.photo_info['aperture']}")
            if 'shutter_speed' in self.photo_info:
                md.append(f"- **快门**: {self.photo_info['shutter_speed']}")
            if 'iso' in self.photo_info:
                md.append(f"- **ISO**: {self.photo_info['iso']}")
            
            md.append("")
        
        # 评分
        if self.scores:
            md.append("## 📊 评分")
            for category, score in self.scores.items():
                emoji = "⭐" * int(score / 20)
                md.append(f"- **{category.upper()}**: {score}/100 {emoji}")
            md.append("")
        
        # 分析
        if self.analysis:
            md.append("## 🔍 详细分析")
            for category, content in self.analysis.items():
                md.append(f"### {category.capitalize()}")
                md.append(content)
                md.append("")
        
        # 建议
        if self.suggestions:
            md.append("## 💡 改进建议")
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            sorted_suggestions = sorted(self.suggestions, key=lambda x: priority_order.get(x['priority'], 3))
            
            for s in sorted_suggestions:
                emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(s['priority'], '⚪')
                md.append(f"{emoji} **[{s['priority'].upper()}]** {s['content']}")
            md.append("")
        
        # 练习方案
        if self.practice_plan:
            md.append("## 📋 定制化练习方案")
            
            if 'goals' in self.practice_plan:
                md.append("### 学习目标")
                for i, goal in enumerate(self.practice_plan['goals'], 1):
                    md.append(f"{i}. {goal}")
                md.append("")
            
            if 'tasks' in self.practice_plan:
                md.append("### 练习任务")
                for i, task in enumerate(self.practice_plan['tasks'], 1):
                    task_desc = task.get('description', '未描述')
                    task_duration = task.get('duration', '待定')
                    task_criteria = task.get('criteria', '待定义')
                    md.append(f"**任务{i}**: {task_desc}")
                    md.append(f"- 建议时长: {task_duration}")
                    md.append(f"- 完成标准: {task_criteria}")
                    md.append("")
        
        # 结语
        md.append("---")
        md.append("\n*本报告由智能摄影学习助手生成，仅供参考。持续练习是摄影进步的关键！*")
        
        return "\n".join(md)
    
    def to_json(self) -> str:
        """
        转换为JSON格式
        
        Returns:
            JSON格式的报告
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def save_to_file(self, filepath: str, format: str = 'markdown'):
        """
        保存报告到文件
        
        Args:
            filepath: 文件路径
            format: 输出格式（markdown/json）
        """
        try:
            if format == 'markdown':
                content = self.to_markdown()
                ext = '.md'
            elif format == 'json':
                content = self.to_json()
                ext = '.json'
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            # 确保文件扩展名正确
            if not filepath.endswith(ext):
                filepath += ext
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"报告已保存到: {filepath}")
            
        except Exception as e:
            print(f"保存报告失败: {str(e)}", file=sys.stderr)
            raise


def create_template_report() -> PhotoAnalysisReport:
    """
    创建模板报告（用于示例）
    
    Returns:
        示例报告对象
    """
    report = PhotoAnalysisReport({
        'file_name': 'example.jpg',
        'resolution': '1920x1080',
        'format': 'JPEG'
    })
    
    # 设置分析
    report.set_analysis('composition', '照片采用了经典的三分法构图，主体位于画面右侧三分之一处。地平线保持在下方三分之一线上，增加了天空的比重，营造出广阔的空间感。')
    report.set_analysis('lighting', '光线来自右侧侧方，形成了良好的立体感和层次感。阴影部分细节保留完整，没有出现死黑。')
    
    # 设置评分
    report.set_scores({
        'composition': 85,
        'lighting': 80,
        'color': 75,
        'creativity': 70,
        'technique': 80
    })
    
    # 添加建议
    report.add_suggestion('high', '尝试在黄金时段（日出后或日落前）拍摄，获得更柔和的光线')
    report.add_suggestion('medium', '注意前景元素的运用，增加照片的纵深感')
    report.add_suggestion('low', '尝试不同的构图角度，如低角度仰拍或高角度俯拍')
    
    # 设置练习方案
    report.set_practice_plan({
        'goals': [
            '掌握三分法构图的灵活运用',
            '学会利用光线营造氛围'
        ],
        'tasks': [
            {
                'description': '拍摄至少20张使用三分法构图的照片',
                'duration': '1周',
                'criteria': '主体清晰位于三分线交点处，画面平衡'
            },
            {
                'description': '在不同光线条件下拍摄同一场景',
                'duration': '3天',
                'criteria': '记录光线变化对照片氛围的影响'
            }
        ]
    })
    
    return report


def main():
    """
    主函数：命令行接口
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='分析报告格式化工具')
    parser.add_argument('--template', action='store_true', help='生成模板报告')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['markdown', 'json'], default='markdown', help='输出格式')
    
    args = parser.parse_args()
    
    try:
        if args.template:
            report = create_template_report()
        else:
            # 交互式创建报告（实际使用时从智能体获取数据）
            print("请通过编程方式使用此工具")
            return
        
        if args.output:
            report.save_to_file(args.output, args.format)
        else:
            if args.format == 'markdown':
                print(report.to_markdown())
            else:
                print(report.to_json())
                
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
