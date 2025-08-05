#!/usr/bin/env python3
"""
Evaluation script for AceCoder on split_sets data
split_sets数据上的AceCoder评估脚本
"""

import json
import random
import os
import glob
from typing import List, Dict, Optional, Tuple
from acecoder_new import AceCoderNew, convert_split_sets_to_training_data
from improved_generator import ImprovedCodeGenerator
from baseline_methods import BaselineMethodManager
from config import config


def load_split_sets_data(split_sets_dir: str = "split_sets") -> List[Dict]:
    """Load all JSON files from split_sets directory"""
    """从split_sets目录加载所有JSON文件"""
    all_test_sets = []
    
    # Find all JSON files in split_sets directory
    json_files = glob.glob(os.path.join(split_sets_dir, "*.json"))
    
    if not json_files:
        print(f"警告: 在 {split_sets_dir} 目录中未找到JSON文件")
        print(f"Warning: No JSON files found in {split_sets_dir} directory")
        return []
    
    print(f"找到 {len(json_files)} 个测试任务文件")
    print(f"Found {len(json_files)} test task files")
    
    for json_file in sorted(json_files):
        print(f"正在加载: {json_file}")
        print(f"Loading: {json_file}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract test set name and data
            test_set_name = data.get('name', os.path.basename(json_file))
            test_data = data.get('data', [])
            
            # Process each item in the test set
            processed_items = []
            for item in test_data:
                # Extract essential fields
                flag = item.get('flag', 'test')  # Default to test if flag not present
                content = item.get('content', {})
                code = item.get('code', {})
                
                # Create a simplified representation for evaluation
                processed_item = {
                    'flag': flag,
                    'content': content,
                    'code': code,
                    'task_name': item.get('task_name_old', ''),
                    'tags': item.get('tags_old', []),
                    'test_set_name': test_set_name,
                    'source_file': json_file
                }
                
                processed_items.append(processed_item)
            
            # Add to all test sets
            all_test_sets.append({
                'test_set_name': test_set_name,
                'source_file': json_file,
                'items': processed_items
            })
            
            print(f"  加载了 {len(processed_items)} 个数据项")
            print(f"  Loaded {len(processed_items)} data items")
            
        except Exception as e:
            print(f"错误: 无法加载文件 {json_file}: {e}")
            print(f"Error: Cannot load file {json_file}: {e}")
            continue
    
    return all_test_sets


def prepare_training_and_test_data_for_task(test_set: Dict) -> Tuple[List[Dict], List[Dict]]:
    """Separate training and test data from a single test set"""
    """从单个测试集中分离训练和测试数据"""
    training_data = []
    test_data = []
    
    for item in test_set['items']:
        if item['flag'] == 'train':
            training_data.append(item)
        elif item['flag'] == 'test':
            test_data.append(item)
    
    print(f"任务 '{test_set['test_set_name']}' - 训练数据: {len(training_data)} 个样本")
    print(f"Task '{test_set['test_set_name']}' - Training data: {len(training_data)} samples")
    print(f"任务 '{test_set['test_set_name']}' - 测试数据: {len(test_data)} 个样本")
    print(f"Task '{test_set['test_set_name']}' - Test data: {len(test_data)} samples")
    
    return training_data, test_data


def create_evaluation_item(item: Dict) -> Dict:
    """Convert a data item to evaluation format"""
    """将数据项转换为评估格式"""
    # Extract content description
    content = item['content']
    
    # Create a description from content fields
    description_parts = []
    if 'src' in content:
        for field_info in content['src']:
            if isinstance(field_info, str):
                # Extract field name and description
                if '/' in field_info:
                    field_name, description = field_info.split('/', 1)
                    description_parts.append(f"{field_name}: {description}")
                else:
                    description_parts.append(field_info)
    
    description = "\n".join(description_parts)
    
    # Extract expected code
    expected_code = item['code']
    
    return {
        'prompt': description,
        'code': expected_code,
        'task_name': item['task_name'],
        'tags': item['tags'],
        'test_set_name': item['test_set_name'],
        'source_file': item['source_file']
    }


def evaluate_single_method_on_task(method_name: str, test_data: List[Dict], 
                                  acecoder: AceCoderNew, generator: ImprovedCodeGenerator,
                                  baseline_manager: BaselineMethodManager, task_name: str) -> Tuple[int, List[Dict]]:
    """Evaluate a single method on a specific task"""
    """在特定任务上评估单个方法"""
    
    correct = 0
    detailed_results = []
    
    print(f"\n{'='*60}")
    print(f"EVALUATING TASK: {task_name.upper()}")
    print(f"METHOD: {method_name.upper()}")
    print(f"评估任务: {task_name.upper()}")
    print(f"方法: {method_name.upper()}")
    print(f"{'='*60}")
    
    for i, item in enumerate(test_data):
        query = item.get('prompt', item.get('text', ''))
        expected_code = item.get('code', {})
        task_item_name = item.get('task_name', f'Task_{i}')
        test_set_name = item.get('test_set_name', 'Unknown')
        
        print(f"\nTest {i+1}/{len(test_data)} ({task_item_name}): {query[:50]}...")
        print(f"测试 {i+1}/{len(test_data)} ({task_item_name}): {query[:50]}...")
        
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
                
            elif method_name == 'few_shot_new':
                method_obj = baseline_manager.get_method('few_shot_new')
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
            
            # For now, we'll use a simple comparison approach
            # In a real implementation, you might want to use more sophisticated code comparison
            is_correct = False
            if code and expected_code:
                # Simple string comparison for now
                # You might want to implement more sophisticated code comparison
                is_correct = str(code).strip() == str(expected_code).strip()
            
            if is_correct:
                correct += 1
                print(f"  ✓ 正确 (Correct)")
            else:
                print(f"  ✗ 错误 (Incorrect)")
            
            detailed_results.append({
                'task_name': task_item_name,
                'test_set_name': test_set_name,
                'query': query,
                'generated_code': code,
                'expected_code': expected_code,
                'is_correct': is_correct,
                'method': method_name
            })
            
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            print(f"  ✗ Error: {e}")
            detailed_results.append({
                'task_name': task_item_name,
                'test_set_name': test_set_name,
                'query': query,
                'generated_code': '',
                'expected_code': expected_code,
                'is_correct': False,
                'method': method_name,
                'error': str(e)
            })
    
    return correct, detailed_results


def extract_code_from_response(response: str) -> str:
    """Extract code from LLM response"""
    """从LLM响应中提取代码"""
    if '[source code]' in response:
        return response.split('[source code]')[-1].strip()
    
    lines = response.split('\n')
    code_lines = []
    for line in lines:
        if not line.strip().startswith('#'):
            code_lines.append(line)
    return '\n'.join(code_lines).strip()


def print_task_evaluation_results(task_name: str, results: Dict[str, int], detailed_results: Dict[str, List[Dict]], total_samples: int):
    """Print evaluation results for a specific task"""
    """打印特定任务的评估结果"""
    
    print("\n" + "=" * 80)
    print(f"EVALUATION RESULTS FOR TASK: {task_name.upper()}")
    print(f"任务评估结果: {task_name.upper()}")
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
            'few_shot_new': 'Few-shot Prompting (Direct Data)',
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


def save_task_evaluation_results(task_name: str, results: Dict[str, int], detailed_results: Dict[str, List[Dict]], total_samples: int):
    """Save evaluation results for a specific task to JSON file"""
    """将特定任务的评估结果保存到JSON文件"""
    
    output_data = {
        'task_name': task_name,
        'evaluation_summary': {
            'total_samples': total_samples,
            'methods_evaluated': list(results.keys()),
            'results': results,
            'accuracies': {name: count/total_samples for name, count in results.items()}
        },
        'detailed_results': detailed_results,
        'config': {
            'dataset_source': 'split_sets',
            'max_samples': config.max_samples,
            'methods_to_run': config.methods_to_run,
            'use_real_llm': config.use_real_llm,
            'model_name': config.model_name if config.use_real_llm else 'Rule-based'
        }
    }
    
    # Create safe filename
    safe_task_name = task_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    output_file = f'task_{safe_task_name}_evaluation_results.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nTask results saved to: {output_file}")
    print(f"任务结果已保存到: {output_file}")


def evaluate_single_task(test_set: Dict, acecoder: AceCoderNew, generator: ImprovedCodeGenerator,
                        baseline_manager: BaselineMethodManager) -> Tuple[Dict[str, int], Dict[str, List[Dict]]]:
    """Evaluate all methods on a single task"""
    """在单个任务上评估所有方法"""
    
    task_name = test_set['test_set_name']
    print(f"\n{'='*80}")
    print(f"EVALUATING TASK: {task_name}")
    print(f"评估任务: {task_name}")
    print(f"{'='*80}")
    
    # Prepare training and test data for this task
    training_data_raw, test_data_raw = prepare_training_and_test_data_for_task(test_set)
    
    if not training_data_raw:
        print(f"警告: 任务 '{task_name}' 没有训练数据，跳过评估")
        print(f"Warning: Task '{task_name}' has no training data, skipping evaluation")
        return {}, {}
    
    if not test_data_raw:
        print(f"警告: 任务 '{task_name}' 没有测试数据，跳过评估")
        print(f"Warning: Task '{task_name}' has no test data, skipping evaluation")
        return {}, {}
    
    # Convert to evaluation format
    test_data = [create_evaluation_item(item) for item in test_data_raw]
    
    # Limit test samples if configured
    if len(test_data) > config.max_samples:
        test_data = random.sample(test_data, config.max_samples)
    
    # Initialize components with training data from this task only
    training_data_converted = convert_split_sets_to_training_data(training_data_raw)
    acecoder = AceCoderNew(training_data_converted)
    baseline_manager = BaselineMethodManager(training_data=training_data_converted)
    
    # Store results for all methods
    all_results = {}
    all_detailed_results = {}
    
    # Evaluate each configured method
    for method_name in config.methods_to_run:
        correct, detailed_results = evaluate_single_method_on_task(
            method_name, test_data, acecoder, generator, baseline_manager, task_name
        )
        all_results[method_name] = correct
        all_detailed_results[method_name] = detailed_results
    
    # Print results for this task
    print_task_evaluation_results(task_name, all_results, all_detailed_results, len(test_data))
    
    # Save results for this task
    save_task_evaluation_results(task_name, all_results, all_detailed_results, len(test_data))
    
    return all_results, all_detailed_results


def evaluate_split_sets():
    """Evaluate AceCoder on split_sets data - each file as separate task"""
    """在split_sets数据上评估AceCoder - 每个文件作为独立任务"""
    
    # 验证配置（跳过文件路径验证，因为我们使用split_sets数据）
    if config.use_real_llm and not config.api_key:
        print("Error: API key is required when use_real_llm is True")
        print("错误: 当 use_real_llm 为 True 时需要 API 密钥")
        return None
    
    if config.max_samples <= 0:
        print("Error: max_samples must be positive")
        print("错误: max_samples 必须为正数")
        return None
    
    # 验证方法配置
    available_methods = ['acecoder', 'zero_shot', 'few_shot', 'few_shot_new', 'cot']
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
    
    # Load split sets data
    print("Loading split sets data...")
    print("正在加载split sets数据...")
    test_sets = load_split_sets_data()
    
    if not test_sets:
        print("No test sets found. Exiting.")
        print("未找到测试集。退出。")
        return None
    
    # Initialize generator (will be reused for all tasks)
    generator = ImprovedCodeGenerator()
    
    if config.use_real_llm:
        print("Using real LLM API for code generation")
        print("使用真实LLM API进行代码生成")
    else:
        print("Using rule-based generator for code generation")
        print("使用基于规则的生成器进行代码生成")
    
    print(f"Found {len(test_sets)} tasks to evaluate")
    print(f"找到 {len(test_sets)} 个任务需要评估")
    print(f"Methods to evaluate: {', '.join(config.methods_to_run)}")
    print(f"评估方法: {', '.join(config.methods_to_run)}")
    
    # Store overall results
    all_task_results = {}
    all_task_detailed_results = {}
    
    # Evaluate each task separately
    for i, test_set in enumerate(test_sets):
        print(f"\n{'='*100}")
        print(f"TASK {i+1}/{len(test_sets)}: {test_set['test_set_name']}")
        print(f"任务 {i+1}/{len(test_sets)}: {test_set['test_set_name']}")
        print(f"{'='*100}")
        
        task_results, task_detailed_results = evaluate_single_task(
            test_set, None, generator, None  # acecoder and baseline_manager will be created per task
        )
        
        all_task_results[test_set['test_set_name']] = task_results
        all_task_detailed_results[test_set['test_set_name']] = task_detailed_results
    
    # Print overall summary
    print_overall_summary(all_task_results, all_task_detailed_results)
    
    return all_task_results, all_task_detailed_results


def print_overall_summary(all_task_results: Dict[str, Dict[str, int]], all_task_detailed_results: Dict[str, Dict[str, List[Dict]]]):
    """Print overall summary across all tasks"""
    """打印所有任务的总体摘要"""
    
    print("\n" + "=" * 100)
    print("OVERALL EVALUATION SUMMARY")
    print("总体评估摘要")
    print("=" * 100)
    
    # Calculate overall statistics
    total_tasks = len(all_task_results)
    methods = list(next(iter(all_task_results.values())).keys()) if all_task_results else []
    
    print(f"Total tasks evaluated: {total_tasks}")
    print(f"总评估任务数: {total_tasks}")
    print(f"Methods evaluated: {', '.join(methods)}")
    print(f"评估方法: {', '.join(methods)}")
    print()
    
    # Calculate average accuracies per method
    method_totals = {method: {'correct': 0, 'total': 0} for method in methods}
    
    for task_name, task_results in all_task_results.items():
        for method, correct in task_results.items():
            # Get total samples for this task
            task_detailed = all_task_detailed_results.get(task_name, {}).get(method, [])
            total_samples = len(task_detailed)
            
            method_totals[method]['correct'] += correct
            method_totals[method]['total'] += total_samples
    
    # Display overall results
    print("Overall Results (Average across all tasks):")
    print("总体结果（所有任务的平均值）:")
    print("-" * 80)
    
    for method in methods:
        if method_totals[method]['total'] > 0:
            accuracy = method_totals[method]['correct'] / method_totals[method]['total']
            display_name = {
                'acecoder': 'AceCoder',
                'zero_shot': 'Zero-shot Prompting',
                'few_shot': 'Few-shot Prompting',
                'few_shot_new': 'Few-shot Prompting (Direct Data)',
                'cot': 'Chain-of-Thought Prompting'
            }.get(method, method)
            
            print(f"{display_name:25s}: {method_totals[method]['correct']:3d}/{method_totals[method]['total']:3d} ({accuracy:.2%})")
    
    # Save overall results
    save_overall_results(all_task_results, all_task_detailed_results)


def save_overall_results(all_task_results: Dict[str, Dict[str, int]], all_task_detailed_results: Dict[str, Dict[str, List[Dict]]]):
    """Save overall results to JSON file"""
    """将总体结果保存到JSON文件"""
    
    output_data = {
        'overall_summary': {
            'total_tasks': len(all_task_results),
            'methods_evaluated': list(next(iter(all_task_results.values())).keys()) if all_task_results else [],
            'task_results': all_task_results,
            'detailed_results': all_task_detailed_results
        },
        'config': {
            'dataset_source': 'split_sets',
            'max_samples': config.max_samples,
            'methods_to_run': config.methods_to_run,
            'use_real_llm': config.use_real_llm,
            'model_name': config.model_name if config.use_real_llm else 'Rule-based'
        }
    }
    
    output_file = 'overall_split_sets_evaluation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nOverall results saved to: {output_file}")
    print(f"总体结果已保存到: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AceCoder evaluation on split_sets data - each file as separate task")
    parser.add_argument("--methods", nargs='+', choices=['acecoder', 'zero_shot', 'few_shot', 'few_shot_new', 'cot'],
                       default=['acecoder'], help="Methods to evaluate (default: acecoder)")
    parser.add_argument("--max-samples", type=int, default=10, 
                       help="Maximum number of test samples to evaluate per task (default: 10)")
    
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    random.seed(42)
    
    print("AceCoder Split Sets Evaluation Script - Per Task Evaluation")
    print("AceCoder Split Sets 评估脚本 - 按任务评估")
    print("=" * 60)
    
    # Configure the evaluation
    config.set_llm_config(
        use_real_llm=True,
        api_key="sk-67a3bbb61aee4bd19e51f45bbac8205d",
        model_name="deepseek-reasoner",
        api_base="https://api.deepseek.com/v1"
    )
    config.set_evaluation_config(
        max_samples=args.max_samples,
        dataset_path="split_sets",  # This will be ignored for split_sets
        training_data_path=""  # Not needed for split_sets evaluation
    )
    config.methods_to_run = args.methods
    
    try:
        evaluate_split_sets()
    except Exception as e:
        print(f"Evaluation failed: {e}")
        print(f"评估失败: {e}")
        import traceback
        traceback.print_exc() 