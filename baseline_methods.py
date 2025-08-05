#!/usr/bin/env python3
"""
Baseline Methods for AceCoder Comparison
AceCoder对比基线方法

This module implements various baseline prompting methods used in the AceCoder paper:
- Zero-shot Prompting
- Few-shot Prompting  
- Chain-of-Thought (CoT) Prompting

这个模块实现了AceCoder论文中使用的各种基线提示方法：
- 零样本提示
- 少样本提示
- 思维链提示
"""

import json
import random
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod


class BaselineMethod(ABC):
    """Abstract base class for baseline prompting methods"""
    """基线提示方法的抽象基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def create_prompt(self, query: str, **kwargs) -> str:
        """Create a prompt for the given query"""
        """为给定查询创建提示"""
        pass


class ZeroShotPrompting(BaselineMethod):
    """Zero-shot prompting baseline method"""
    """零样本提示基线方法"""
    
    def __init__(self):
        super().__init__("Zero-shot Prompting")
    
    def create_prompt(self, query: str, **kwargs) -> str:
        """Create a zero-shot prompt"""
        """创建零样本提示"""
        return f"""Write a Python function to solve the following problem:

Problem: {query}

Please provide a complete Python function that solves this problem."""


class FewShotPrompting(BaselineMethod):
    """Few-shot prompting baseline method"""
    """少样本提示基线方法"""
    
    def __init__(self, training_data_path: str = None):
        super().__init__("Few-shot Prompting")
        self.examples = self._load_fixed_examples(training_data_path)
    
    def _load_fixed_examples(self, training_data_path: str = None) -> List[Dict]:
        """Load fixed examples for few-shot prompting"""
        """为少样本提示加载固定示例"""
        # 使用MBPP数据集中的固定示例（任务ID 2, 3, 4，如论文所述）
        fixed_examples = [
            {
                "text": "Write a function to find the similar elements from the given two tuple lists.",
                "code": "def similar_elements(test_tup1, test_tup2):\n    res = tuple(set(test_tup1) & set(test_tup2))\n    return (res)",
                "test_list": ["assert set(similar_elements((3, 4, 5, 6),(5, 7, 4, 10))) == set((4, 5))", 
                             "assert set(similar_elements((1, 2, 3, 4),(5, 4, 3, 7))) == set((3, 4))",
                             "assert set(similar_elements((11, 12, 14, 13),(17, 15, 14, 13))) == set((13, 14))"]
            },
            {
                "text": "Write a python function to remove first and last occurrence of a given character from the string.",
                "code": "def remove_Occ(s,ch):\n    for i in range(len(s)):\n        if (s[i] == ch):\n            s = s[0:i] + s[i+1:]\n            break\n    for i in range(len(s)-1,-1,-1):\n        if (s[i] == ch):\n            s = s[0:i] + s[i+1:]\n            break\n    return s",
                "test_list": ["assert remove_Occ(\"hello\",\"l\") == \"heo\"",
                             "assert remove_Occ(\"abcda\",\"a\") == \"bcd\"", 
                             "assert remove_Occ(\"PHP\",\"P\") == \"H\""]
            },
            {
                "text": "Write a python function to find sum of elements in list.",
                "code": "def _sum(arr):\n    sum=0\n    for i in arr:\n        sum = sum + i\n    return(sum)",
                "test_list": ["assert _sum([1, 2, 3]) == 6",
                             "assert _sum([15, 12, 13, 10]) == 50",
                             "assert _sum([20, 10, 30, 40]) == 100"]
            }
        ]
        
        # 如果提供了训练数据路径，尝试从中加载真实的固定示例
        if training_data_path:
            try:
                with open(training_data_path, 'r', encoding='utf-8') as f:
                    data = []
                    for line in f:
                        if line.strip():
                            item = json.loads(line)
                            # 使用任务ID 2, 3, 4作为固定示例（如MBPP论文所述）
                            if item.get('task_id') in [2, 3, 4]:
                                data.append(item)
                    if len(data) >= 3:
                        return data[:3]
            except Exception as e:
                print(f"Warning: Could not load examples from {training_data_path}: {e}")
        
        return fixed_examples
    
    def create_prompt(self, query: str, **kwargs) -> str:
        """Create a few-shot prompt with fixed examples"""
        """使用固定示例创建少样本提示"""
        prompt_parts = []
        
        # 添加指令
        prompt_parts.append("You are an expert Python programmer. Here are some examples:")
        prompt_parts.append("")
        
        # 添加固定示例
        for i, example in enumerate(self.examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"Problem: {example['text']}")
            prompt_parts.append("Solution:")
            prompt_parts.append(example['code'])
            prompt_parts.append("")
        
        # 添加新任务
        prompt_parts.append("Now solve this problem:")
        prompt_parts.append(f"Problem: {query}")
        prompt_parts.append("Solution:")
        
        return "\n".join(prompt_parts)


class FewShotPromptingNew(BaselineMethod):
    """Few-shot prompting baseline method that accepts training data directly"""
    """直接接受训练数据的少样本提示基线方法"""
    
    def __init__(self, training_data: List[Dict] = None, num_examples: int = 3):
        super().__init__("Few-shot Prompting (Direct Data)")
        self.training_data = training_data or []
        self.num_examples = num_examples
        self.examples = self._prepare_examples()
    
    def _prepare_examples(self) -> List[Dict]:
        """Prepare examples from training data"""
        """从训练数据准备示例"""
        if not self.training_data:
            # 如果没有提供训练数据，使用默认示例
            return self._get_default_examples()
        
        # 从训练数据中选择示例
        examples = []
        for item in self.training_data:
            if len(examples) >= self.num_examples:
                break
            
            # 提取文本和代码
            text = item.get('text', item.get('prompt', ''))
            code = item.get('code', '')
            
            if text and code:
                examples.append({
                    'text': text,
                    'code': code,
                    'test_list': item.get('test_list', [])
                })
        
        # 如果训练数据不足，补充默认示例
        if len(examples) < self.num_examples:
            default_examples = self._get_default_examples()
            for example in default_examples:
                if len(examples) >= self.num_examples:
                    break
                examples.append(example)
        
        return examples
    
    def _get_default_examples(self) -> List[Dict]:
        """Get default examples when no training data is provided"""
        """当没有提供训练数据时获取默认示例"""
        return [
            {
                "text": "Write a function to find the similar elements from the given two tuple lists.",
                "code": "def similar_elements(test_tup1, test_tup2):\n    res = tuple(set(test_tup1) & set(test_tup2))\n    return (res)",
                "test_list": ["assert set(similar_elements((3, 4, 5, 6),(5, 7, 4, 10))) == set((4, 5))", 
                             "assert set(similar_elements((1, 2, 3, 4),(5, 4, 3, 7))) == set((3, 4))",
                             "assert set(similar_elements((11, 12, 14, 13),(17, 15, 14, 13))) == set((13, 14))"]
            },
            {
                "text": "Write a python function to remove first and last occurrence of a given character from the string.",
                "code": "def remove_Occ(s,ch):\n    for i in range(len(s)):\n        if (s[i] == ch):\n            s = s[0:i] + s[i+1:]\n            break\n    for i in range(len(s)-1,-1,-1):\n        if (s[i] == ch):\n            s = s[0:i] + s[i+1:]\n            break\n    return s",
                "test_list": ["assert remove_Occ(\"hello\",\"l\") == \"heo\"",
                             "assert remove_Occ(\"abcda\",\"a\") == \"bcd\"", 
                             "assert remove_Occ(\"PHP\",\"P\") == \"H\""]
            },
            {
                "text": "Write a python function to find sum of elements in list.",
                "code": "def _sum(arr):\n    sum=0\n    for i in arr:\n        sum = sum + i\n    return(sum)",
                "test_list": ["assert _sum([1, 2, 3]) == 6",
                             "assert _sum([15, 12, 13, 10]) == 50",
                             "assert _sum([20, 10, 30, 40]) == 100"]
            }
        ]
    
    def create_prompt(self, query: str, **kwargs) -> str:
        """Create a few-shot prompt with examples from training data"""
        """使用训练数据中的示例创建少样本提示"""
        prompt_parts = []
        
        # 添加指令
        prompt_parts.append("You are an expert Python programmer. Here are some examples:")
        prompt_parts.append("")
        
        # 添加示例
        for i, example in enumerate(self.examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"Problem: {example['text']}")
            prompt_parts.append("Solution:")
            prompt_parts.append(example['code'])
            prompt_parts.append("")
        
        # 添加新任务
        prompt_parts.append("Now solve this problem:")
        prompt_parts.append(f"Problem: {query}")
        prompt_parts.append("Solution:")
        
        return "\n".join(prompt_parts)
    
    def update_training_data(self, new_training_data: List[Dict]):
        """Update training data and re-prepare examples"""
        """更新训练数据并重新准备示例"""
        self.training_data = new_training_data
        self.examples = self._prepare_examples()


class ChainOfThoughtPrompting(BaselineMethod):
    """Chain-of-Thought (CoT) prompting baseline method"""
    """思维链（CoT）提示基线方法"""
    
    def __init__(self):
        super().__init__("Chain-of-Thought Prompting")
    
    def create_prompt(self, query: str, **kwargs) -> str:
        """Create a chain-of-thought prompt"""
        """创建思维链提示"""
        return f"""Let's solve this step by step.

Problem: {query}

Let's think about this problem:

1. First, I need to understand what the problem is asking for.
2. Then, I need to think about the approach to solve it.
3. Next, I need to consider edge cases and constraints.
4. Finally, I'll implement the solution.

Let me work through this step by step:

Step 1: Understanding the problem
- What inputs do I expect?
- What output should I return?
- What are the requirements?

Step 2: Planning the approach
- What algorithm or method should I use?
- What data structures might be helpful?
- How can I break this down into smaller steps?

Step 3: Implementation
Now I'll write the Python function:"""


class BaselineMethodManager:
    """Manager class for all baseline methods"""
    """所有基线方法的管理器类"""
    
    def __init__(self, training_data_path: str = None, training_data: List[Dict] = None):
        self.methods = {
            'zero_shot': ZeroShotPrompting(),
            'few_shot': FewShotPrompting(training_data_path),
            'few_shot_new': FewShotPromptingNew(training_data),
            'cot': ChainOfThoughtPrompting()
        }
    
    def get_method(self, method_name: str) -> BaselineMethod:
        """Get a specific baseline method"""
        """获取特定的基线方法"""
        if method_name not in self.methods:
            raise ValueError(f"Unknown baseline method: {method_name}. Available: {list(self.methods.keys())}")
        return self.methods[method_name]
    
    def get_all_methods(self) -> Dict[str, BaselineMethod]:
        """Get all baseline methods"""
        """获取所有基线方法"""
        return self.methods
    
    def create_prompt(self, method_name: str, query: str, **kwargs) -> str:
        """Create prompt using specified method"""
        """使用指定方法创建提示"""
        method = self.get_method(method_name)
        return method.create_prompt(query, **kwargs)


def demonstrate_baseline_methods():
    """Demonstrate all baseline methods with an example"""
    """用示例演示所有基线方法"""
    print("=" * 80)
    print("BASELINE METHODS DEMONSTRATION")
    print("基线方法演示")
    print("=" * 80)
    
    manager = BaselineMethodManager('BMPP/mbpp.jsonl')
    query = "Write a function to find the maximum value in a list of numbers."
    
    print(f"Query: {query}")
    print(f"查询: {query}")
    print()
    
    for method_name, method in manager.get_all_methods().items():
        print("-" * 60)
        print(f"METHOD: {method.name}")
        print(f"方法: {method.name}")
        print("-" * 60)
        
        prompt = method.create_prompt(query)
        print("Generated Prompt:")
        print("生成的提示:")
        print()
        print(prompt)
        print()
        print(f"Prompt Length: {len(prompt)} characters")
        print(f"提示长度: {len(prompt)} 字符")
        print()


if __name__ == "__main__":
    demonstrate_baseline_methods()