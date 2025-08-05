#!/usr/bin/env python3
"""
Comprehensive Evaluation Script for AceCoder vs Multiple Baseline Methods
AceCoder与多种基线方法的综合评估脚本

This script evaluates AceCoder against all baseline methods mentioned in the paper:
- Zero-shot Prompting
- Few-shot Prompting
- Chain-of-Thought (CoT) Prompting

这个脚本评估AceCoder与论文中提到的所有基线方法：
- 零样本提示
- 少样本提示  
- 思维链提示
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


def evaluate_method(method_name: str, method_obj, test_data: List[Dict], 
                   acecoder: AceCoder, generator: ImprovedCodeGenerator) -> Tuple[int, List[Dict]]:
    """Evaluate a specific method on test data"""
    """在测试数据上评估特定方法"""
    correct = 0
    detailed_results = []
    
    print(f"\n{'='*20} Evaluating {method_name} {'='*20}")
    print(f"\n{'='*20} 评估 {method_name} {'='*20}")
    
    for i, item in enumerate(test_data):
        query = item.get('prompt', item.get('text', ''))
        test_list = item.get('test_list', [])
        task_id = item.get('task_id', i)
        
        print(f"Test {i+1}/{len(test_data)} (Task {task_id}): {query[:50]}...")
        print(f"测试 {i+1}/{len(test_data)} (任务 {task_id}): {query[:50]}...")
        
        try:
            if method_name == 'AceCoder':
                # Use AceCoder prompting
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
            else:
                # Use baseline method
                prompt = method_obj.create_prompt(query)
                response = generator.generate(prompt)
                
                # Extract code from baseline response
                lines = response.split('\n')
                code_lines = []
                for line in lines:
                    if not line.strip().startswith('#'):
                        code_lines.append(line)
                code = '\n'.join(code_lines).strip()
            
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
                'query': query[:100],
                'error': str(e),
                'is_correct': False
            })
    
    return correct, detailed_results


def comprehensive_evaluation():
    """Run comprehensive evaluation comparing AceCoder with all baseline methods"""
    """运行综合评估，比较AceCoder与所有基线方法"""
    
    # 验证配置
    if not config.validate():
        print("Configuration validation failed. Please check your settings.")
        print("配置验证失败。请检查您的设置。")
        return None
    
    # 打印当前配置
    config.print_config()
    
    print("Initializing comprehensive evaluation...")
    print("正在初始化综合评估...")
    
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
    
    # Evaluate all methods
    results = {}
    detailed_results = {}
    
    # 1. Evaluate AceCoder
    acecoder_correct, acecoder_details = evaluate_method(
        'AceCoder', None, test_data, acecoder, generator
    )
    results['AceCoder'] = acecoder_correct
    detailed_results['AceCoder'] = acecoder_details
    
    # 2. Evaluate baseline methods
    for method_name, method_obj in baseline_manager.get_all_methods().items():
        method_display_name = method_obj.name
        correct, details = evaluate_method(
            method_display_name, method_obj, test_data, acecoder, generator
        )
        results[method_display_name] = correct
        detailed_results[method_display_name] = details
    
    # Calculate and display results
    print_comprehensive_results(results, detailed_results, len(test_data))
    
    # Save detailed results
    save_detailed_results(results, detailed_results, len(test_data))
    
    return results, detailed_results


def print_comprehensive_results(results: Dict[str, int], detailed_results: Dict[str, List[Dict]], total_samples: int):
    """Print comprehensive evaluation results"""
    """打印综合评估结果"""
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE EVALUATION RESULTS")
    print("综合评估结果")
    print("=" * 80)
    
    print(f"Total test samples: {total_samples}")
    print(f"总测试样本数: {total_samples}")
    print()
    
    # Calculate accuracies
    accuracies = {}
    for method_name, correct_count in results.items():
        accuracy = correct_count / total_samples
        accuracies[method_name] = accuracy
        print(f"{method_name:25s}: {correct_count:2d}/{total_samples} ({accuracy:.2%})")
    
    print("\n" + "-" * 80)
    print("PERFORMANCE COMPARISON")
    print("性能对比")
    print("-" * 80)
    
    # Sort methods by accuracy
    sorted_methods = sorted(accuracies.items(), key=lambda x: x[1], reverse=True)
    
    print("Ranking (Best to Worst):")
    print("排名（从最好到最差）:")
    for rank, (method_name, accuracy) in enumerate(sorted_methods, 1):
        print(f"{rank}. {method_name:20s}: {accuracy:.2%}")
    
    # Calculate improvements over baselines
    acecoder_accuracy = accuracies.get('AceCoder', 0)
    
    print(f"\nAceCoder vs Baseline Methods:")
    print(f"AceCoder vs 基线方法:")
    
    baseline_methods = ['Zero-shot Prompting', 'Few-shot Prompting', 'Chain-of-Thought Prompting']
    for baseline_name in baseline_methods:
        if baseline_name in accuracies:
            baseline_accuracy = accuracies[baseline_name]
            if baseline_accuracy > 0:
                improvement = ((acecoder_accuracy - baseline_accuracy) / baseline_accuracy) * 100
                print(f"  vs {baseline_name:20s}: {improvement:+.1f}%")
            else:
                print(f"  vs {baseline_name:20s}: +∞% (baseline failed all tests)")
    
    print("\n" + "-" * 80)
    print("STATISTICAL SUMMARY")
    print("统计摘要")
    print("-" * 80)
    
    # Calculate average prompt lengths
    for method_name, details in detailed_results.items():
        if details:
            avg_prompt_len = sum(d.get('prompt_length', 0) for d in details) / len(details)
            avg_code_len = sum(d.get('code_length', 0) for d in details) / len(details)
            print(f"{method_name:25s}: Avg prompt {avg_prompt_len:.0f} chars, Avg code {avg_code_len:.0f} chars")


def save_detailed_results(results: Dict[str, int], detailed_results: Dict[str, List[Dict]], total_samples: int):
    """Save detailed results to JSON file"""
    """将详细结果保存到JSON文件"""
    
    output_data = {
        'evaluation_summary': {
            'total_samples': total_samples,
            'results': results,
            'accuracies': {name: count/total_samples for name, count in results.items()}
        },
        'detailed_results': detailed_results,
        'config': {
            'dataset_path': config.dataset_path,
            'training_data_path': config.training_data_path,
            'max_samples': config.max_samples,
            'use_real_llm': config.use_real_llm,
            'model_name': config.model_name if config.use_real_llm else 'Rule-based'
        }
    }
    
    output_file = 'comprehensive_evaluation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: {output_file}")
    print(f"详细结果已保存到: {output_file}")


def demo_baseline_methods():
    """Demonstrate all baseline methods with a specific example"""
    """用特定示例演示所有基线方法"""
    print("=" * 80)
    print("BASELINE METHODS DEMONSTRATION")
    print("基线方法演示")
    print("=" * 80)
    
    # Initialize components
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    baseline_manager = BaselineMethodManager('BMPP/mbpp.jsonl')
    
    query = "Write a function to find the shared elements from the given two lists."
    
    print(f"Example Query: {query}")
    print(f"示例查询: {query}")
    print()
    
    # Show AceCoder prompt
    print("-" * 60)
    print("ACECODER PROMPT")
    print("ACECODER 提示")
    print("-" * 60)
    acecoder_prompt = acecoder.construct_prompt(query, k=3)
    print(f"Prompt length: {len(acecoder_prompt)} characters")
    print(f"提示长度: {len(acecoder_prompt)} 字符")
    print(f"First 500 characters:")
    print(f"前500个字符:")
    print(acecoder_prompt[:500] + "..." if len(acecoder_prompt) > 500 else acecoder_prompt)
    print()
    
    # Show baseline prompts
    for method_name, method_obj in baseline_manager.get_all_methods().items():
        print("-" * 60)
        print(f"{method_obj.name.upper()} PROMPT")
        print(f"{method_obj.name.upper()} 提示")
        print("-" * 60)
        
        prompt = method_obj.create_prompt(query)
        print(f"Prompt length: {len(prompt)} characters")
        print(f"提示长度: {len(prompt)} 字符")
        print("Full prompt:")
        print("完整提示:")
        print(prompt)
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive AceCoder evaluation")
    parser.add_argument("--demo", action="store_true", help="Run demonstration of baseline methods")
    parser.add_argument("--eval", action="store_true", help="Run comprehensive evaluation")
    
    args = parser.parse_args()
    
    if args.demo:
        demo_baseline_methods()
    elif args.eval:
        comprehensive_evaluation()
    else:
        print("Use --demo to see baseline method examples or --eval to run evaluation")
        print("使用 --demo 查看基线方法示例或 --eval 运行评估")