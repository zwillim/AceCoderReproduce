# AceCoder 快速开始指南

## 在 main 方法中直接配置

### 方法1: 使用配置函数（推荐）

1. **编辑 `evaluate_acecoder.py`**
2. **取消注释并选择配置函数**：

```python
# 在 main 方法中，取消注释下面的行：
from config_examples import example_rule_based, example_gpt35, example_gpt4

# 选择你想要的配置：
example_rule_based()      # 规则生成器（免费，快速）
# example_gpt35()          # GPT-3.5-turbo（经济选择）
# example_gpt4()           # GPT-4（高质量选择）
```

### 方法2: 直接在代码中配置

在 `evaluate_acecoder.py` 的 main 方法中直接设置：

```python
# 规则生成器配置
config.set_llm_config(
    use_real_llm=False,  # 不使用真实LLM
    api_key=None,        # 不需要API密钥
    model_name="gpt-3.5-turbo"
)
config.set_evaluation_config(
    max_samples=10,      # 评估10个样本
    dataset_path="BMPP/sanitized-mbpp.json",
    training_data_path="BMPP/mbpp.jsonl"
)

# 或者使用真实LLM配置
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
```

## 配置选项

### 1. 规则生成器（免费）
```python
config.set_llm_config(use_real_llm=False)
config.set_evaluation_config(max_samples=10)
```

### 2. GPT-3.5-turbo（经济）
```python
config.set_llm_config(
    use_real_llm=True,
    api_key="sk-your-api-key-here",
    model_name="gpt-3.5-turbo"
)
config.set_evaluation_config(max_samples=5)
```

### 3. GPT-4（高质量）
```python
config.set_llm_config(
    use_real_llm=True,
    api_key="sk-your-api-key-here",
    model_name="gpt-4"
)
config.set_evaluation_config(max_samples=3)
```

### 4. Azure OpenAI
```python
config.set_llm_config(
    use_real_llm=True,
    api_key="your-azure-api-key",
    model_name="gpt-4",
    api_base="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
)
config.set_evaluation_config(max_samples=5)
```

## 运行评估

配置完成后，直接运行：

```bash
python evaluate_acecoder.py
```

## 测试配置

在运行评估之前，可以先测试配置：

```bash
python test_config.py
```

## 查看所有配置示例

```bash
python config_examples.py
```

## 成本估算

| 配置 | 样本数 | 预估成本 |
|------|--------|----------|
| 规则生成器 | 10 | $0 |
| GPT-3.5-turbo | 5 | $0.05-0.10 |
| GPT-4 | 3 | $1.00-2.00 |
| GPT-4 | 10 | $3.00-5.00 |

## 故障排除

### 1. API 密钥错误
```
Error: API key is required when use_real_llm is True
```
**解决方案**: 确保设置了正确的 API 密钥

### 2. 文件路径错误
```
Error: Dataset file not found
```
**解决方案**: 检查数据集文件路径是否正确

### 3. 网络错误
```
Error calling real LLM: Connection timeout
```
**解决方案**: 检查网络连接，或使用代理

## 安全建议

1. **不要在代码中硬编码 API 密钥**
2. **使用环境变量或配置文件**
3. **定期轮换 API 密钥**
4. **监控 API 使用情况** 