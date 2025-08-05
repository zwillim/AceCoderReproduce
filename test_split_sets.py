#!/usr/bin/env python3
"""
Test script for split_sets data loading and processing
测试split_sets数据加载和处理功能
"""

import json
import os
import glob
from typing import List, Dict, Tuple

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


def analyze_data_structure():
    """Analyze the structure of the data"""
    """分析数据结构"""
    print("=" * 60)
    print("数据分析")
    print("Data Analysis")
    print("=" * 60)
    
    # Load data
    test_sets = load_split_sets_data()
    
    if not test_sets:
        print("没有找到测试集数据")
        return
    
    # Prepare training and test data
    training_data, test_data_raw = prepare_training_and_test_data(test_sets)
    
    # Convert to evaluation format
    test_data = [create_evaluation_item(item) for item in test_data_raw]
    
    print(f"\n转换后的测试数据: {len(test_data)} 个样本")
    print(f"Converted test data: {len(test_data)} samples")
    
    # Show some examples
    print(f"\n示例数据:")
    print(f"Sample data:")
    for i, item in enumerate(test_data[:3]):
        print(f"\n示例 {i+1}:")
        print(f"Sample {i+1}:")
        print(f"  任务名称: {item['task_name']}")
        print(f"  Task name: {item['task_name']}")
        print(f"  测试集: {item['test_set_name']}")
        print(f"  Test set: {item['test_set_name']}")
        print(f"  提示长度: {len(item['prompt'])} 字符")
        print(f"  Prompt length: {len(item['prompt'])} characters")
        print(f"  代码字段数: {len(item['code'])}")
        print(f"  Code fields: {len(item['code'])}")
        print(f"  提示预览: {item['prompt'][:100]}...")
        print(f"  Prompt preview: {item['prompt'][:100]}...")
    
    # Analyze flags distribution
    print(f"\n标志分布:")
    print(f"Flag distribution:")
    flag_counts = {}
    for test_set in test_sets:
        for item in test_set['items']:
            flag = item['flag']
            flag_counts[flag] = flag_counts.get(flag, 0) + 1
    
    for flag, count in flag_counts.items():
        print(f"  {flag}: {count} 个样本")
        print(f"  {flag}: {count} samples")


if __name__ == "__main__":
    analyze_data_structure() 