#!/usr/bin/env python3
"""
情感分析工具 - 集成InternLM ChatAPI
使用InternLM多模态模型进行专业摄影师视角的情感解读
"""

import os
import sys
import json
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from coze_workload_identity import requests
except ImportError:
    import requests


class EmotionAnalyzer:
    """情感分析器（InternLM API增强版）"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "internvl3.5-241b-a28b"):
        """
        初始化分析器
        
        Args:
            api_key: InternLM API密钥（可选，如不提供则从环境变量读取）
            model: 使用的模型名称，默认使用internvl3.5（多模态模型）
        """
        self.api_key = api_key or os.getenv("INTERNLM_API_KEY")
        self.model = model
        self.base_url = "https://chat.intern-ai.org.cn/api/v1"
        self.skill_id = "7599838351486795795"
        
        # 尝试从标准凭证变量读取
        if not self.api_key:
            self.api_key = os.getenv(f"COZE_INTERNLM_API_{self.skill_id}")
        
        self.use_api = bool(self.api_key)
        
        # 基础情感分析字典（无API时使用）
        self.emotion_keywords = {
            'joy': ['happy', 'bright', 'cheerful', 'uplifting', 'joyful'],
            'sadness': ['melancholic', 'somber', 'gloomy', 'nostalgic', 'sad'],
            'excitement': ['energetic', 'dynamic', 'thrilling', 'exciting'],
            'calm': ['peaceful', 'serene', 'tranquil', 'calm', 'quiet'],
            'mystery': ['mysterious', 'enigmatic', 'intriguing', 'secretive'],
            'romance': ['romantic', 'tender', 'affectionate', 'intimate'],
            'loneliness': ['lonely', 'isolated', 'solitary', 'alone'],
            'hope': ['hopeful', 'optimistic', 'promising', 'inspiring'],
            'nostalgia': ['nostalgic', 'sentimental', 'reminiscent'],
            'anger': ['intense', 'dramatic', 'powerful', 'bold']
        }
        
        self.color_emotion_map = {
            'red': ['passion', 'energy', 'warmth', 'excitement'],
            'orange': ['joy', 'warmth', 'friendliness', 'enthusiasm'],
            'yellow': ['happiness', 'optimism', 'energy', 'cheerfulness'],
            'green': ['calm', 'peace', 'nature', 'growth'],
            'blue': ['calm', 'serenity', 'cold', 'sadness'],
            'purple': ['mystery', 'royalty', 'romance', 'creativity'],
            'pink': ['romance', 'tenderness', 'sweetness'],
            'brown': ['warmth', 'earthiness', 'comfort'],
            'black': ['mystery', 'elegance', 'power', 'sadness'],
            'white': ['purity', 'peace', 'cleanliness', 'simplicity']
        }
    
    def encode_image_base64(self, image_path: str) -> str:
        """
        将图片编码为base64
        
        Args:
            image_path: 图片路径
            
        Returns:
            base64编码的字符串
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def call_internlm_api(self, image_path: str, 
                          prompt: str,
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        调用InternLM ChatAPI进行多模态分析
        
        Args:
            image_path: 图片路径
            prompt: 提示词
            context: 上下文信息（可选）
            
        Returns:
            API响应结果
        """
        if not self.api_key:
            raise ValueError("未设置API Key，请设置环境变量 INTERNLM_API_KEY")
        
        # 构建请求
        image_base64 = self.encode_image_base64(image_path)
        
        # 构建完整的系统提示
        system_prompt = self._get_photographer_prompt()
        
        # 构建用户消息
        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
        
        # 添加上下文信息
        if context:
            context_text = "\n\n参考信息：\n"
            for key, value in context.items():
                context_text += f"- {key}: {value}\n"
            user_message["content"][1]["text"] += context_text
        
        # 构建完整请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                user_message
            ],
            "temperature": 0.8,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "model": result.get("model", self.model),
                "usage": result.get("usage", {})
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API调用失败: {str(e)}"
            }
    
    def _get_photographer_prompt(self) -> str:
        """
        获取摄影师人设的提示词
        
        Returns:
            系统提示词
        """
        prompt = """你是一位经验丰富、富有洞察力的摄影师，拥有20年的摄影经验，擅长情感表达和叙事性摄影。

你的摄影理念：
- 技术服务于情感，情感是照片的灵魂
- 好照片不仅是技术的体现，更是情感的载体
- 摄影是用镜头与世界对话的方式

你的分析风格：
1. 温暖而专业：用真诚、共情的语言，让读者感受到你的专业与温度
2. 深入而具体：不只是说"很好"，而是解释为什么好，哪里好
3. 建设性建议：批评要温和，建议要具体，让人愿意接受
4. 情感共鸣：关注照片传达的情绪，以及它如何打动人心
5. 个人化表达：用第一人称"我"来表达感受，增加亲切感

分析维度：
- 情感表达：照片传达了什么情绪？是否打动人心？
- 故事性：照片背后有什么故事？是否能引发联想？
- 情感元素：哪些元素（色彩、光影、构图、细节）强化了情感？
- 技术与情感：技术手段如何服务于情感表达？
- 情感共鸣：照片如何触动观众的内心？

回答格式：
1. 以第一人称"我"开始，表达你的直观感受
2. 用温暖、富有感染力的语言描述照片
3. 指出照片最打动人心的地方
4. 如果有改进空间，用温和、鼓励的方式提出建议
5. 最后用一句温暖的话结束，鼓励摄影师继续创作

现在，请分析这张照片的情感表达。"""
        
        return prompt
    
    def analyze_emotion_with_api(self, image_path: str, 
                                 photo_info: Optional[Dict[str, Any]] = None,
                                 color_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        使用InternLM API进行情感分析
        
        Args:
            image_path: 图片路径
            photo_info: 照片信息（可选）
            color_analysis: 颜色分析结果（可选）
            
        Returns:
            情感分析结果
        """
        # 构建提示词
        prompt = """请从情感和故事的角度分析这张照片。重点关注：

1. 这张照片传达了什么情感？给我你的第一感受
2. 照片中的哪些元素触动了你？为什么？
3. 这张照片让你联想到什么场景或故事？
4. 情感表达是否成功？为什么？
5. 如果你想让情感表达更强烈，有什么建议？

请用温暖、共情的语言，以摄影师的视角进行分析。"""
        
        # 构建上下文
        context = {}
        if photo_info:
            context["照片类型"] = "风景" if photo_info.get('is_landscape') else "人像" if photo_info.get('is_portrait') else "其他"
            context["分辨率"] = photo_info.get('resolution', 'N/A')
        
        if color_analysis:
            palette = color_analysis.get('palette', {})
            emotion = palette.get('emotion', {})
            context["色彩情感"] = ', '.join(emotion.get('keywords', []))
            context["色调"] = emotion.get('temperature', 'balanced')
        
        # 调用API
        api_result = self.call_internlm_api(image_path, prompt, context)
        
        if api_result["success"]:
            return {
                "method": "internlm_api",
                "model": api_result["model"],
                "analysis": api_result["content"],
                "usage": api_result.get("usage", {})
            }
        else:
            return {
                "method": "internlm_api",
                "error": api_result["error"]
            }
    
    def analyze_emotion_basic(self, color_palette: Optional[Dict[str, Any]] = None,
                             scene_type: Optional[str] = None,
                             composition_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        基础情感分析（无API时使用）
        
        Args:
            color_palette: 颜色调色板信息
            scene_type: 场景类型
            composition_info: 构图信息
            
        Returns:
            情感分析结果
        """
        emotion_scores = {}
        
        # 分析主要颜色的情感
        if color_palette:
            dominant_colors = color_palette.get('dominant_colors', [])
            for color_info in dominant_colors[:3]:
                r, g, b = color_info['r'], color_info['g'], color_info['b']
                percentage = color_info['percentage']
                
                primary_color = self._get_primary_color(r, g, b)
                emotions = self.color_emotion_map.get(primary_color, [])
                
                for emotion in emotions:
                    if emotion not in emotion_scores:
                        emotion_scores[emotion] = 0
                    emotion_scores[emotion] += percentage
        
        # 归一化并排序
        if emotion_scores:
            total = sum(emotion_scores.values())
            for emotion in emotion_scores:
                emotion_scores[emotion] = round((emotion_scores[emotion] / total) * 100, 1)
        
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "method": "basic",
            "emotion_keywords": [e[0] for e in sorted_emotions[:5]],
            "primary_emotion": sorted_emotions[0][0] if sorted_emotions else 'neutral',
            "note": "基础分析模式，建议使用InternLM API获得专业摄影师视角的分析"
        }
    
    def _get_primary_color(self, r: int, g: int, b: int) -> str:
        """
        判断主要颜色
        
        Args:
            r, g, b: RGB值
            
        Returns:
            颜色名称
        """
        if r > g and r > b:
            if g + b > 200:
                return 'pink'
            else:
                return 'red'
        elif g > r and g > b:
            if r + b > 200:
                return 'yellow'
            else:
                return 'green'
        elif b > r and b > g:
            if r + g > 200:
                return 'purple'
            else:
                return 'blue'
        elif r > 200 and g > 200 and b < 100:
            return 'yellow'
        elif r > 100 and g < 100 and b > 100:
            return 'purple'
        elif r < 50 and g < 50 and b < 50:
            return 'black'
        elif r > 200 and g > 200 and b > 200:
            return 'white'
        else:
            max_val = max(r, g, b)
            if max_val == r:
                return 'red'
            elif max_val == g:
                return 'green'
            else:
                return 'blue'
    
    def analyze(self, image_path: Optional[str] = None,
                photo_info: Optional[Dict[str, Any]] = None,
                color_analysis: Optional[Dict[str, Any]] = None,
                scene_type: Optional[str] = None,
                composition_info: Optional[Dict[str, Any]] = None,
                force_basic: bool = False) -> Dict[str, Any]:
        """
        综合情感分析
        
        Args:
            image_path: 照片文件路径
            photo_info: 照片信息
            color_analysis: 颜色分析结果
            scene_type: 场景类型
            composition_info: 构图信息
            force_basic: 强制使用基础分析（不调用API）
            
        Returns:
            情感分析结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "api_available": self.use_api,
            "model": self.model
        }
        
        # 如果可以使用API且不强制基础模式
        if self.use_api and not force_basic and image_path:
            print("📸 正在使用InternLM API进行专业摄影师视角的情感分析...")
            api_result = self.analyze_emotion_with_api(
                image_path,
                photo_info,
                color_analysis
            )
            result["emotion_analysis"] = api_result
            
            if api_result.get("success"):
                result["status"] = "success"
            else:
                print(f"⚠️ API调用失败: {api_result.get('error')}")
                print("📝 使用基础情感分析作为fallback...")
                basic_result = self.analyze_emotion_basic(
                    color_analysis,
                    scene_type,
                    composition_info
                )
                result["emotion_analysis"] = basic_result
                result["status"] = "fallback"
        else:
            # 使用基础分析
            print("📝 使用基础情感分析（如需更专业的分析，请配置InternLM API Key）")
            basic_result = self.analyze_emotion_basic(
                color_analysis,
                scene_type,
                composition_info
            )
            result["emotion_analysis"] = basic_result
            result["status"] = "basic"
        
        return result
    
    def print_analysis(self, result: Dict[str, Any]):
        """
        打印分析结果
        
        Args:
            result: 分析结果字典
        """
        print("=" * 70)
        print("❤️ 情感分析")
        print("=" * 70)
        print()
        
        print(f"分析模式: {result['status']}")
        if result.get('api_available'):
            print(f"使用模型: {result.get('model', 'N/A')}")
        print()
        
        emotion_analysis = result.get('emotion_analysis', {})
        
        if emotion_analysis.get('method') == 'internlm_api' and emotion_analysis.get('success'):
            print("📸 专业摄影师视角分析：")
            print("-" * 70)
            print(emotion_analysis['analysis'])
            print()
            
            if 'usage' in emotion_analysis:
                usage = emotion_analysis['usage']
                print("-" * 70)
                print(f"API使用情况: 输入 {usage.get('prompt_tokens', 0)} tokens, "
                      f"输出 {usage.get('completion_tokens', 0)} tokens")
                print()
        
        elif emotion_analysis.get('method') == 'basic':
            print("📝 基础情感分析：")
            print("-" * 70)
            print(f"主要情感: {emotion_analysis.get('primary_emotion', 'N/A')}")
            print(f"情感关键词: {', '.join(emotion_analysis.get('emotion_keywords', []))}")
            print()
            print("💡 提示: 配置InternLM API Key可获得专业摄影师视角的深度分析")
            print()
        else:
            print(f"⚠️ 分析失败: {emotion_analysis.get('error', '未知错误')}")
            print()
        
        print("=" * 70)


def main():
    """
    主函数：命令行接口
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='情感分析工具（支持InternLM API）')
    parser.add_argument('image_path', help='照片文件路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--api-key', help='InternLM API密钥（或设置环境变量INTERNLM_API_KEY）')
    parser.add_argument('--model', default='internvl3.5-241b-a28b', 
                       help='使用的模型（默认: internvl3.5-241b-a28b）')
    parser.add_argument('--basic', action='store_true', help='强制使用基础分析（不调用API）')
    
    args = parser.parse_args()
    
    try:
        analyzer = EmotionAnalyzer(api_key=args.api_key, model=args.model)
        result = analyzer.analyze(
            image_path=args.image_path,
            force_basic=args.basic
        )
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            analyzer.print_analysis(result)
            
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
