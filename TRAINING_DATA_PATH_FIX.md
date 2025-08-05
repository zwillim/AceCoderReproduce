# Training Data Path 依赖问题修复

## 问题描述

在 `evaluate_split_sets.py` 脚本中，虽然我们已经实现了使用split_sets数据的功能，但仍然存在对 `training_data_path` 的依赖：

1. **BaselineMethodManager** 初始化时使用了 `config.training_data_path`
2. **配置验证** 检查 `training_data_path` 文件是否存在
3. **配置设置** 仍然设置了不必要的 `training_data_path`

## 修复过程

### 1. 修复 BaselineMethodManager 初始化

**问题**：
```python
baseline_manager = BaselineMethodManager(config.training_data_path)
```

**修复**：
```python
# For baseline methods, we don't need training data path since we're mainly using AceCoder
baseline_manager = BaselineMethodManager()
```

**原因**：
- 在split_sets评估中，我们主要使用AceCoder方法
- 基线方法（zero_shot, few_shot, cot）只是作为对比
- FewShotPrompting 有内置的固定示例，不需要外部训练数据

### 2. 修复配置验证

**问题**：
```python
# 验证配置
if not config.validate():
    print("Configuration validation failed. Please check your settings.")
    print("配置验证失败。请检查您的设置。")
    return None
```

**修复**：
```python
# 验证配置（跳过文件路径验证，因为我们使用split_sets数据）
if config.use_real_llm and not config.api_key:
    print("Error: API key is required when use_real_llm is True")
    print("错误: 当 use_real_llm 为 True 时需要 API 密钥")
    return None

if config.max_samples <= 0:
    print("Error: max_samples must be positive")
    print("错误: max_samples 必须为正数")
    return None
```

**原因**：
- `config.validate()` 检查 `training_data_path` 文件是否存在
- 对于split_sets评估，我们不需要这个验证
- 只需要验证API密钥和样本数量等必要参数

### 3. 修复配置设置

**问题**：
```python
config.set_evaluation_config(
    max_samples=args.max_samples,
    dataset_path="split_sets",  # This will be ignored for split_sets
    training_data_path="BMPP/mbpp.jsonl"  # Fallback training data
)
```

**修复**：
```python
config.set_evaluation_config(
    max_samples=args.max_samples,
    dataset_path="split_sets",  # This will be ignored for split_sets
    training_data_path=""  # Not needed for split_sets evaluation
)
```

**原因**：
- 对于split_sets评估，不需要training_data_path
- 设置为空字符串避免不必要的文件检查

## 修复后的优势

### 1. 完全独立
- 不再依赖MBPP数据集文件
- 完全使用split_sets中的数据
- 避免了文件路径验证错误

### 2. 更清晰的架构
- AceCoderNew 直接使用训练数据
- BaselineMethodManager 使用内置示例
- 配置验证只检查必要参数

### 3. 更好的错误处理
- 避免了"找不到训练数据文件"的错误
- 提供了更准确的错误信息
- 简化了配置流程

## 测试结果

### 修复前
```bash
$ python evaluate_split_sets.py --max-samples 2
Error: Training data file not found: 
错误: 找不到训练数据文件: 
Configuration validation failed. Please check your settings.
配置验证失败。请检查您的设置。
```

### 修复后
```bash
$ python evaluate_split_sets.py --max-samples 2
AceCoder Split Sets Evaluation Script
AceCoder Split Sets 评估脚本
============================================================
...
Prepared retrieval corpus with 268 examples
已准备包含 268 个示例的检索语料库
...
Evaluating on 2 test samples...
正在评估 2 个测试样本...
```

## 代码变更总结

### 修改的文件
1. **evaluate_split_sets.py**
   - 移除 `BaselineMethodManager` 的 `training_data_path` 参数
   - 自定义配置验证逻辑
   - 设置空的 `training_data_path`

### 关键变更
```python
# 之前
baseline_manager = BaselineMethodManager(config.training_data_path)
if not config.validate():
    return None

# 之后
baseline_manager = BaselineMethodManager()
if config.use_real_llm and not config.api_key:
    return None
```

## 最佳实践

### 1. 数据源分离
- 不同评估脚本使用不同的数据源
- 避免不必要的文件依赖
- 提供清晰的错误信息

### 2. 配置验证
- 只验证必要的参数
- 根据具体用途定制验证逻辑
- 提供有意义的错误消息

### 3. 组件初始化
- 根据实际需要初始化组件
- 避免传递不必要的参数
- 使用默认值或内置数据

## 未来改进

1. **配置类扩展**：为split_sets评估创建专门的配置类
2. **验证策略**：实现可插拔的验证策略
3. **组件工厂**：使用工厂模式创建不同的组件实例
4. **错误处理**：提供更详细的错误信息和恢复建议 