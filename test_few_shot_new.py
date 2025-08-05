#!/usr/bin/env python3
"""
Test script for FewShotPromptingNew class
测试FewShotPromptingNew类的脚本
"""

from baseline_methods import FewShotPromptingNew
from acecoder_new import convert_split_sets_to_training_data
import json
import glob
import os


def load_split_sets_data(split_sets_dir: str = "split_sets"):
    """Load training data from split_sets"""
    """从split_sets加载训练数据"""
    all_test_sets = []
    
    json_files = glob.glob(os.path.join(split_sets_dir, "*.json"))
    
    if not json_files:
        print(f"警告: 在 {split_sets_dir} 目录中未找到JSON文件")
        return []
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_set_name = data.get('name', os.path.basename(json_file))
            test_data = data.get('data', [])
            
            processed_items = []
            for item in test_data:
                flag = item.get('flag', 'test')
                if flag == 'train':  # 只使用训练数据
                    processed_items.append(item)
            
            all_test_sets.extend(processed_items)
            
        except Exception as e:
            print(f"错误: 无法加载文件 {json_file}: {e}")
            continue
    
    return all_test_sets


def test_few_shot_new():
    """Test FewShotPromptingNew with split_sets data"""
    """使用split_sets数据测试FewShotPromptingNew"""
    
    print("=" * 60)
    print("FewShotPromptingNew 测试")
    print("FewShotPromptingNew Test")
    print("=" * 60)
    
    # 加载split_sets训练数据
    print("正在加载split_sets训练数据...")
    print("Loading split_sets training data...")
    training_items = load_split_sets_data()
    
    if not training_items:
        print("没有找到训练数据")
        print("No training data found")
        return
    
    print(f"找到 {len(training_items)} 个训练样本")
    print(f"Found {len(training_items)} training samples")
    
    # 转换为AceCoder格式
    training_data = convert_split_sets_to_training_data(training_items)
    print(f"转换为AceCoder格式后: {len(training_data)} 个样本")
    print(f"After conversion to AceCoder format: {len(training_data)} samples")
    
    # 创建FewShotPromptingNew实例
    print("\n创建FewShotPromptingNew实例...")
    print("Creating FewShotPromptingNew instance...")
    few_shot_new = FewShotPromptingNew(training_data=training_data, num_examples=3)
    
    # 测试查询
    test_query = "Write a function to process user data with field mapping"
    print(f"\n测试查询: {test_query}")
    print(f"Test query: {test_query}")
    
    # 生成提示
    prompt = few_shot_new.create_prompt(test_query)
    print("\n生成的提示:")
    print("Generated prompt:")
    print("-" * 40)
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    print("-" * 40)
    
    # 显示使用的示例
    print(f"\n使用的示例数量: {len(few_shot_new.examples)}")
    print(f"Number of examples used: {len(few_shot_new.examples)}")
    
    for i, example in enumerate(few_shot_new.examples[:2], 1):
        print(f"\n示例 {i}:")
        print(f"Example {i}:")
        print(f"  文本: {example['text'][:100]}...")
        print(f"  Text: {example['text'][:100]}...")
        print(f"  代码长度: {len(example['code'])} 字符")
        print(f"  Code length: {len(example['code'])} characters")
    
    # 测试更新训练数据
    print("\n测试更新训练数据...")
    print("Testing training data update...")
    
    # 创建新的训练数据
    new_training_data = [
        {
            'prompt': 'Write a function to validate email format',
            'code': 'def validate_email(email):\n    import re\n    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"\n    return re.match(pattern, email) is not None',
            'test_list': ['assert validate_email("test@example.com") == True', 'assert validate_email("invalid-email") == False']
        },
        {
            'prompt': 'Write a function to calculate factorial',
            'code': 'def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)',
            'test_list': ['assert factorial(5) == 120', 'assert factorial(0) == 1']
        }
    ]
    
    # 更新训练数据
    few_shot_new.update_training_data(new_training_data)
    print(f"更新后使用的示例数量: {len(few_shot_new.examples)}")
    print(f"Number of examples after update: {len(few_shot_new.examples)}")
    
    # 生成新的提示
    new_prompt = few_shot_new.create_prompt(test_query)
    print("\n更新后生成的提示:")
    print("Generated prompt after update:")
    print("-" * 40)
    print(new_prompt[:1000] + "..." if len(new_prompt) > 1000 else new_prompt)
    print("-" * 40)


def test_without_training_data():
    """Test FewShotPromptingNew without training data (uses default examples)"""
    """测试FewShotPromptingNew不使用训练数据（使用默认示例）"""
    
    print("\n" + "=" * 60)
    print("FewShotPromptingNew 无训练数据测试")
    print("FewShotPromptingNew Test Without Training Data")
    print("=" * 60)
    
    # 创建FewShotPromptingNew实例（无训练数据）
    few_shot_new = FewShotPromptingNew()
    
    test_query = "Write a function to find the maximum element in a list"
    print(f"测试查询: {test_query}")
    print(f"Test query: {test_query}")
    
    # 生成提示
    prompt = few_shot_new.create_prompt(test_query)
    print("\n生成的提示:")
    print("Generated prompt:")
    print("-" * 40)
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    print("-" * 40)
    
    print(f"使用的默认示例数量: {len(few_shot_new.examples)}")
    print(f"Number of default examples used: {len(few_shot_new.examples)}")


if __name__ == "__main__":
    test_few_shot_new()
    test_without_training_data() 