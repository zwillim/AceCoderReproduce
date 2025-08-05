#!/usr/bin/env python3
"""
Test script for baseline methods
基线方法测试脚本

This script tests the implementation of all baseline methods to ensure they work correctly.
这个脚本测试所有基线方法的实现，确保它们正常工作。
"""

from baseline_methods import BaselineMethodManager, ZeroShotPrompting, FewShotPrompting, ChainOfThoughtPrompting


def test_individual_methods():
    """Test each baseline method individually"""
    """单独测试每个基线方法"""
    
    print("=" * 80)
    print("TESTING INDIVIDUAL BASELINE METHODS")
    print("测试单个基线方法")
    print("=" * 80)
    
    query = "Write a function to find the maximum value in a list."
    
    # Test Zero-shot
    print("\n1. Testing Zero-shot Prompting")
    print("1. 测试零样本提示")
    print("-" * 40)
    
    zero_shot = ZeroShotPrompting()
    zero_shot_prompt = zero_shot.create_prompt(query)
    print(f"Method name: {zero_shot.name}")
    print(f"方法名称: {zero_shot.name}")
    print(f"Prompt length: {len(zero_shot_prompt)} characters")
    print(f"提示长度: {len(zero_shot_prompt)} 字符")
    print("Generated prompt:")
    print("生成的提示:")
    print(zero_shot_prompt)
    
    # Test Few-shot
    print("\n2. Testing Few-shot Prompting")
    print("2. 测试少样本提示")
    print("-" * 40)
    
    few_shot = FewShotPrompting()
    few_shot_prompt = few_shot.create_prompt(query)
    print(f"Method name: {few_shot.name}")
    print(f"方法名称: {few_shot.name}")
    print(f"Number of examples: {len(few_shot.examples)}")
    print(f"示例数量: {len(few_shot.examples)}")
    print(f"Prompt length: {len(few_shot_prompt)} characters")
    print(f"提示长度: {len(few_shot_prompt)} 字符")
    print("Generated prompt (first 800 chars):")
    print("生成的提示（前800字符）:")
    print(few_shot_prompt[:800] + "..." if len(few_shot_prompt) > 800 else few_shot_prompt)
    
    # Test Chain-of-Thought
    print("\n3. Testing Chain-of-Thought Prompting")
    print("3. 测试思维链提示")
    print("-" * 40)
    
    cot = ChainOfThoughtPrompting()
    cot_prompt = cot.create_prompt(query)
    print(f"Method name: {cot.name}")
    print(f"方法名称: {cot.name}")
    print(f"Prompt length: {len(cot_prompt)} characters")
    print(f"提示长度: {len(cot_prompt)} 字符")
    print("Generated prompt:")
    print("生成的提示:")
    print(cot_prompt)


def test_baseline_manager():
    """Test the baseline method manager"""
    """测试基线方法管理器"""
    
    print("\n" + "=" * 80)
    print("TESTING BASELINE METHOD MANAGER")
    print("测试基线方法管理器")
    print("=" * 80)
    
    manager = BaselineMethodManager()
    query = "Write a function to calculate the factorial of a number."
    
    print(f"Test query: {query}")
    print(f"测试查询: {query}")
    print()
    
    # Test getting all methods
    all_methods = manager.get_all_methods()
    print(f"Available methods: {list(all_methods.keys())}")
    print(f"可用方法: {list(all_methods.keys())}")
    print()
    
    # Test each method through manager
    for method_name in all_methods.keys():
        print(f"\nTesting {method_name} through manager:")
        print(f"通过管理器测试 {method_name}:")
        print("-" * 40)
        
        try:
            prompt = manager.create_prompt(method_name, query)
            print(f"✓ Successfully created prompt ({len(prompt)} chars)")
            print(f"✓ 成功创建提示 ({len(prompt)} 字符)")
        except Exception as e:
            print(f"✗ Error: {e}")
            print(f"✗ 错误: {e}")
    
    # Test error handling
    print(f"\nTesting error handling:")
    print(f"测试错误处理:")
    print("-" * 40)
    
    try:
        manager.get_method('nonexistent_method')
        print("✗ Should have raised an error")
        print("✗ 应该抛出错误")
    except ValueError as e:
        print(f"✓ Correctly handled error: {e}")
        print(f"✓ 正确处理错误: {e}")


def test_prompt_quality():
    """Test the quality and structure of generated prompts"""
    """测试生成提示的质量和结构"""
    
    print("\n" + "=" * 80)
    print("TESTING PROMPT QUALITY")
    print("测试提示质量")
    print("=" * 80)
    
    manager = BaselineMethodManager()
    test_queries = [
        "Write a function to reverse a string.",
        "Write a function to check if a number is prime.",
        "Write a function to find the intersection of two lists.",
        "Write a function to sort a dictionary by values."
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest Query {i}: {query}")
        print(f"测试查询 {i}: {query}")
        print("-" * 60)
        
        for method_name, method_obj in manager.get_all_methods().items():
            prompt = method_obj.create_prompt(query)
            
            # Basic quality checks
            contains_query = query.lower() in prompt.lower()
            has_reasonable_length = 50 < len(prompt) < 5000
            
            print(f"{method_obj.name:25s}: {len(prompt):4d} chars, Contains query: {contains_query}, Reasonable length: {has_reasonable_length}")


if __name__ == "__main__":
    test_individual_methods()
    test_baseline_manager()
    test_prompt_quality()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("所有测试完成")
    print("=" * 80)