#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Connector for DouBao API using mock responses.
"""

import os
import logging
import tempfile
import random
import time
import json

logger = logging.getLogger(__name__)

# Force development mode since the SDK isn't available
DEV_MODE = True

class DouBaoConnector:
    """Mock connector for ByteDance's DouBao API."""
    
    def __init__(self, config=None):
        """
        Initialize mock DouBao connector.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.api_key = os.environ.get("DOUBAO_API_KEY", "mock_key")
        self.config = config or {}
        
        # Add the missing model_name attribute
        self.model_name = config.get("name", "DouBao") if config else "DouBao"
        
        logger.info(f"DouBao connector initialized in mock mode with model name: {self.model_name}")
    
    def generate(self, prompt, max_tokens=1000, temperature=0.7):
        """
        Generate text (wrapper method).
        
        This method is called by text_generator.py.
        
        Args:
            prompt (str): Input prompt
            max_tokens (int, optional): Maximum tokens to generate
            temperature (float, optional): Sampling temperature
        
        Returns:
            str: Generated text
        """
        return self.generate_text(prompt, max_tokens, temperature)
    
    def generate_text(self, prompt, max_tokens=1000, temperature=0.7):
        """
        Generate mock text response.
        
        Args:
            prompt (str): Input prompt
            max_tokens (int, optional): Maximum tokens to generate
            temperature (float, optional): Sampling temperature
        
        Returns:
            str: Generated text
        """
        logger.info(f"Generating mock text response with {self.model_name}. Prompt length: {len(prompt)}")
        
        # Simulate API delay for realism
        time.sleep(1)
        
        # Create a simple mock response based on keywords in the prompt
        keywords = {
            "meditation": [
                "冥想", "放松", "平静", "呼吸", "专注", "正念", "平和", "内心", "心灵", "意识"
            ],
            "nature": [
                "大自然", "山水", "风景", "树木", "河流", "湖泊", "动物", "花草", "云彩", "星空"
            ],
            "technology": [
                "科技", "创新", "未来", "智能", "数字", "发展", "进步", "应用", "系统", "设备"
            ],
            "education": [
                "教育", "学习", "知识", "学校", "学生", "老师", "课程", "方法", "理解", "思考"
            ],
            "witch": [
                "女巫", "魔法", "巫术", "咒语", "魔药", "神秘", "力量", "自然", "治愈", "智慧"
            ]
        }
        
        # Determine the most relevant category
        category = "general"
        max_matches = 0
        
        # Check for exact keywords in prompt
        lower_prompt = prompt.lower()
        if "witch" in lower_prompt or "女巫" in lower_prompt:
            category = "witch"
        else:
            # Fall back to counting keyword matches
            for cat, words in keywords.items():
                matches = sum(1 for word in words if word in prompt)
                if matches > max_matches:
                    max_matches = matches
                    category = cat
        
        # Generate response based on category
        response = ""
        if category == "witch":
            response = """
            成为一名女巫，意味着与自然和宇宙能量建立深层次的联系。
            
            想象自己站在月光下的森林中，周围环绕着古老的橡树和银色的白桦。
            你的手中握着一根雕刻精美的魔杖，它是从一棵在雷雨中倒下的树上取材制成的。
            
            你学习草药知识，了解每一种植物的特性和用途。你的小屋里挂满了晾干的草药，
            架子上摆放着各种颜色的水晶和魔法书籍。你酿造的魔药能治愈伤痛，带来好运，
            或者保护你爱的人。
            
            作为女巫，你遵循自然的循环和季节的变化，庆祝满月和日月交替。
            你的力量来源于内心的平静和对宇宙规律的理解。
            
            在现代，成为一名女巫更多关乎精神上的追求 —— 寻找内心的力量，
            尊重自然，追求知识，以及用你的才能帮助他人。
            """
        elif category == "meditation":
            response = """
            闭上眼睛，深呼吸。让你的身体完全放松，感受每一次呼吸带来的平静。
            
            想象你站在一片宁静的沙滩上，脚趾感受着温暖细腻的沙子。海浪轻柔地拍打着岸边，
            发出令人心旷神怡的声音。蔚蓝的天空与大海融为一体，阳光温柔地照耀着你的身体。
            
            随着每一次呼吸，你感到越来越平静，越来越专注。所有的压力和焦虑都随着呼气离开了你的身体。
            你的心灵现在完全沉浸在这片宁静的海滩上，感受着大自然的力量和治愈。
            
            继续保持这种平静的状态，让它在你的内心深处扎根。这份宁静会一直伴随着你，
            即使在日常生活中也能随时唤起这种平静的感觉。
            """
        elif category == "nature":
            response = """
            高山流水，云雾缭绕。清晨的第一缕阳光穿透云层，洒在翠绿的山谷中。
            
            小溪欢快地流淌着，水面映照着蓝天和白云的倒影。山间野花竞相绽放，
            各色蝴蝶在花丛中翩翩起舞。远处，一群鹿正在溪边饮水，它们警觉而优雅的姿态，
            与这片宁静的自然景观融为一体。
            
            微风拂过树梢，发出沙沙的响声，仿佛大自然在讲述着古老的故事。
            高耸入云的古树见证了千年的风霜，它们默默伫立，守护着这片净土。
            
            在这里，时间仿佛停滞了，只有季节的变换在悄悄进行。大自然的鬼斧神工
            创造了这片美丽的景色，让人不禁感叹生命的神奇和壮美。
            """
        elif category == "technology":
            response = """
            科技的进步日新月异，人工智能、大数据、云计算等前沿技术正在重塑我们的生活和工作方式。
            
            智能设备已经走进千家万户，从智能手机到智能家居，它们不断提升着我们的生活品质和效率。
            未来的智慧城市将更加智能化，交通系统实现自动调度，能源使用更加高效环保。
            
            虚拟现实和增强现实技术正在创造全新的交互体验，打破了物理世界的限制，
            让人们可以沉浸在数字构建的奇妙世界中。
            
            随着技术的发展，我们需要思考如何让科技更好地服务于人类，
            如何在创新中保持对伦理和隐私的尊重，让技术真正成为改善人类生活的力量。
            """
        elif category == "education":
            response = """
            教育是点亮心灵的火炬，是开启未来的钥匙。在知识爆炸的时代，教育的方式和内容也在不断革新。
            
            个性化学习正成为新趋势，每个学生可以根据自己的节奏和兴趣探索知识的海洋。
            技术在教育中的应用使学习变得更加生动有趣，虚拟课堂打破了地域限制，
            优质教育资源可以惠及更多人。
            
            然而，教育的核心永远是培养人的全面发展，包括批判性思维、创造力、沟通能力和情感智力。
            好的教育不仅传授知识，更教会学生如何思考，如何成为终身学习者。
            
            教师的角色也在转变，从知识的传递者变为学习的引导者和激发者，
            帮助学生发现自己的潜能和热情，为未来的挑战做好准备。
            """
        else:
            response = """
            感谢您的提问。我将为您生成一段富有视觉描述性的内容，适合用于视频制作。
            
            想象一个充满活力的场景，色彩鲜明，光影交错。人们在其中互动，分享知识和经验。
            这是一个既有深度又有趣味的内容展示，能够吸引观众的注意力并保持他们的兴趣。
            
            通过精心编排的画面转换和流畅的叙事，我们可以将复杂的概念简化，让观众轻松理解
            并记住关键信息。视频中的每一个元素都经过精心设计，服务于整体主题。
            
            希望这段内容能够启发您的创作灵感，帮助您制作出精彩的视频作品。
            如果您需要更具体的内容，请提供更详细的主题和方向。
            """
        
        logger.info("Generated mock text response")
        return response.strip()
    
    def generate_speech(self, text, voice="zh_female_1", format="mp3"):
        """
        Generate mock speech file.
        
        Args:
            text (str): Text to convert to speech
            voice (str, optional): Voice ID
            format (str, optional): Audio format
        
        Returns:
            str: Path to mock audio file
        """
        logger.info(f"Generating mock speech file with {self.model_name}. Text length: {len(text)}")
        
        # Create a mock audio file
        temp_path = os.path.join(tempfile.gettempdir(), f"mock_audio_{random.randint(1000, 9999)}.mp3")
        
        try:
            # Create an empty file
            with open(temp_path, 'wb') as f:
                # Write some random bytes to simulate an audio file
                f.write(b'\x00' * 1024)
            
            logger.info(f"Created mock audio file: {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"Error creating mock audio file: {e}")
            return None 