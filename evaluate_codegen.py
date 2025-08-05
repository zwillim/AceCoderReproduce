#!/usr/bin/env python3
"""
Evaluation script for AceCoder on MBPP dataset
MBPP数据集上的AceCoder评估脚本
"""

import json
import random
import os
import glob
from typing import List, Dict, Optional, Tuple
from acecoder import AceCoder
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
    
    print(f"找到 {len(json_files)} 个测试集文件")
    print(f"Found {len(json_files)} test set files")
    
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


def prepare_training_and_test_data(test_sets: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Separate training and test data from all test sets"""
    """从所有测试集中分离训练和测试数据"""
    training_data = []
    test_data = []
    
    for test_set in test_sets:
        for item in test_set['items']:
            if item['flag'] == 'train':
                training_data.append(item)
            elif item['flag'] == 'test':
                test_data.append(item)
    
    print(f"训练数据: {len(training_data)} 个样本")
    print(f"Training data: {len(training_data)} samples")
    print(f"测试数据: {len(test_data)} 个样本")
    print(f"Test data: {len(test_data)} samples")
    
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
        expected_code = item.get('code', {})
        task_name = item.get('task_name', f'Task_{i}')
        test_set_name = item.get('test_set_name', 'Unknown')
        
        print(f"\nTest {i+1}/{len(test_data)} ({test_set_name} - {task_name}): {query[:50]}...")
        print(f"测试 {i+1}/{len(test_data)} ({test_set_name} - {task_name}): {query[:50]}...")
        
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
                'task_name': task_name,
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
                'task_name': task_name,
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


def evaluate_acecoder():
    """Evaluate AceCoder with configurable methods"""
    """使用可配置方法评估AceCoder"""
    
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
    
    # Load split sets data
    print("Loading split sets data...")
    print("正在加载split sets数据...")
    test_sets = load_split_sets_data()
    
    if not test_sets:
        print("No test sets found. Falling back to original MBPP dataset.")
        print("未找到测试集。回退到原始MBPP数据集。")
        
        # Fallback to original method
        acecoder = AceCoder(config.training_data_path)
        generator = ImprovedCodeGenerator()
        baseline_manager = BaselineMethodManager(config.training_data_path)
        
        # Load test data
        print("Loading test data...")
        print("正在加载测试数据...")
        test_data = load_test_data(config.dataset_path, max_samples=config.max_samples)
    else:
        # Prepare training and test data from split sets
        training_data, test_data_raw = prepare_training_and_test_data(test_sets)
        
        # Convert to evaluation format
        test_data = [create_evaluation_item(item) for item in test_data_raw]
        
        # Limit test samples if configured
        if len(test_data) > config.max_samples:
            test_data = random.sample(test_data, config.max_samples)
        
        # Initialize components with training data
        # Note: We'll need to modify AceCoder to accept training data directly
        # For now, we'll use the original approach
        acecoder = AceCoder(config.training_data_path)
        generator = ImprovedCodeGenerator()
        baseline_manager = BaselineMethodManager(config.training_data_path)
    
    if config.use_real_llm:
        print("Using real LLM API for code generation")
        print("使用真实LLM API进行代码生成")
    else:
        print("Using rule-based generator for code generation")
        print("使用基于规则的生成器进行代码生成")
    
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
    
    output_file = 'evaluation_results.json'
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
    # 初始化AceCoder
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    # Example query
    # 示例查询
    query = "Write a function to find the shared elements from the given two lists."
    
    print(f"Query: {query}")
    print(f"查询: {query}")
    print("\nConstructing AceCoder prompt...")
    print("\n正在构建 AceCoder 提示...")
    
    # Construct prompt
    # 构建提示
    prompt = acecoder.construct_prompt(query, k=3)
    
    print("\nGenerated AceCoder Prompt:")
    print("\n生成的 AceCoder 提示:")
    print("-" * 40)
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    print("-" * 40)
    
    # Show how the prompt would be used
    # 展示如何使用提示
    generator = ImprovedCodeGenerator()
    response = generator.generate(prompt)
    
    print(f"\nGenerated Response:")
    print(f"\n生成的响应:")
    print(response)
    
    # Test the generated code
    # 测试生成的代码
    test_cases = [
        "assert set(shared_elements([1, 2, 3, 4], [3, 4, 5, 6])) == set([3, 4])",
        "assert set(shared_elements([1, 2], [3, 4])) == set([])"
    ]
    
    try:
        # Remove comments from response
        # 从响应中移除注释
        lines = response.split('\n')
        code_lines = []
        for line in lines:
            if not line.strip().startswith('#'):
                code_lines.append(line)
        code = '\n'.join(code_lines).strip()
        
        print(f"\nTesting generated code...")
        print(f"\n正在测试生成的代码...")
        exec_globals = {}
        exec(code, exec_globals)
        
        all_passed = True
        for test in test_cases:
            try:
                exec(test, exec_globals)
                print(f"  ✓ {test}")
            except Exception as e:
                print(f"  ✗ {test} - {e}")
                all_passed = False
        
        if all_passed:
            print("All tests passed!")
            print("所有测试通过!")
        else:
            print("Some tests failed.")
            print("部分测试失败。")
            
    except Exception as e:
        print(f"Code execution failed: {e}")
        print(f"代码执行失败: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AceCoder evaluation with configurable methods")
    parser.add_argument("--demo", action="store_true", help="Run AceCoder demonstration")
    parser.add_argument("--eval", action="store_true", help="Run evaluation")
    parser.add_argument("--methods", nargs='+', choices=['acecoder', 'zero_shot', 'few_shot', 'cot'],
                       help="Override methods to run (e.g., --methods acecoder zero_shot)")
    parser.add_argument("--split-sets", action="store_true", 
                       help="Use split_sets directory for evaluation (default)")
    parser.add_argument("--mbpp", action="store_true", 
                       help="Use original MBPP dataset for evaluation")
    
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    # 设置随机种子以确保可重现性
    random.seed(42)
    
    print("AceCoder Evaluation Script")
    print("AceCoder 评估脚本")
    print("=" * 60)
    
    # =============================================================================
    # 配置方式1: 使用配置函数（推荐）
    # Configuration Method 1: Use configuration functions (recommended)
    # =============================================================================
    
    # 取消注释下面的行来使用不同的配置
    # Uncomment the lines below to use different configurations
    
    # 从 config_examples.py 导入配置函数
    # from config_examples import example_rule_based, example_gpt35, example_gpt4
    
    # 选择你想要的配置：
    # Choose the configuration you want:
    
    # example_rule_based()      # 规则生成器（免费，快速）
    # example_gpt35()          # GPT-3.5-turbo（经济选择）
    # example_gpt4()           # GPT-4（高质量选择）
    
    # =============================================================================
    # 配置方式2: 直接在代码中配置
    # Configuration Method 2: Configure directly in code
    # =============================================================================
    
    # 示例1: 使用规则生成器（默认）
    # Example 1: Use rule-based generator (default)
    config.set_llm_config(
        use_real_llm=True,  # 不使用真实LLM
        api_key="sk-67a3bbb61aee4bd19e51f45bbac8205d",        # 不需要API密钥
        model_name="deepseek-reasoner",
        api_base="https://api.deepseek.com/v1"
    )
    config.set_evaluation_config(
        max_samples=10,      # 评估10个样本
        dataset_path="BMPP/sanitized-mbpp.json",
        training_data_path="BMPP/mbpp.jsonl"
    )
    
    # 示例2: 使用真实LLM API（取消注释下面的代码）
    # Example 2: Use real LLM API (uncomment the code below)
    # config.set_llm_config(
    #     use_real_llm=True,                    # 使用真实LLM
    #     api_key="sk-your-api-key-here",      # 你的OpenAI API密钥
    #     model_name="gpt-4",                  # 使用GPT-4模型
    #     api_base="https://api.openai.com/v1"
    # )
    # config.set_evaluation_config(
    #     max_samples=5,                       # 评估5个样本（节省成本）
    #     dataset_path="BMPP/sanitized-mbpp.json",
    #     training_data_path="BMPP/mbpp.jsonl"
    # )
    # config.set_generator_config(
    #     temperature=0.1,                     # 低温度，更确定性
    #     max_tokens=1000                      # 最大1000个令牌
    # )
    
    # 示例3: 使用自定义API端点（如Azure OpenAI）
    # Example 3: Use custom API endpoint (like Azure OpenAI)
    # config.set_llm_config(
    #     use_real_llm=True,
    #     api_key="your-azure-api-key",
    #     model_name="gpt-4",
    #     api_base="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
    # )
    # config.set_evaluation_config(max_samples=3)
    
    # Override methods if specified
    if args.methods:
        config.methods_to_run = args.methods
        print(f"Overriding methods to run: {args.methods}")
        print(f"覆盖运行方法: {args.methods}")
    
    # Determine evaluation mode
    if args.mbpp:
        print("Using MBPP dataset for evaluation")
        print("使用MBPP数据集进行评估")
        # Force use of original MBPP dataset
        config.dataset_path = "BMPP/sanitized-mbpp.json"
        config.training_data_path = "BMPP/mbpp.jsonl"
    else:
        print("Using split_sets directory for evaluation (default)")
        print("使用split_sets目录进行评估（默认）")
    
    if args.demo:
        demo_acecoder()
    elif args.eval:
        try:
            evaluate_acecoder()
        except Exception as e:
            print(f"Evaluation failed: {e}")
            print(f"评估失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Default behavior - run both demo and evaluation
        demo_acecoder()
        try:
            evaluate_acecoder()
        except Exception as e:
            print(f"Evaluation failed: {e}")
            print(f"评估失败: {e}")
            import traceback
            traceback.print_exc()