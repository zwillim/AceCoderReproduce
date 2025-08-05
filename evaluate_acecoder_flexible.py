#!/usr/bin/env python3
"""
Flexible Evaluation Script for AceCoder with Configurable Methods
支持配置方法的AceCoder灵活评估脚本

This script allows you to configure which methods to run in the evaluation.
Available methods: 'acecoder', 'zero_shot', 'few_shot', 'cot'

这个脚本允许您配置在评估中运行哪些方法。
可用方法: 'acecoder', 'zero_shot', 'few_shot', 'cot'
"""

import json
import random
import os
from typing import List, Dict, Optional, Tuple
from acecoder import AceCoder
from improved_generator import ImprovedCodeGenerator
from baseline_methods import BaselineMethodManager
from config import config


def load_test_data(file_path: str, max_samples: int = 50) -> List[Dict]:
    """Load test data from MBPP dataset"""
    """从MBPP数据集加载测试数据"""
    data = []
    
    if file_path.endswith('.jsonl'):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    elif file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    # Use a subset for evaluation
    # 使用子集进行评估
    if len(data) > max_samples:
        data = random.sample(data, max_samples)
    
    return data


def evaluate_single_method(method_name: str, test_data: List[Dict], 
                          acecoder: AceCoder, generator: ImprovedCodeGenerator,
                          baseline_manager: BaselineMethodManager) -> Tuple[int, List[Dict]]:
    """Evaluate a single method on test data"""
    """在测试数据上评估单个方法"""
    
    correct = 0
    detailed_results = []
    
    print(f"\n{'='*60}")
    print(f"EVALUATING: {method_name.upper()}")
    print(f"评估: {method_name.upper()}")
    print(f"{'='*60}")
    
    for i, item in enumerate(test_data):
        query = item.get('prompt', item.get('text', ''))
        test_list = item.get('test_list', [])
        task_id = item.get('task_id', i)
        
        print(f"\nTest {i+1}/{len(test_data)} (Task {task_id}): {query[:50]}...")
        print(f"测试 {i+1}/{len(test_data)} (任务 {task_id}): {query[:50]}...")
        
        try:
            # Generate prompt based on method
            if method_name == 'acecoder':
                prompt = acecoder.construct_prompt(query, k=3)
                response = generator.generate(prompt)
                
                # Extract code from AceCoder response
                if '[source code]' in response:
                    code = response.split('[source code]')[-1].strip()
                else:
                    lines = response.split('\n')
                    code_lines = []
                    for line in lines:
                        if not line.strip().startswith('#'):
                            code_lines.append(line)
                    code = '\n'.join(code_lines).strip()
                    
            elif method_name == 'zero_shot':
                method_obj = baseline_manager.get_method('zero_shot')
                prompt = method_obj.create_prompt(query)
                response = generator.generate(prompt)
                code = extract_code_from_response(response)
                
            elif method_name == 'few_shot':
                method_obj = baseline_manager.get_method('few_shot')
                prompt = method_obj.create_prompt(query)
                response = generator.generate(prompt)
                code = extract_code_from_response(response)
                
            elif method_name == 'cot':
                method_obj = baseline_manager.get_method('cot')
                prompt = method_obj.create_prompt(query)
                response = generator.generate(prompt)
                code = extract_code_from_response(response)
                
            else:
                raise ValueError(f"Unknown method: {method_name}")
            
            # Test the generated code
            is_correct = acecoder.test_code(code, test_list)
            
            if is_correct:
                correct += 1
                print(f"  ✓ {method_name}: PASS")
                print(f"  ✓ {method_name}: 通过")
            else:
                print(f"  ✗ {method_name}: FAIL")
                print(f"  ✗ {method_name}: 失败")
                print(f"    Generated: {code[:100]}...")
                print(f"    生成的代码: {code[:100]}...")
            
            detailed_results.append({
                'task_id': task_id,
                'method': method_name,
                'query': query[:100],
                'prompt_length': len(prompt),
                'response_length': len(response),
                'code_length': len(code),
                'is_correct': is_correct,
                'generated_code': code[:200] + '...' if len(code) > 200 else code
            })
            
        except Exception as e:
            print(f"  ✗ {method_name}: ERROR - {e}")
            print(f"  ✗ {method_name}: 错误 - {e}")
            detailed_results.append({
                'task_id': task_id,
                'method': method_name,
                'query': query[:100],
                'error': str(e),
                'is_correct': False
            })
    
    return correct, detailed_results


def extract_code_from_response(response: str) -> str:
    """Extract code from baseline method response"""
    """从基线方法响应中提取代码"""
    lines = response.split('\n')
    code_lines = []
    for line in lines:
        if not line.strip().startswith('#'):
            code_lines.append(line)
    return '\n'.join(code_lines).strip()


def flexible_evaluation():
    """Run flexible evaluation with configurable methods"""
    """运行支持配置方法的灵活评估"""
    
    # 验证配置
    if not config.validate():
        print("Configuration validation failed. Please check your settings.")
        print("配置验证失败。请检查您的设置。")
        return None
    
    # 验证方法配置
    available_methods = ['acecoder', 'zero_shot', 'few_shot', 'cot']
    invalid_methods = [m for m in config.methods_to_run if m not in available_methods]
    if invalid_methods:
        print(f"Error: Invalid methods specified: {invalid_methods}")
        print(f"错误: 指定了无效的方法: {invalid_methods}")
        print(f"Available methods: {available_methods}")
        print(f"可用方法: {available_methods}")
        return None
    
    # 打印当前配置
    config.print_config()
    
    print("Initializing evaluation components...")
    print("正在初始化评估组件...")
    
    # Initialize components
    acecoder = AceCoder(config.training_data_path)
    generator = ImprovedCodeGenerator()
    baseline_manager = BaselineMethodManager(config.training_data_path)
    
    # Load test data
    print("Loading test data...")
    print("正在加载测试数据...")
    test_data = load_test_data(config.dataset_path, max_samples=config.max_samples)
    
    print(f"Evaluating on {len(test_data)} test samples...")
    print(f"正在评估 {len(test_data)} 个测试样本...")
    print(f"Methods to evaluate: {', '.join(config.methods_to_run)}")
    print(f"评估方法: {', '.join(config.methods_to_run)}")
    
    # Store results for all methods
    all_results = {}
    all_detailed_results = {}
    
    # Evaluate each configured method
    for method_name in config.methods_to_run:
        correct, detailed_results = evaluate_single_method(
            method_name, test_data, acecoder, generator, baseline_manager
        )
        all_results[method_name] = correct
        all_detailed_results[method_name] = detailed_results
    
    # Print comprehensive results
    print_evaluation_results(all_results, all_detailed_results, len(test_data))
    
    # Save detailed results
    save_evaluation_results(all_results, all_detailed_results, len(test_data))
    
    return all_results, all_detailed_results


def print_evaluation_results(results: Dict[str, int], detailed_results: Dict[str, List[Dict]], total_samples: int):
    """Print evaluation results"""
    """打印评估结果"""
    
    print("\n" + "=" * 80)
    print("EVALUATION RESULTS")
    print("评估结果")
    print("=" * 80)
    
    print(f"Total test samples: {total_samples}")
    print(f"总测试样本数: {total_samples}")
    print()
    
    # Calculate and display accuracies
    accuracies = {}
    for method_name, correct_count in results.items():
        accuracy = correct_count / total_samples
        accuracies[method_name] = accuracy
        
        # Display method name mapping
        display_name = {
            'acecoder': 'AceCoder',
            'zero_shot': 'Zero-shot Prompting',
            'few_shot': 'Few-shot Prompting', 
            'cot': 'Chain-of-Thought Prompting'
        }.get(method_name, method_name)
        
        print(f"{display_name:25s}: {correct_count:2d}/{total_samples} ({accuracy:.2%})")
    
    # Show method comparison if multiple methods
    if len(results) > 1:
        print("\n" + "-" * 60)
        print("METHOD COMPARISON")
        print("方法对比")
        print("-" * 60)
        
        # Sort methods by accuracy
        sorted_methods = sorted(accuracies.items(), key=lambda x: x[1], reverse=True)
        
        print("Ranking (Best to Worst):")
        print("排名（从最好到最差）:")
        for rank, (method_name, accuracy) in enumerate(sorted_methods, 1):
            display_name = {
                'acecoder': 'AceCoder',
                'zero_shot': 'Zero-shot Prompting',
                'few_shot': 'Few-shot Prompting',
                'cot': 'Chain-of-Thought Prompting'
            }.get(method_name, method_name)
            print(f"{rank}. {display_name:25s}: {accuracy:.2%}")
        
        # Calculate improvements if AceCoder is present
        if 'acecoder' in accuracies:
            acecoder_accuracy = accuracies['acecoder']
            print(f"\nAceCoder vs Other Methods:")
            print(f"AceCoder vs 其他方法:")
            
            for method_name, accuracy in accuracies.items():
                if method_name != 'acecoder':
                    display_name = {
                        'zero_shot': 'Zero-shot Prompting',
                        'few_shot': 'Few-shot Prompting',
                        'cot': 'Chain-of-Thought Prompting'
                    }.get(method_name, method_name)
                    
                    if accuracy > 0:
                        improvement = ((acecoder_accuracy - accuracy) / accuracy) * 100
                        print(f"  vs {display_name:20s}: {improvement:+.1f}%")
                    else:
                        print(f"  vs {display_name:20s}: +∞% (baseline failed all tests)")
    
    # Statistical summary
    print("\n" + "-" * 60)
    print("STATISTICAL SUMMARY")
    print("统计摘要")
    print("-" * 60)
    
    for method_name, details in detailed_results.items():
        if details:
            avg_prompt_len = sum(d.get('prompt_length', 0) for d in details) / len(details)
            avg_code_len = sum(d.get('code_length', 0) for d in details) / len(details)
            
            display_name = {
                'acecoder': 'AceCoder',
                'zero_shot': 'Zero-shot Prompting',
                'few_shot': 'Few-shot Prompting',
                'cot': 'Chain-of-Thought Prompting'
            }.get(method_name, method_name)
            
            print(f"{display_name:25s}: Avg prompt {avg_prompt_len:.0f} chars, Avg code {avg_code_len:.0f} chars")


def save_evaluation_results(results: Dict[str, int], detailed_results: Dict[str, List[Dict]], total_samples: int):
    """Save evaluation results to JSON file"""
    """将评估结果保存到JSON文件"""
    
    output_data = {
        'evaluation_summary': {
            'total_samples': total_samples,
            'methods_evaluated': list(results.keys()),
            'results': results,
            'accuracies': {name: count/total_samples for name, count in results.items()}
        },
        'detailed_results': detailed_results,
        'config': {
            'dataset_path': config.dataset_path,
            'training_data_path': config.training_data_path,
            'max_samples': config.max_samples,
            'methods_to_run': config.methods_to_run,
            'use_real_llm': config.use_real_llm,
            'model_name': config.model_name if config.use_real_llm else 'Rule-based'
        }
    }
    
    output_file = 'flexible_evaluation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: {output_file}")
    print(f"详细结果已保存到: {output_file}")


def demo_acecoder():
    """Demonstrate AceCoder with a specific example"""
    """使用特定示例演示AceCoder"""
    print("=" * 60)
    print("ACECODER DEMONSTRATION")
    print("ACECODER 演示")
    print("=" * 60)
    
    # Initialize AceCoder
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    # Example query
    query = "Write a function to find the shared elements from the given two lists."
    
    print(f"Query: {query}")
    print(f"查询: {query}")
    print("\nConstructing AceCoder prompt...")
    print("\n正在构建 AceCoder 提示...")
    
    # Construct prompt
    prompt = acecoder.construct_prompt(query, k=3)
    
    print(f"\nGenerated AceCoder Prompt:")
    print(f"\n生成的 AceCoder 提示:")
    print("-" * 40)
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    print("-" * 40)
    
    # Generate response (using rule-based generator for demo)
    generator = ImprovedCodeGenerator()
    response = generator.generate(prompt)
    
    print(f"\nGenerated Response:")
    print(f"\n生成的响应:")
    print(response)
    
    # Test the generated code
    test_list = [
        "assert set(shared_elements([1, 2, 3, 4], [3, 4, 5, 6])) == set([3, 4])",
        "assert set(shared_elements([1, 2], [3, 4])) == set([])"
    ]
    
    print(f"\nTesting generated code...")
    print(f"\n正在测试生成的代码...")
    
    # Extract code
    lines = response.split('\n')
    code_lines = []
    for line in lines:
        if not line.strip().startswith('#'):
            code_lines.append(line)
    code = '\n'.join(code_lines).strip()
    
    # Test code
    try:
        if acecoder.test_code(code, test_list):
            print("  ✓ assert set(shared_elements([1, 2, 3, 4], [3, 4, 5, 6])) == set([3, 4])")
            print("  ✓ assert set(shared_elements([1, 2], [3, 4])) == set([])")
            print("All tests passed!")
            print("所有测试通过!")
        else:
            print("Some tests failed!")
            print("部分测试失败!")
    except Exception as e:
        print(f"Error testing code: {e}")
        print(f"测试代码时出错: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Flexible AceCoder evaluation with configurable methods")
    parser.add_argument("--demo", action="store_true", help="Run AceCoder demonstration")
    parser.add_argument("--eval", action="store_true", help="Run flexible evaluation")
    parser.add_argument("--methods", nargs='+', choices=['acecoder', 'zero_shot', 'few_shot', 'cot'],
                       help="Override methods to run (e.g., --methods acecoder zero_shot)")
    
    args = parser.parse_args()
    
    # Override methods if specified
    if args.methods:
        config.methods_to_run = args.methods
        print(f"Overriding methods to run: {args.methods}")
        print(f"覆盖运行方法: {args.methods}")
    
    if args.demo:
        demo_acecoder()
    elif args.eval:
        flexible_evaluation()
    else:
        print("Use --demo to see AceCoder demonstration or --eval to run evaluation")
        print("使用 --demo 查看 AceCoder 演示或 --eval 运行评估")
        print("Use --methods to specify which methods to run (e.g., --methods acecoder zero_shot)")
        print("使用 --methods 指定运行哪些方法 (例如: --methods acecoder zero_shot)")