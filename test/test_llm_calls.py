import os
import sys
import unittest
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

from utils import call_assistant_llm, call_target_llm, call_llm

class TestLLMCalls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 加载环境变量
        load_dotenv()
        
        # 设置测试日志
        log_dir = Path(__file__).parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'test_llm_{current_time}.log'
        
        # 使用UTF-8编码配置日志
        handler = logging.FileHandler(str(log_file), encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        logger = logging.getLogger('TestLLM')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        cls.logger = logger
        cls.logger.info('开始LLM调用测试')

    def test_real_api_connection(self):
        """测试真实API连接，类似于test_api.py"""
        self.logger.info('测试真实API连接')
        
        # 验证API配置
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        model = os.getenv("AI_MODEL", "gpt-4")
        
        self.assertIsNotNone(api_key, "API密钥必须设置")
        self.assertIsNotNone(api_base, "API基础URL必须设置")
        self.logger.info(f"使用API基础URL: {api_base}")
        self.logger.info(f"使用模型: {model}")
        
        # 测试实际API调用
        response = call_llm("你好！这是一条测试消息。请回复'API测试成功'。")
        self.assertIsNotNone(response, "应该收到API响应")
        self.logger.info(f"API响应: {response}")
        
        # 验证响应中包含期望的文本
        self.assertIn("测试成功", response, "响应应该表明测试成功")

    def setUp(self):
        """仅为模拟测试设置环境变量"""
        self.real_env = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'OPENAI_API_BASE': os.getenv('OPENAI_API_BASE'),
            'AI_MODEL': os.getenv('AI_MODEL')
        }

    def tearDown(self):
        """恢复真实的环境变量"""
        os.environ.update(self.real_env)

    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """模拟测试错误处理"""
        self.logger.info('测试API错误处理（模拟）')
        
        # 设置模拟环境
        test_env = {
            'OPENAI_API_KEY': 'test-api-key',
            'OPENAI_API_BASE': 'http://test.api',
            'AI_MODEL': 'gpt-4'
        }
        with patch.dict('os.environ', test_env):
            # 测试网络错误
            mock_post.side_effect = Exception("网络错误")
            response = call_llm("测试提示")
            self.assertIsNone(response)
            self.logger.info('成功捕获网络错误')

            # 测试API错误响应
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "请求错误"
            mock_post.side_effect = None
            mock_post.return_value = mock_response

            response = call_llm("测试提示")
            self.assertIsNone(response)
            self.logger.info('成功处理API错误响应')

    def test_assistant_and_target_calls(self):
        """测试辅助和目标LLM调用"""
        self.logger.info('测试辅助和目标LLM调用')
        
        # 测试辅助LLM调用
        response = call_assistant_llm("测试提示")
        self.assertIsNotNone(response)
        self.logger.info(f"辅助LLM响应: {response}")
        
        # 测试目标LLM调用
        response = call_target_llm("测试提示")
        self.assertIsNotNone(response)
        self.logger.info(f"目标LLM响应: {response}")

if __name__ == '__main__':
    unittest.main() 