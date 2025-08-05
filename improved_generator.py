#!/usr/bin/env python3
"""
Improved Code Generator for AceCoder evaluation
This generator tries to understand the pattern from examples and generate appropriate code
"""

import re
import json
import os
import requests
from typing import List, Dict, Tuple, Optional, Any
from config import config


class ImprovedCodeGenerator:
    """Improved code generator that learns from AceCoder prompts"""

    def __init__(self):

        from openai import OpenAI

        # self.client = OpenAI(api_key="sk-67a3bbb61aee4bd19e51f45bbac8205d", base_url="https://api.deepseek.com/v1")

        self.api_key = config.api_key
        self.model_name = config.model_name
        self.api_base = config.api_base
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        # self.client = OpenAI(
        #     api_key="sk-ed389b5fd931478bbb7611d88879527a",
        #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        # )
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
        )
        
    def call_real_llm(self, prompt: str) -> str:
        """Call real LLM API"""
        """调用真实LLM API"""

        # 改进的 system prompt，更明确地要求只生成代码
        system_prompt = """You are an expert Python programmer. Your task is to generate code based on the given examples and requirements.
CRITICAL REQUIREMENTS:
1. Generate ONLY the function code
2. Do NOT include any explanations, comments, or markdown formatting
3. Do NOT include any text before or after the code
4. The output should be a clean Python function that can be executed directly
5. Follow the exact function signature and logic from the examples provided
6. Do NOT add any print statements or debug code
7. Return ONLY the code

Example of expected output:
asp=util::mapping($sys.key_map,$src.key)
gasp=string::addSuffix("_",$asp)
=string::concat($gasp,codex::base64Decode($src.userid))"""

        # 改进的 user prompt，更清晰地说明要求
        user_prompt = f"""Based on the following examples and requirements, generate code:
{prompt}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self.client.chat.completions.create(
            # model="deepseek-reasoner",
            # model="qwen3-coder-plus",
            model=self.model_name,
            messages=messages,
            stream=False,
        )
        generated_code = response.choices[0].message.content.strip()

        # 清理响应 - 移除可能的markdown格式
        if generated_code.startswith("```python"):
            generated_code = generated_code[9:]
        if generated_code.endswith("```"):
            generated_code = generated_code[:-3]

        # 更严格的代码提取逻辑
        lines = generated_code.split("\n")
        code_lines = []
        in_code_block = False
        found_function = False

        for line in lines:
            original_line = line  # 保留原始行（包含缩进）
            stripped_line = line.strip()

            # 跳过明显的解释文本
            if (
                not stripped_line
                or stripped_line.startswith("To solve")
                or stripped_line.startswith("This approach")
                or stripped_line.startswith("The solution")
                or stripped_line.startswith("Here")
                or stripped_line.startswith("We")
                or stripped_line.startswith("Let")
                or stripped_line.startswith("First")
                or stripped_line.startswith("Next")
                or stripped_line.startswith("Finally")
                or stripped_line.startswith("###")
                or stripped_line.startswith("**")
                or stripped_line.startswith("1.")
                or stripped_line.startswith("2.")
                or stripped_line.startswith("3.")
            ):
                continue

            # 如果遇到函数定义，开始收集代码
            if stripped_line.startswith("def "):
                in_code_block = True
                found_function = True

            if in_code_block:
                code_lines.append(original_line)  # 使用原始行保留缩进

        # 如果没有找到函数定义，尝试其他方法
        if not found_function:
            # 查找包含 def 的行
            for line in lines:
                if "def " in line:
                    code_lines = [line]  # 保留原始行
                    found_function = True
                    break

        # 如果仍然没有找到，尝试提取代码块
        if not found_function:
            # 查找可能的代码模式
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                if (
                    "def " in stripped_line
                    or "return " in stripped_line
                    or "=" in stripped_line
                    or "if " in stripped_line
                    or "for " in stripped_line
                    or "while " in stripped_line
                ):
                    code_lines = lines[i:]  # 保留原始行
                    break

        if code_lines:
            # 移除末尾的空行和注释
            while code_lines and (
                not code_lines[-1].strip() or code_lines[-1].strip().startswith("#")
            ):
                code_lines.pop()

            return "\n".join(code_lines).strip()
        else:
            # 如果清理后没有代码，返回原始响应
            return generated_code.strip()

    def generate(self, prompt: str) -> str:
        return self.call_real_llm(prompt)


def test_real_llm_generator():
    """Test the generator with real LLM API"""
    """使用真实LLM API测试生成器"""

    generator = ImprovedCodeGenerator()

    # 使用更简洁的测试prompt，更接近AceCoder的实际格式
    test_prompt = """[requirement]
Write a function to find the shared elements from the given two lists.

[test case]
# similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) -> (4, 5)
# similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) -> (3, 4)

[source code]
def similar_elements(test_tup1, test_tup2):
  res = tuple(set(test_tup1) & set(test_tup2))
  return (res)

[requirement]
Write a function to find the common elements in two lists.

[test case]
# common_elements([1, 2, 3, 4], [3, 4, 5, 6]) -> [3, 4]
"""

    try:
        result = generator.generate(test_prompt)
        print("Generated code with real LLM:")
        print("使用真实LLM生成的代码:")
        print(result)
        print("\n" + "=" * 50)
    except Exception as e:
        print(f"Error testing real LLM: {e}")
        print(f"测试真实LLM时出错: {e}")


if __name__ == "__main__":

    print("\n" + "=" * 50)
    config.set_llm_config(use_real_llm=True)
    print("=== Testing Real LLM Generator ===")
    print("测试真实LLM生成器")
    test_real_llm_generator()
