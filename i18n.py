#!/usr/bin/env python3
"""
国际化（i18n）支持模块
支持中文（zh）和英文（en）
"""

import os

class I18n:
    """国际化翻译类"""
    
    # 翻译字典
    TRANSLATIONS = {
        'zh': {
            # 报告标题
            'report_title': '智能摄影学习助手',
            'report_subtitle': '专业照片分析报告',
            'generated_time': '生成时间',
            
            # 章节标题
            'basic_info': '基础信息',
            'six_dimensions': '六维评分',
            'color_analysis': '色彩美学分析',
            'emotion_analysis': '情感分析',
            'learning_suggestions': '学习建议',
            'practice_plan': '个性化练习方案',
            
            # 基础信息字段
            'resolution': '分辨率',
            'aspect_ratio': '长宽比',
            'orientation_landscape': '横拍',
            'orientation_portrait': '竖拍',
            'orientation_square': '方形',
            'average_brightness': '平均亮度',
            'contrast': '对比度',
            
            # 六维度名称
            'composition': '构图',
            'lighting': '光影',
            'color': '色彩',
            'creativity': '创意',
            'technique': '技术',
            'emotion': '情绪',
            
            # 色彩分析
            'dominant_colors': '主要色彩',
            'color_harmony': '色彩和谐度',
            'harmony_type': '类型',
            'description': '描述',
            'aesthetics_score': '美学综合评分',
            'color_psychology': '色彩心理学',
            'emotional_tendency': '情感倾向',
            'psychology_score': '心理学评分',
            
            # 色彩和谐类型
            'harmony_monochromatic': '单色系：和谐统一，但可能略显单调',
            'harmony_monochromatic_theory': '单色系：使用同一色相，通过改变亮度和饱和度创造和谐',
            'harmony_analogous': '类似色系：和谐统一，有一定变化',
            'harmony_analogous_theory': '类似色系：使用色相环上相邻的颜色，创造和谐且有变化的视觉效果',
            'harmony_complementary': '互补色系：对比强烈，视觉冲击力强',
            'harmony_complementary_theory': '互补色系：使用色相环上相对的颜色，创造强烈的视觉对比',
            'harmony_split_complementary': '分裂互补色系：对比适中，和谐与冲击力平衡',
            'harmony_split_complementary_theory': '分裂互补色系：使用一个颜色的互补色两侧的相邻色，创造平衡的对比',
            'harmony_triadic': '三分色系：色彩丰富，活力强',
            'harmony_triadic_theory': '三分色系：使用色相环上等距的三个颜色，创造丰富的视觉效果',
            
            # 色温描述
            'temp_warm': '暖色调：传递温暖、活力、激情',
            'temp_cool': '冷色调：传递冷静、理性、忧郁',
            'temp_neutral': '中性色调：传递平和、专业、沉稳',
            
            # 强度描述
            'intensity_high': '高饱和度：色彩鲜艳，视觉冲击力强',
            'intensity_medium': '中等饱和度：色彩适中，视觉舒适',
            'intensity_low': '低饱和度：色彩柔和，视觉舒适',
            
            # 情感关键词（色彩心理学）
            'emotion_热情': '热情',
            'emotion_活力': '活力',
            'emotion_激情': '激情',
            'emotion_危险': '危险',
            'emotion_爱': '爱',
            'emotion_温暖': '温暖',
            'emotion_友好': '友好',
            'emotion_创意': '创意',
            'emotion_快乐': '快乐',
            'emotion_乐观': '乐观',
            'emotion_注意': '注意',
            'emotion_自然': '自然',
            'emotion_平静': '平静',
            'emotion_成长': '成长',
            'emotion_健康': '健康',
            'emotion_信任': '信任',
            'emotion_专业': '专业',
            'emotion_忧郁': '忧郁',
            'emotion_神秘': '神秘',
            'emotion_高贵': '高贵',
            'emotion_浪漫': '浪漫',
            'emotion_温柔': '温柔',
            'emotion_甜美': '甜美',
            'emotion_力量': '力量',
            'emotion_优雅': '优雅',
            'emotion_悲伤': '悲伤',
            'emotion_纯净': '纯净',
            'emotion_简洁': '简洁',
            'emotion_和平': '和平',
            'emotion_中性': '中性',
            'emotion_沉稳': '沉稳',
            
            # 学习建议
            'focus_area': '重点关注',
            'need_improvement': '需要提升',
            'excellent_level': '优秀水平',
            'current_issue': '当前问题',
            'improvement_suggestions': '改进建议',
            'reference_resources': '参考资源',
            'current_level': '当前水平',
            'advanced_suggestions': '进阶建议',
            
            # 练习方案
            'practice_intro': '根据你的当前水平，我们为你制定了以下练习计划：',
            'short_term': '短期练习（1-2周）',
            'medium_term': '中期练习（1个月）',
            'long_term': '长期目标（3个月）',
            'task': '任务',
            'completion_standard': '完成标准',
            'practice_tips': '练习建议',
            'frequency_suggestion': '频率建议',
            'feedback_method': '反馈方式',
            'remember': '记住：持续练习和反思是提升的关键！',
            
            # 短期练习任务
            'task1_title': '任务1：构图练习',
            'task1_content': '''• 每天拍摄10张照片，刻意运用三分法构图
• 选择不同的主体（人物、建筑、风景等）
• 完成标准：能够快速识别并运用三分法''',
            'task2_title': '任务2：光线观察',
            'task2_content': '''• 同一场景在不同时间拍摄（早、中、晚）
• 记录光线变化对画面的影响
• 完成标准：能够预判光线效果''',
            
            # 中期练习任务
            'task3_title': '任务3：主题创作',
            'task3_content': '''• 选择一个主题（如"城市夜景"、"人物情感"）
• 围绕主题拍摄30-50张作品
• 完成标准：形成自己的拍摄思路和风格''',
            'task4_title': '任务4：后期学习',
            'task4_content': '''• 学习基础的后期调色技巧
• 每周精修2-3张照片
• 完成标准：掌握曝光、色彩、锐度等基础调整''',
            
            # 长期练习任务
            'task5_title': '任务5：风格探索',
            'task5_content': '''• 尝试不同的摄影风格（纪实、艺术、商业等）
• 模仿3-5位喜欢的摄影师作品
• 完成标准：找到自己的风格方向''',
            'task6_title': '任务6：作品集整理',
            'task6_content': '''• 从过去作品中精选20-30张
• 整理成完整的作品集
• 完成标准：能够清晰表达自己的摄影理念''',
            
            # 练习建议详情
            'frequency_details': '''• 每天至少拍摄10-15分钟
• 每周整理和回顾作品1-2次
• 每月与他人交流学习心得1次''',
            'feedback_details': '''• 定期上传作品到本系统进行分析
• 加入摄影社群，获得更多反馈
• 记录学习笔记，总结进步和不足''',
            
            # 具体建议内容
            'composition_improvement': '构图改进',
            'composition_issue': '构图还有提升空间',
            'composition_suggestions': '''
                <li>学习并运用三分法则，将主体放在画面的黄金分割点上</li>
                <li>注意画面的平衡感，避免一侧过重</li>
                <li>尝试不同的拍摄角度，如低角度、高角度或平视角度</li>
                <li>利用引导线引导观众视线到主体</li>
            ''',
            'lighting_control': '光影控制',
            'lighting_issue': '光影处理需要加强',
            'lighting_suggestions': '''
                <li>学习识别不同的光线类型（自然光、人工光、散射光等）</li>
                <li>掌握黄金时段拍摄（日出后、日落前的柔和光线）</li>
                <li>练习使用反光板或补光设备改善光影效果</li>
                <li>理解光线的方向性对主体的影响</li>
            ''',
            'color_usage': '色彩运用',
            'color_issue': '色彩美学可以更进一步',
            'color_suggestions': '''
                <li>学习色彩理论，理解互补色、类似色的运用</li>
                <li>注意画面的色彩和谐度，避免色彩过于杂乱</li>
                <li>练习后期调色，提升色彩的表现力</li>
                <li>尝试不同的色调风格（冷色调、暖色调、黑白等）</li>
            ''',
            'advanced_improvement': '进阶提升',
            'excellent_foundation': '你的基础功底已经很扎实了！',
            'advanced_suggestions': '''
                <li>尝试拍摄更具挑战性的题材（如夜景、运动、人像等）</li>
                <li>学习更高级的后期处理技巧</li>
                <li>培养自己独特的摄影风格和视角</li>
                <li>多观摩大师作品，提升审美和创意</li>
                <li>尝试参加摄影比赛或展览，获得更多反馈</li>
            ''',
            
            # 页脚
            'footer_tech': '基于 PIL、NumPy、scikit-image 和 InternLM AI',
            'footer_tip': '更多摄影知识请参考 photo-tutor/references/ 目录',
            
            # 亮度级别
            'very_dark': '非常暗',
            'dark': '暗',
            'normal': '正常',
            'bright': '亮',
            'very_bright': '非常亮',
            
            # 对比度级别
            'very_low': '非常低',
            'low': '低',
            'medium': '中等',
            'high': '高',
            'very_high': '非常高',
        },
        
        'en': {
            # Report title
            'report_title': 'Smart Photography Learning Assistant',
            'report_subtitle': 'Professional Photo Analysis Report',
            'generated_time': 'Generated at',
            
            # Section titles
            'basic_info': 'Basic Information',
            'six_dimensions': 'Six-Dimension Scores',
            'color_analysis': 'Color Aesthetics Analysis',
            'emotion_analysis': 'Emotional Analysis',
            'learning_suggestions': 'Learning Suggestions',
            'practice_plan': 'Personalized Practice Plan',
            
            # Basic info fields
            'resolution': 'Resolution',
            'aspect_ratio': 'Aspect Ratio',
            'orientation_landscape': 'Landscape',
            'orientation_portrait': 'Portrait',
            'orientation_square': 'Square',
            'average_brightness': 'Average Brightness',
            'contrast': 'Contrast',
            
            # Six dimensions
            'composition': 'Composition',
            'lighting': 'Lighting',
            'color': 'Color',
            'creativity': 'Creativity',
            'technique': 'Technique',
            'emotion': 'Emotion',
            
            # Color analysis
            'dominant_colors': 'Dominant Colors',
            'color_harmony': 'Color Harmony',
            'harmony_type': 'Type',
            'description': 'Description',
            'aesthetics_score': 'Aesthetics Score',
            'color_psychology': 'Color Psychology',
            'emotional_tendency': 'Emotional Tendency',
            'psychology_score': 'Psychology Score',
            
            # Color harmony types
            'harmony_monochromatic': 'Monochromatic: Harmonious and unified, but may be slightly monotonous',
            'harmony_monochromatic_theory': 'Monochromatic: Using the same hue, creating harmony by changing brightness and saturation',
            'harmony_analogous': 'Analogous: Harmonious and unified with variation',
            'harmony_analogous_theory': 'Analogous: Using adjacent colors on the color wheel, creating harmonious and varied visual effects',
            'harmony_complementary': 'Complementary: Strong contrast, powerful visual impact',
            'harmony_complementary_theory': 'Complementary: Using opposite colors on the color wheel, creating strong visual contrast',
            'harmony_split_complementary': 'Split-Complementary: Moderate contrast, balanced harmony and impact',
            'harmony_split_complementary_theory': 'Split-Complementary: Using colors adjacent to the complement, creating balanced contrast',
            'harmony_triadic': 'Triadic: Rich colors, strong vitality',
            'harmony_triadic_theory': 'Triadic: Using three evenly spaced colors on the color wheel, creating rich visual effects',
            
            # Temperature descriptions
            'temp_warm': 'Warm Tone: Conveys warmth, vitality, and passion',
            'temp_cool': 'Cool Tone: Conveys calmness, rationality, and melancholy',
            'temp_neutral': 'Neutral Tone: Conveys peace, professionalism, and stability',
            
            # Intensity descriptions
            'intensity_high': 'High Saturation: Vivid colors, strong visual impact',
            'intensity_medium': 'Medium Saturation: Moderate colors, visually comfortable',
            'intensity_low': 'Low Saturation: Soft colors, visually comfortable',
            
            # Emotion keywords (color psychology)
            'emotion_热情': 'Passion',
            'emotion_活力': 'Vitality',
            'emotion_激情': 'Fervor',
            'emotion_危险': 'Danger',
            'emotion_爱': 'Love',
            'emotion_温暖': 'Warmth',
            'emotion_友好': 'Friendliness',
            'emotion_创意': 'Creativity',
            'emotion_快乐': 'Joy',
            'emotion_乐观': 'Optimism',
            'emotion_注意': 'Attention',
            'emotion_自然': 'Nature',
            'emotion_平静': 'Calmness',
            'emotion_成长': 'Growth',
            'emotion_健康': 'Health',
            'emotion_信任': 'Trust',
            'emotion_专业': 'Professionalism',
            'emotion_忧郁': 'Melancholy',
            'emotion_神秘': 'Mystery',
            'emotion_高贵': 'Nobility',
            'emotion_浪漫': 'Romance',
            'emotion_温柔': 'Tenderness',
            'emotion_甜美': 'Sweetness',
            'emotion_力量': 'Power',
            'emotion_优雅': 'Elegance',
            'emotion_悲伤': 'Sadness',
            'emotion_纯净': 'Purity',
            'emotion_简洁': 'Simplicity',
            'emotion_和平': 'Peace',
            'emotion_中性': 'Neutrality',
            'emotion_沉稳': 'Composure',
            
            # Learning suggestions
            'focus_area': 'Focus Area',
            'need_improvement': 'Need Improvement',
            'excellent_level': 'Excellent Level',
            'current_issue': 'Current Issue',
            'improvement_suggestions': 'Improvement Suggestions',
            'reference_resources': 'Reference Resources',
            'current_level': 'Current Level',
            'advanced_suggestions': 'Advanced Suggestions',
            
            # Practice plan
            'practice_intro': 'Based on your current level, we have created the following practice plan:',
            'short_term': 'Short-term Practice (1-2 weeks)',
            'medium_term': 'Medium-term Practice (1 month)',
            'long_term': 'Long-term Goals (3 months)',
            'task': 'Task',
            'completion_standard': 'Completion Standard',
            'practice_tips': 'Practice Tips',
            'frequency_suggestion': 'Frequency Suggestion',
            'feedback_method': 'Feedback Method',
            'remember': 'Remember: Consistent practice and reflection are the keys to improvement!',
            
            # Short-term tasks
            'task1_title': 'Task 1: Composition Practice',
            'task1_content': '''• Take 10 photos daily, deliberately applying the rule of thirds
• Choose different subjects (people, architecture, landscapes, etc.)
• Completion standard: Quickly identify and apply the rule of thirds''',
            'task2_title': 'Task 2: Light Observation',
            'task2_content': '''• Shoot the same scene at different times (morning, noon, evening)
• Record how light changes affect the image
• Completion standard: Predict lighting effects''',
            
            # Medium-term tasks
            'task3_title': 'Task 3: Thematic Creation',
            'task3_content': '''• Choose a theme (e.g., "City Nightscape", "Human Emotions")
• Shoot 30-50 works around the theme
• Completion standard: Develop your own shooting approach and style''',
            'task4_title': 'Task 4: Post-Processing Learning',
            'task4_content': '''• Learn basic color grading techniques
• Fine-tune 2-3 photos weekly
• Completion standard: Master exposure, color, sharpness adjustments''',
            
            # Long-term tasks
            'task5_title': 'Task 5: Style Exploration',
            'task5_content': '''• Try different photography styles (documentary, artistic, commercial, etc.)
• Imitate 3-5 favorite photographers' works
• Completion standard: Find your own style direction''',
            'task6_title': 'Task 6: Portfolio Organization',
            'task6_content': '''• Select 20-30 photos from past works
• Organize into a complete portfolio
• Completion standard: Clearly express your photography philosophy''',
            
            # Practice tips details
            'frequency_details': '''• Shoot for at least 10-15 minutes daily
• Review and organize works 1-2 times weekly
• Exchange learning experiences with others once a month''',
            'feedback_details': '''• Regularly upload works to this system for analysis
• Join photography communities for more feedback
• Keep learning notes, summarize progress and shortcomings''',
            
            # Specific suggestions
            'composition_improvement': 'Composition Improvement',
            'composition_issue': 'Composition has room for improvement',
            'composition_suggestions': '''
                <li>Learn and apply the rule of thirds, placing subjects at golden ratio points</li>
                <li>Pay attention to visual balance, avoid one-sided composition</li>
                <li>Try different shooting angles like low angle, high angle or eye level</li>
                <li>Use leading lines to guide viewer's attention to the subject</li>
            ''',
            'lighting_control': 'Lighting Control',
            'lighting_issue': 'Lighting needs enhancement',
            'lighting_suggestions': '''
                <li>Learn to identify different light types (natural, artificial, diffused light, etc.)</li>
                <li>Master golden hour shooting (soft light after sunrise, before sunset)</li>
                <li>Practice using reflectors or fill lights to improve lighting</li>
                <li>Understand how light direction affects the subject</li>
            ''',
            'color_usage': 'Color Usage',
            'color_issue': 'Color aesthetics can be improved',
            'color_suggestions': '''
                <li>Learn color theory, understand complementary and analogous colors</li>
                <li>Pay attention to color harmony, avoid chaotic colors</li>
                <li>Practice post-processing to enhance color expression</li>
                <li>Try different color styles (cool, warm, black & white, etc.)</li>
            ''',
            'advanced_improvement': 'Advanced Improvement',
            'excellent_foundation': 'Your foundation is already solid!',
            'advanced_suggestions': '''
                <li>Try more challenging subjects (night scenes, sports, portraits, etc.)</li>
                <li>Learn advanced post-processing techniques</li>
                <li>Develop your unique photography style and perspective</li>
                <li>Study masterworks to improve aesthetics and creativity</li>
                <li>Join photography competitions or exhibitions for more feedback</li>
            ''',
            
            # Footer
            'footer_tech': 'Based on PIL, NumPy, scikit-image and InternLM AI',
            'footer_tip': 'More photography knowledge in photo-tutor/references/ directory',
            
            # Brightness levels
            'very_dark': 'Very Dark',
            'dark': 'Dark',
            'normal': 'Normal',
            'bright': 'Bright',
            'very_bright': 'Very Bright',
            
            # Contrast levels
            'very_low': 'Very Low',
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'very_high': 'Very High',
        }
    }
    
    def __init__(self, lang='zh'):
        """
        初始化
        
        Args:
            lang: 语言代码，'zh' 或 'en'，默认从环境变量 LANG 读取
        """
        # 从环境变量读取语言设置
        env_lang = os.getenv('PHOTO_AI_LANG', lang)
        self.lang = env_lang if env_lang in ['zh', 'en'] else 'zh'
    
    def t(self, key, default=None):
        """
        翻译函数
        
        Args:
            key: 翻译键
            default: 默认值（如果翻译不存在）
            
        Returns:
            翻译后的文本
        """
        translations = self.TRANSLATIONS.get(self.lang, self.TRANSLATIONS['zh'])
        return translations.get(key, default or key)
    
    def set_lang(self, lang):
        """设置语言"""
        if lang in ['zh', 'en']:
            self.lang = lang
    
    def get_lang(self):
        """获取当前语言"""
        return self.lang


# 全局实例
_i18n = None

def get_i18n(lang=None):
    """获取国际化实例"""
    global _i18n
    if _i18n is None or (lang and lang != _i18n.get_lang()):
        _i18n = I18n(lang or os.getenv('PHOTO_AI_LANG', 'zh'))
    return _i18n


def t(key, default=None, lang=None):
    """翻译快捷函数"""
    i18n = get_i18n(lang)
    return i18n.t(key, default)
