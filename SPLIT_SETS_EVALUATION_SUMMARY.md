# Split Sets 评估脚本修改总结

## 概述

已成功修改 `evaluate_codegen.py` 脚本，使其能够处理 `split_sets` 目录中的JSON文件进行代码生成评估。

## 主要修改内容

### 1. 新增数据加载功能

#### `load_split_sets_data(split_sets_dir: str = "split_sets") -> List[Dict]`
- 自动扫描 `split_sets` 目录中的所有JSON文件
- 解析每个文件的 `data` 字段
- 提取每个数据项的 `flag`、`content`、`code` 等关键字段
- 支持错误处理和文件验证

#### `prepare_training_and_test_data(test_sets: List[Dict]) -> Tuple[List[Dict], List[Dict]]`
- 根据 `flag` 字段分离训练和测试数据
- `flag: "train"` → 训练样本（用于检索相似记录）
- `flag: "test"` → 测试数据（用于评估）

#### `create_evaluation_item(item: Dict) -> Dict`
- 将原始数据项转换为评估格式
- 从 `content.src` 字段构建描述信息
- 提取 `code` 字段作为期望的输出

### 2. 修改评估逻辑

#### 更新 `evaluate_single_method` 函数
- 适配新的数据格式
- 支持测试集名称和任务名称显示
- 改进错误处理和结果记录

#### 更新 `evaluate_acecoder` 函数
- 优先使用 `split_sets` 数据
- 回退到原始MBPP数据集（如果split_sets不可用）
- 支持数据样本数量限制

### 3. 新增命令行参数

```bash
# 使用split_sets数据（默认）
python evaluate_codegen.py --eval --methods acecoder

# 强制使用MBPP数据集
python evaluate_codegen.py --eval --methods acecoder --mbpp

# 指定评估方法
python evaluate_codegen.py --eval --methods acecoder zero_shot few_shot
```

### 4. 创建专门的评估脚本

创建了 `evaluate_split_sets.py` 脚本，专门用于处理split_sets数据：

```bash
# 基本用法
python evaluate_split_sets.py

# 指定评估方法和样本数量
python evaluate_split_sets.py --methods acecoder zero_shot --max-samples 20
```

## 数据格式说明

### 输入数据格式
每个JSON文件包含：
```json
{
  "name": "测试集名称",
  "data": [
    {
      "flag": "train|test",
      "content": {
        "src": ["字段名/描述:类型;详细说明"],
        "dst": ["目标字段信息"]
      },
      "code": {
        "字段名": "转换表达式"
      },
      "task_name_old": "任务名称",
      "tags_old": ["标签"]
    }
  ]
}
```

### 评估数据格式
转换后的评估数据：
```json
{
  "prompt": "字段描述信息",
  "code": "期望的代码输出",
  "task_name": "任务名称",
  "test_set_name": "测试集名称",
  "source_file": "源文件路径"
}
```

## 使用方法

### 1. 使用修改后的主脚本

```bash
# 评估AceCoder方法
python evaluate_codegen.py --eval --methods acecoder

# 评估多个方法
python evaluate_codegen.py --eval --methods acecoder zero_shot few_shot

# 使用MBPP数据集（回退）
python evaluate_codegen.py --eval --methods acecoder --mbpp
```

### 2. 使用专门的split_sets脚本

```bash
# 默认评估（AceCoder，10个样本）
python evaluate_split_sets.py

# 自定义参数
python evaluate_split_sets.py --methods acecoder zero_shot --max-samples 20
```

## 输出结果

### 1. 控制台输出
- 数据加载进度
- 评估过程详情
- 最终结果统计
- 方法对比分析

### 2. 结果文件
- `split_sets_evaluation_results.json`：详细的评估结果
- 包含每个测试样本的详细信息
- 生成代码与期望代码的对比

## 测试结果示例

基于当前数据集的测试显示：
- 成功加载了4个测试集文件
- 每个文件包含163个数据项
- 总共268个训练样本，384个测试样本
- 支持多种评估方法（AceCoder、Zero-shot、Few-shot、CoT）

## 注意事项

1. **数据格式**：确保split_sets目录中的JSON文件格式正确
2. **API配置**：需要正确配置LLM API密钥和端点
3. **样本数量**：可以通过 `--max-samples` 参数控制评估样本数量
4. **回退机制**：如果split_sets不可用，会自动回退到MBPP数据集

## 未来改进方向

1. **代码比较优化**：实现更智能的代码比较算法
2. **训练数据集成**：直接使用split_sets中的训练数据进行检索
3. **多语言支持**：支持更多编程语言的代码生成评估
4. **性能优化**：优化大规模数据集的评估性能 