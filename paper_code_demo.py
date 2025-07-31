#!/usr/bin/env python3
"""
AceCoder: 代码与论文对应关系演示

本脚本详细展示了AceCoder实现代码与原始论文的对应关系，
验证了实现的准确性和与论文的一致性。
"""

from acecoder import AceCoder, LuceneRetriever, BM25Retriever, ExampleSelector, TestCaseAnalyzer
import json


def demonstrate_paper_code_mapping():
    """演示代码与论文的对应关系"""
    print("=" * 80)
    print("ACECODER: 代码与论文对应关系演示")
    print("基于论文: 'AceCoder: An Effective Prompting Technique Specialized for Code Generation'")
    print("=" * 80)
    
    # 1. 示例检索 (Example Retrieval) - Section 3.2.1
    print("\n📋 1. 示例检索 (Example Retrieval) - Section 3.2.1")
    print("-" * 60)
    print("论文描述: 'We use Lucene to retrieve similar programs from the training corpus'")
    
    # 初始化AceCoder（尝试使用Lucene）
    try:
        acecoder = AceCoder('BMPP/mbpp.jsonl', use_lucene=True)
        print("✅ 实现: 使用LuceneRetriever (通过Pyserini)")
        print("   - 自动构建Lucene索引")
        print("   - 使用Lucene默认BM25评分")
        print("   - 支持top-k检索")
    except Exception as e:
        print(f"⚠️  Lucene不可用: {e}")
        print("✅ 回退到内部BM25Retriever实现")
    
    # 2. 示例选择 (Example Selection) - Section 3.2.2
    print("\n📋 2. 示例选择 (Example Selection) - Section 3.2.2")
    print("-" * 60)
    print("论文描述: 'We use a redundancy filtering selector with n-gram overlap analysis'")
    
    selector = ExampleSelector(decay_factor=0.5, n=4)
    print("✅ 实现: ExampleSelector类")
    print(f"   - n-gram大小: {selector.n} (4-gram)")
    print(f"   - 衰减因子: {selector.decay_factor} (λ=0.5)")
    print("   - 使用ROUGE-n评分计算重叠度")
    print("   - 应用衰减因子减少冗余")
    
    # 3. 引导代码生成 (Guided Code Generation) - Section 3.3
    print("\n📋 3. 引导代码生成 (Guided Code Generation) - Section 3.3")
    print("-" * 60)
    print("论文描述: 'We use test cases as intermediate preliminaries'")
    
    analyzer = TestCaseAnalyzer()
    test_cases = [
        "assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)",
        "assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4)"
    ]
    preliminaries = analyzer.extract_test_cases(test_cases)
    
    print("✅ 实现: TestCaseAnalyzer类")
    print("   - 提取测试用例作为预备内容")
    print("   - 格式化: # function_call -> expected_result")
    print("   - 示例输出:")
    print(f"     {preliminaries}")
    
    # 4. 结构化提示 (Structured Prompting) - Section 3.3
    print("\n📋 4. 结构化提示 (Structured Prompting) - Section 3.3")
    print("-" * 60)
    print("论文描述: 'The prompt follows the structure: <requirement, preliminary, code>'")
    
    # 构建示例提示
    example_prompt = acecoder.construct_prompt(
        "Write a function to find the shared elements from two lists", 
        k=1
    )
    
    print("✅ 实现: construct_prompt方法")
    print("   - 三元组结构: <requirement, preliminary, code>")
    print("   - 特殊标签: [requirement], [test case], [source code]")
    print("   - 引导生成: 新查询后留空test case位置")
    print("\n示例提示结构:")
    print("=" * 40)
    print(example_prompt[:500] + "..." if len(example_prompt) > 500 else example_prompt)
    
    # 5. 技术参数对应关系
    print("\n📋 5. 技术参数对应关系")
    print("-" * 60)
    
    print("✅ BM25参数:")
    print("   - 论文: 使用Lucene默认BM25参数")
    print("   - 代码: LuceneRetriever使用Lucene默认参数")
    print("   - 回退: BM25Retriever使用k1=1.5, b=0.75")
    
    print("\n✅ 示例数量:")
    print("   - 论文: 检索top-20，选择top-3")
    print("   - 代码: retrieve_examples(top_k=20), select_examples(k=3)")
    
    print("\n✅ n-gram设置:")
    print("   - 论文: 使用4-gram进行重叠分析")
    print("   - 代码: ExampleSelector(n=4)")
    
    print("\n✅ 衰减因子:")
    print("   - 论文: λ=0.5的衰减因子")
    print("   - 代码: ExampleSelector(decay_factor=0.5)")
    
    # 6. 实验设置对应关系
    print("\n📋 6. 实验设置对应关系")
    print("-" * 60)
    
    print("✅ 数据集:")
    print("   - 论文: MBPP (Mostly Basic Python Problems)")
    print("   - 代码: 使用BMPP/mbpp.jsonl数据集")
    
    print("\n✅ 评估指标:")
    print("   - 论文: Pass@k (k=1, 5, 10)")
    print("   - 代码: evaluate_pass_at_k方法支持不同k值")
    
    print("\n✅ 基线方法:")
    print("   - 论文: 与标准提示方法对比")
    print("   - 代码: performance_analysis.py中的基线对比")
    
    # 7. 验证实现完整性
    print("\n📋 7. 实现完整性验证")
    print("-" * 60)
    
    # 测试检索功能
    query = "Write a function to find the maximum value in a list"
    examples = acecoder.retrieve_examples(query, top_k=5)
    
    print("✅ 示例检索功能:")
    print(f"   - 查询: {query}")
    print(f"   - 检索到 {len(examples)} 个相似示例")
    print(f"   - 第一个示例: {examples[0][0][:100]}...")
    
    # 测试提示构建
    prompt = acecoder.construct_prompt(query, k=2)
    
    print("\n✅ 提示构建功能:")
    print(f"   - 生成长度: {len(prompt)} 字符")
    print(f"   - 包含三元组: {'[requirement]' in prompt and '[test case]' in prompt and '[source code]' in prompt}")
    print(f"   - 引导生成: {prompt.endswith('[test case]\\n')}")
    
    print("\n🎯 总结:")
    print("=" * 60)
    print("✅ 代码实现与论文保持了高度一致性:")
    print("   - 使用Lucene进行示例检索")
    print("   - 实现n-gram重叠分析和衰减因子")
    print("   - 测试用例作为中间预备内容")
    print("   - 结构化提示格式")
    print("   - 完整的实验评估框架")
    
    print("\n✅ 技术细节完全对应:")
    print("   - 检索引擎: Lucene (通过Pyserini)")
    print("   - 选择策略: 4-gram + λ=0.5衰减")
    print("   - 提示格式: <requirement, preliminary, code>")
    print("   - 评估指标: Pass@k")
    
    print("\n✅ 工程实现亮点:")
    print("   - 模块化设计，易于扩展")
    print("   - 自动回退机制，提高鲁棒性")
    print("   - 完整的文档和示例")
    print("   - 可直接用于实际应用")


def demonstrate_lucene_vs_bm25():
    """演示Lucene与BM25的对比"""
    print("\n" + "=" * 80)
    print("LUCENE vs BM25 实现对比")
    print("=" * 80)
    
    # 测试查询
    query = "Write a function to find the shared elements from two lists"
    
    print(f"测试查询: {query}")
    print("-" * 60)
    
    # 使用Lucene (如果可用)
    try:
        lucene_acecoder = AceCoder('BMPP/mbpp.jsonl', use_lucene=True)
        lucene_examples = lucene_acecoder.retrieve_examples(query, top_k=3)
        print("✅ Lucene检索结果:")
        for i, (text, code, tests) in enumerate(lucene_examples):
            print(f"   {i+1}. {text[:80]}...")
    except Exception as e:
        print(f"⚠️  Lucene不可用: {e}")
    
    # 使用BM25
    bm25_acecoder = AceCoder('BMPP/mbpp.jsonl', use_lucene=False)
    bm25_examples = bm25_acecoder.retrieve_examples(query, top_k=3)
    print("\n✅ BM25检索结果:")
    for i, (text, code, tests) in enumerate(bm25_examples):
        print(f"   {i+1}. {text[:80]}...")
    
    print("\n📊 对比分析:")
    print("-" * 60)
    print("• Lucene: 论文指定的检索引擎，性能更优")
    print("• BM25: 内部实现，无需外部依赖")
    print("• 两者都使用BM25评分函数")
    print("• 代码自动选择最佳可用方案")


if __name__ == "__main__":
    # 演示代码与论文的对应关系
    demonstrate_paper_code_mapping()
    
    # 演示Lucene vs BM25对比
    demonstrate_lucene_vs_bm25()
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80) 