#!/usr/bin/env python3
"""
AceCoder Demo Script - Demonstrates the implementation based on the paper:
"AceCoder: Utilizing Existing Code to Enhance Code Generation" by Li et al. (2024)

This script demonstrates:
1. Example Retrieval using BM25
2. Guided Code Generation with test cases as preliminaries  
3. Prompt construction with <requirement, preliminary, code> triples
4. Comparison with baseline prompting
"""

from acecoder import AceCoder
from improved_generator import ImprovedCodeGenerator


def demonstrate_core_components():
    """Demonstrate each core component of AceCoder"""
    print("=" * 80)
    print("ACECODER CORE COMPONENTS DEMONSTRATION")
    print("ACECODER 核心组件演示")
    print("=" * 80)
    
    # Initialize AceCoder
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    # Test query
    query = "Write a function to find the shared elements from the given two lists."
    print(f"Query: {query}")
    print(f"查询: {query}")
    
    print("\n" + "-" * 60)
    print("1. EXAMPLE RETRIEVAL (BM25-based)")
    print("1. 示例检索 (基于BM25)")
    print("-" * 60)
    
    # Demonstrate retrieval
    similar_examples = acecoder.retrieve_examples(query, top_k=5)
    print(f"Retrieved {len(similar_examples)} similar examples:")
    print(f"检索到 {len(similar_examples)} 个相似示例:")
    
    for i, (text, code, tests) in enumerate(similar_examples[:3]):
        print(f"\nExample {i+1}:")
        print(f"示例 {i+1}:")
        print(f"  Requirement: {text[:80]}...")
        print(f"  需求: {text[:80]}...")
        print(f"  Code snippet: {code[:60].replace(chr(10), ' ')}...")
        print(f"  代码片段: {code[:60].replace(chr(10), ' ')}...")
        print(f"  Test cases: {len(tests)} tests")
        print(f"  测试用例: {len(tests)} 个")
    
    print("\n" + "-" * 60)
    print("2. EXAMPLE SELECTION (Redundancy filtering)")
    print("2. 示例选择 (冗余过滤)")
    print("-" * 60)
    
    # Demonstrate selection
    example_pairs = [(text, code) for text, code, _ in similar_examples]
    selected_pairs = acecoder.selector.select_examples(query, example_pairs, k=3)
    
    print(f"Selected {len(selected_pairs)} examples after filtering redundancy:")
    print(f"过滤冗余后选择了 {len(selected_pairs)} 个示例:")
    for i, (text, code) in enumerate(selected_pairs):
        print(f"  {i+1}. {text[:60]}...")
    
    print("\n" + "-" * 60)
    print("3. GUIDED CODE GENERATION (Test cases as preliminaries)")
    print("3. 引导代码生成 (测试用例作为预备内容)")
    print("-" * 60)
    
    # Demonstrate test case extraction
    for text, code in selected_pairs[:1]:  # Show one example
        # Find test cases for this example
        test_list = []
        for orig_text, orig_code, orig_tests in similar_examples:
            if orig_text == text and orig_code == code:
                test_list = orig_tests
                break
        
        preliminary = acecoder.analyzer.extract_test_cases(test_list)
        print(f"Original requirement: {text}")
        print(f"原始需求: {text}")
        print(f"Extracted test cases as preliminary:")
        print(f"提取的测试用例作为预备内容:")
        print(preliminary)
        print(f"Original code: {code[:100]}...")
        print(f"原始代码: {code[:100]}...")
    
    print("\n" + "-" * 60)
    print("4. PROMPT CONSTRUCTION")
    print("4. 提示构建")
    print("-" * 60)
    
    # Show final prompt
    prompt = acecoder.construct_prompt(query, k=3)
    print("Final AceCoder prompt structure:")
    print("最终的 AceCoder 提示结构:")
    print(f"Length: {len(prompt)} characters")
    print(f"长度: {len(prompt)} 字符")
    print(f"Number of examples: {prompt.count('[requirement]') - 1}")
    print(f"示例数量: {prompt.count('[requirement]') - 1}")
    print(f"Contains test cases: {'[test case]' in prompt}")
    print(f"包含测试用例: {'[test case]' in prompt}")
    print(f"Contains source code: {'[source code]' in prompt}")
    print(f"包含源代码: {'[source code]' in prompt}")


def compare_prompting_approaches():
    """Compare AceCoder with standard prompting"""
    print("\n" + "=" * 80)
    print("PROMPTING APPROACHES COMPARISON")
    print("提示方法对比")
    print("=" * 80)
    
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    generator = ImprovedCodeGenerator()
    
    query = "Write a function to find the maximum value in a list of numbers."
    
    print(f"Query: {query}")
    print(f"查询: {query}")
    
    print("\n" + "-" * 40)
    print("STANDARD FEW-SHOT PROMPTING:")
    print("标准少样本提示:")
    print("-" * 40)
    
    standard_prompt = f"""def max_value(nums):
    return max(nums)

def min_value(nums):
    return min(nums)

def sum_values(nums):
    return sum(nums)

{query}"""
    
    print("Standard prompt structure:")
    print("标准提示结构:")
    print("- Simple examples without context")
    print("- 简单的无上下文示例")
    print("- No test cases provided")
    print("- 不提供测试用例")
    print("- No guided generation")
    print("- 无引导生成")
    print(f"- Prompt length: {len(standard_prompt)} characters")
    print(f"- 提示长度: {len(standard_prompt)} 字符")
    
    standard_response = generator.generate(standard_prompt)
    print(f"\nGenerated code:\n{standard_response}")
    print(f"\n生成的代码:\n{standard_response}")
    
    print("\n" + "-" * 40)
    print("ACECODER PROMPTING:")
    print("ACECODER 提示:")
    print("-" * 40)
    
    acecoder_prompt = acecoder.construct_prompt(query, k=3)
    print("AceCoder prompt structure:")
    print("AceCoder 提示结构:")
    print("- Retrieved similar examples")
    print("- 检索相似示例")
    print("- Test cases as preliminaries")
    print("- 测试用例作为预备内容")
    print("- Guided generation pattern")
    print("- 引导生成模式")
    print(f"- Prompt length: {len(acecoder_prompt)} characters")
    print(f"- 提示长度: {len(acecoder_prompt)} 字符")
    
    acecoder_response = generator.generate(acecoder_prompt)
    print(f"\nGenerated code:\n{acecoder_response}")
    print(f"\n生成的代码:\n{acecoder_response}")


def demonstrate_paper_consistency():
    """Demonstrate consistency with the paper's methodology"""
    print("\n" + "=" * 80)
    print("PAPER CONSISTENCY DEMONSTRATION")
    print("论文一致性演示")
    print("=" * 80)
    
    print("AceCoder Implementation Features (from paper):")
    print("AceCoder 实现特性 (来自论文):")
    print("✓ 1. Example Retrieval:")
    print("✓ 1. 示例检索:")
    print("     - BM25-based retrieval system")
    print("     - 基于BM25的检索系统")
    print("     - Retrieves top-k similar programs")
    print("     - 检索top-k个相似程序")
    print("     - Uses requirement text as query")
    print("     - 使用需求文本作为查询")
    
    print("✓ 2. Example Selection:")
    print("✓ 2. 示例选择:")
    print("     - Filters redundant programs using n-gram overlap")
    print("     - 使用n-gram重叠过滤冗余程序")
    print("     - Uses decay factor to reduce redundancy")
    print("     - 使用衰减因子减少冗余")
    print("     - ROUGE-n based scoring")
    print("     - 基于ROUGE-n的评分")
    
    print("✓ 3. Guided Code Generation:")
    print("✓ 3. 引导代码生成:")
    print("     - Test cases as intermediate preliminaries")
    print("     - 测试用例作为中间预备内容")
    print("     - Follows <requirement, preliminary, code> structure")
    print("     - 遵循 <需求, 预备内容, 代码> 结构")
    print("     - Encourages LLMs to understand requirements first")
    print("     - 鼓励LLM先理解需求")
    
    print("✓ 4. Prompt Construction:")
    print("✓ 4. 提示构建:")
    print("     - Triple examples format")
    print("     - 三元组示例格式")
    print("     - Special tags: [requirement], [test case], [source code]")
    print("     - 特殊标签: [requirement], [test case], [source code]")
    print("     - Ends with new requirement and empty test case slot")
    print("     - 以新需求和空测试用例槽位结束")
    
    print("\nDataset Compatibility:")
    print("\n数据集兼容性:")
    print("✓ - Uses MBPP dataset as specified in paper")
    print("✓ - 按论文要求使用MBPP数据集")
    print("✓ - Handles test cases for evaluation")
    print("✓ - 处理测试用例进行评估")
    print("✓ - Supports Pass@k evaluation metric")
    print("✓ - 支持Pass@k评估指标")
    
    print("\nKey Differences from Standard ICL:")
    print("\n与标准ICL的关键差异:")
    print("- Standard ICL: Simple <requirement, code> pairs")
    print("- 标准ICL: 简单的 <需求, 代码> 对")
    print("- AceCoder: <requirement, test_cases, code> triples")
    print("- AceCoder: <需求, 测试用例, 代码> 三元组")
    print("- Standard ICL: Random example selection")  
    print("- 标准ICL: 随机示例选择")
    print("- AceCoder: Intelligent retrieval + redundancy filtering")
    print("- AceCoder: 智能检索 + 冗余过滤")
    print("- Standard ICL: Direct code generation")
    print("- 标准ICL: 直接代码生成")
    print("- AceCoder: Guided generation via preliminaries")
    print("- AceCoder: 通过预备内容引导生成")


def show_example_outputs():
    """Show concrete examples of AceCoder outputs"""
    print("\n" + "=" * 80)
    print("CONCRETE EXAMPLES")
    print("具体示例")
    print("=" * 80)
    
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    test_queries = [
        "Write a function to find the minimum value in a list.",
        "Write a function to count occurrences of an element in a list.",
        "Write a function to remove duplicates from a list."
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n{'-' * 50}")
        print(f"Example {i+1}: {query}")
        print(f"示例 {i+1}: {query}")
        print(f"{'-' * 50}")
        
        # Show retrieval results
        similar_examples = acecoder.retrieve_examples(query, top_k=3)
        print(f"Top retrieved example: {similar_examples[0][0][:80]}...")
        print(f"检索到的顶级示例: {similar_examples[0][0][:80]}...")
        
        # Show constructed prompt (abbreviated)
        prompt = acecoder.construct_prompt(query, k=2)
        lines = prompt.split('\n')
        print(f"Prompt preview ({len(lines)} lines):")
        print(f"提示预览 ({len(lines)} 行):")
        print('\n'.join(lines[:10]) + '\n...')
        
        # Show what would be generated (conceptually)
        print("Expected generation pattern:")
        print("预期的生成模式:")
        print("1. Model sees examples with test cases")
        print("1. 模型看到带有测试用例的示例")
        print("2. Model generates test cases for new query")
        print("2. 模型为新查询生成测试用例")
        print("3. Model generates code guided by test cases")
        print("3. 模型在测试用例引导下生成代码")


def main():
    """Main demonstration function"""
    print("AceCoder Implementation Demo")
    print("AceCoder 实现演示")
    print("Based on: 'AceCoder: Utilizing Existing Code to Enhance Code Generation'")
    print("基于: 'AceCoder: 利用现有代码增强代码生成'")
    print("by Li et al. (2024)")
    print("作者: Li 等人 (2024)")
    
    # Run all demonstrations
    demonstrate_core_components()
    compare_prompting_approaches()
    demonstrate_paper_consistency()
    show_example_outputs()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("总结")
    print("=" * 80)
    print("This implementation demonstrates AceCoder's key innovations:")
    print("此实现演示了 AceCoder 的关键创新:")
    print("1. ✓ BM25-based example retrieval")
    print("1. ✓ 基于BM25的示例检索")
    print("2. ✓ Redundancy-aware example selection") 
    print("2. ✓ 冗余感知的示例选择")
    print("3. ✓ Test-case guided code generation")
    print("3. ✓ 测试用例引导的代码生成")
    print("4. ✓ Structured prompt construction")
    print("4. ✓ 结构化提示构建")
    print("5. ✓ MBPP dataset compatibility")
    print("5. ✓ MBPP数据集兼容性")
    print("\nThe implementation follows the paper's methodology and")
    print("\n该实现遵循论文的方法论，")
    print("provides a foundation for reproducing the reported results.")
    print("为复现报告结果提供了基础。")


if __name__ == "__main__":
    main()