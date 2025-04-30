import os
import sys
import unittest
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

from strategies.hallucination import hallucination_mutate
from strategies.jailbreak import jailbreak_mutate
from strategies.consistency import consistency_mutate, char_level_mutate, word_level_mutate, sentence_level_mutate

class TestMutationStrategies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 设置测试日志
        log_dir = Path(__file__).parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'test_mutation_{current_time}.log'
        
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        cls.logger = logging.getLogger('TestMutation')
        cls.logger.info('开始变异策略测试')

    def setUp(self):
        self.template_text = "This is a test template."
        self.test_question = {
            "id": "test001",
            "question": "What is the capital of France?",
            "incorrect_answers": "London is the capital of France",
            "category": "Geography"
        }

    def test_hallucination_mutation(self):
        self.logger.info('测试幻觉变异策略')
        mutated, log = hallucination_mutate(self.template_text, self.test_question)
        self.assertIsNotNone(mutated)
        self.assertNotEqual(mutated, self.template_text)
        self.logger.info(f'幻觉变异结果: {mutated}')

    def test_jailbreak_mutation(self):
        self.logger.info('测试越狱变异策略')
        mutated, log = jailbreak_mutate(self.template_text, self.test_question)
        self.assertIsNotNone(mutated)
        self.assertNotEqual(mutated, self.template_text)
        self.logger.info(f'越狱变异结果: {mutated}')

    def test_char_level_mutation(self):
        self.logger.info('测试字符级变异')
        mutated = char_level_mutate(self.template_text)
        self.assertIsNotNone(mutated)
        self.assertNotEqual(mutated, self.template_text)
        self.assertEqual(len(mutated), len(self.template_text) + 1)  # 应该只插入了一个字符
        self.logger.info(f'字符级变异结果: {mutated}')

    def test_word_level_mutation(self):
        self.logger.info('测试词级变异')
        mutated = word_level_mutate(self.template_text)
        self.assertIsNotNone(mutated)
        self.logger.info(f'词级变异结果: {mutated}')

    def test_consistency_mutation(self):
        self.logger.info('测试一致性变异策略')
        mutated, log = consistency_mutate(self.template_text, self.test_question)
        self.assertIsNotNone(mutated)
        self.assertNotEqual(mutated, self.template_text)
        self.logger.info(f'一致性变异结果: {mutated}')

if __name__ == '__main__':
    unittest.main() 