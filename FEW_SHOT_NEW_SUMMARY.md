# FewShotPromptingNew 类实现总结

## 概述

在 `baseline_methods.py` 中新增了 `FewShotPromptingNew` 类，实现了能够直接使用训练数据集而不是从目录中读取的 few-shot 提示方法。

## 主要特性

### 1. 直接数据初始化
- **无需文件路径**：直接接受训练数据列表
- **灵活格式**：支持多种数据格式
- **动态更新**：支持运行时更新训练数据

### 2. 智能示例选择
- **自动选择**：从训练数据中自动选择示例
- **数量控制**：可配置使用的示例数量
- **默认回退**：当训练数据不足时使用默认示例

### 3. 向后兼容
- **默认示例**：当没有提供训练数据时使用内置示例
- **API兼容**：与原有FewShotPrompting保持相同的接口

## 类结构

### FewShotPromptingNew
```python
class FewShotPromptingNew(BaselineMethod):
    def __init__(self, training_data: List[Dict] = None, num_examples: int = 3)
    def _prepare_examples(self) -> List[Dict]
    def _get_default_examples(self) -> List[Dict]
    def create_prompt(self, query: str, **kwargs) -> str
    def update_training_data(self, new_training_data: List[Dict])
```

## 使用方法

### 1. 基本使用（无训练数据）
```python
from baseline_methods import FewShotPromptingNew

# 使用默认示例
few_shot = FewShotPromptingNew()
prompt = few_shot.create_prompt("Write a function to find the maximum element")
```

### 2. 使用训练数据
```python
# 准备训练数据
training_data = [
    {
        'prompt': 'Write a function to validate email',
        'code': 'def validate_email(email):\n    import re\n    return re.match(r"^[^@]+@[^@]+\\.[^@]+$", email) is not None',
        'test_list': ['assert validate_email("test@example.com") == True']
    }
]

# 创建实例
few_shot = FewShotPromptingNew(training_data=training_data, num_examples=2)
prompt = few_shot.create_prompt("Write a function to validate phone number")
```

### 3. 与split_sets集成
```python
from acecoder_new import convert_split_sets_to_training_data

# 转换split_sets数据
training_data = convert_split_sets_to_training_data(training_items)

# 创建实例
few_shot = FewShotPromptingNew(training_data=training_data)
prompt = few_shot.create_prompt("Write a function to process user data")
```

### 4. 动态更新训练数据
```python
# 更新训练数据
new_training_data = [
    {
        'prompt': 'Write a function to calculate factorial',
        'code': 'def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)',
        'test_list': ['assert factorial(5) == 120']
    }
]

few_shot.update_training_data(new_training_data)
```

## 在评估脚本中使用

### 1. 更新BaselineMethodManager
```python
# 在evaluate_split_sets.py中
baseline_manager = BaselineMethodManager(training_data=training_data_converted)
```

### 2. 支持新的方法名
```bash
# 使用新的few_shot_new方法
python evaluate_split_sets.py --methods few_shot_new --max-samples 5
```

### 3. 方法名称映射
```python
display_name = {
    'acecoder': 'AceCoder',
    'zero_shot': 'Zero-shot Prompting',
    'few_shot': 'Few-shot Prompting', 
    'few_shot_new': 'Few-shot Prompting (Direct Data)',
    'cot': 'Chain-of-Thought Prompting'
}
```

## 数据格式

### 输入格式
```python
training_data = [
    {
        'prompt': '问题描述',  # 或 'text'
        'code': '代码字符串',
        'test_list': ['测试用例1', '测试用例2']  # 可选
    }
]
```

### split_sets格式转换
```python
# 原始split_sets格式
{
    'flag': 'train',
    'content': {
        'src': ['字段名/描述:类型;详细说明']
    },
    'code': {
        '字段名': '转换表达式'
    }
}

# 转换后的格式
{
    'prompt': '字段名: 描述:类型;详细说明',
    'code': '{"字段名": "转换表达式"}',
    'test_list': []
}
```

## 优势对比

| 特性 | 原始FewShotPrompting | FewShotPromptingNew |
|------|---------------------|-------------------|
| 数据来源 | 文件路径 | 直接数据 |
| 初始化方式 | `FewShotPrompting(file_path)` | `FewShotPromptingNew(training_data)` |
| 灵活性 | 低 | 高 |
| 动态更新 | 不支持 | 支持 |
| 内存效率 | 中等 | 高 |
| 集成难度 | 中等 | 低 |

## 测试结果

### 功能测试
```bash
# 测试FewShotPromptingNew基本功能
python test_few_shot_new.py

# 输出示例：
# 找到 268 个训练样本
# 转换为AceCoder格式后: 268 个样本
# 使用的示例数量: 3
```

### 集成测试
```bash
# 测试与evaluate_split_sets的集成
python evaluate_split_sets.py --methods few_shot_new --max-samples 2

# 输出示例：
# Few-shot Prompting (Direct Data): 0/2 (0.00%)
```

## 性能特点

1. **快速初始化**：直接使用内存中的数据，无需文件I/O
2. **内存高效**：只加载必要的训练数据
3. **动态更新**：支持运行时更新训练数据
4. **智能选择**：自动从训练数据中选择合适的示例

## 使用建议

### 适用场景
- 需要动态加载训练数据的应用
- 内存受限的环境
- 需要频繁切换训练数据的场景
- 与split_sets数据集的集成

### 最佳实践
1. **数据预处理**：在传入FewShotPromptingNew之前预处理数据
2. **示例数量**：根据任务复杂度调整num_examples参数
3. **错误处理**：确保训练数据格式正确
4. **性能监控**：监控提示生成的性能

## 未来改进

1. **智能示例选择**：基于查询相似性选择最相关的示例
2. **示例多样性**：确保选择的示例具有足够的多样性
3. **缓存机制**：添加提示生成结果缓存
4. **并行处理**：支持多线程示例选择 