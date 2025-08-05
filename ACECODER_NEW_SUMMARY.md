# AceCoderNew 实现总结

## 概述

创建了新的 `acecoder_new.py` 文件，实现了能够直接通过训练数据初始化AceCoder的功能，而不需要从文件读取。

## 主要特性

### 1. 直接数据初始化
- **AceCoderNew**: 接受训练数据列表直接初始化
- **无需文件**: 不需要从文件路径加载数据
- **灵活格式**: 支持多种数据格式的转换

### 2. 数据格式转换
- **convert_split_sets_to_training_data()**: 将split_sets数据转换为AceCoder格式
- **自动处理**: 自动提取content字段并构建描述
- **兼容性**: 保持与原有AceCoder的API兼容

### 3. 核心功能保持
- **BM25检索**: 基于BM25算法的相似示例检索
- **示例选择**: 使用n-gram重叠的多样化示例选择
- **提示构建**: 构建<requirement, preliminary, code>三元组提示

## 类结构

### AceCoderNew
```python
class AceCoderNew:
    def __init__(self, training_data: List[Dict[str, Any]], *, use_lucene: bool = False, lucene_index_dir: str = "lucene_index")
    
    def prepare_retrieval_corpus(self)
    def retrieve_examples(self, query: str, top_k: int = 20) -> List[Tuple[str, str, List[str]]]
    def construct_prompt(self, query: str, k: int = 3) -> str
    def generate_code(self, query: str, model_generate_func, k: int = 3) -> str
    def evaluate_pass_at_k(self, test_queries: List[Dict], model_generate_func, k: int = 1) -> float
    def test_code(self, code: str, test_list: List[str]) -> bool
```

### 辅助函数
```python
def convert_split_sets_to_training_data(training_items: List[Dict]) -> List[Dict]
```

## 使用方法

### 1. 基本使用
```python
from acecoder_new import AceCoderNew

# 准备训练数据
training_data = [
    {
        'prompt': 'Write a function to find the maximum element in a list',
        'code': 'def find_max(lst):\n    return max(lst)',
        'test_list': ['assert find_max([1, 2, 3]) == 3']
    }
]

# 初始化AceCoderNew
acecoder = AceCoderNew(training_data)

# 构建提示
prompt = acecoder.construct_prompt("Write a function to find the minimum element in a list")
```

### 2. 与split_sets集成
```python
from acecoder_new import AceCoderNew, convert_split_sets_to_training_data

# 从split_sets获取训练数据
training_items = [...]  # split_sets中的训练项

# 转换为AceCoder格式
training_data = convert_split_sets_to_training_data(training_items)

# 初始化AceCoderNew
acecoder = AceCoderNew(training_data)
```

### 3. 在评估脚本中使用
```python
# 在evaluate_split_sets.py中
training_data_raw, test_data_raw = prepare_training_and_test_data(test_sets)
training_data_converted = convert_split_sets_to_training_data(training_data_raw)
acecoder = AceCoderNew(training_data_converted)
```

## 数据格式

### 输入格式（AceCoderNew期望）
```python
training_data = [
    {
        'prompt': '描述文本',  # 或 'text'
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

# 转换后的AceCoder格式
{
    'prompt': '字段名: 描述:类型;详细说明',
    'code': '{"字段名": "转换表达式"}',
    'test_list': []
}
```

## 优势对比

| 特性 | 原始AceCoder | AceCoderNew |
|------|-------------|-------------|
| 数据来源 | 文件路径 | 直接数据 |
| 初始化方式 | `AceCoder(file_path)` | `AceCoderNew(training_data)` |
| 灵活性 | 低 | 高 |
| 内存效率 | 中等 | 高 |
| 集成难度 | 中等 | 低 |

## 测试结果

### 功能测试
```bash
# 测试AceCoderNew基本功能
python acecoder_new.py

# 输出示例：
# Prepared retrieval corpus with 2 examples
# Query: Write a function to find the minimum element in a list
# Generated prompt: [requirement]... [test case]... [source code]...
```

### 集成测试
```bash
# 测试与evaluate_split_sets的集成
python evaluate_split_sets.py --max-samples 3

# 输出示例：
# Prepared retrieval corpus with 268 examples
# Evaluating on 3 test samples...
# AceCoder: 0/3 (0.00%)
```

## 性能特点

1. **快速初始化**: 直接使用内存中的数据，无需文件I/O
2. **内存高效**: 只加载必要的训练数据
3. **检索优化**: 基于BM25算法的快速相似性检索
4. **多样化选择**: 使用n-gram重叠确保示例多样性

## 使用建议

### 适用场景
- 需要动态加载训练数据的应用
- 内存受限的环境
- 需要频繁切换训练数据的场景
- 与split_sets数据集的集成

### 最佳实践
1. **数据预处理**: 在传入AceCoderNew之前预处理数据
2. **内存管理**: 对于大数据集，考虑分批处理
3. **错误处理**: 确保训练数据格式正确
4. **性能监控**: 监控检索和提示构建的性能

## 未来改进

1. **缓存机制**: 添加检索结果缓存
2. **并行处理**: 支持多线程检索
3. **更多检索算法**: 支持更多相似性算法
4. **动态更新**: 支持运行时更新训练数据 