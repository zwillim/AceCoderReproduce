# AceCoder 配置指南

本指南将帮助你通过修改配置来设置 API 密钥等信息，而不需要使用命令行参数。

## 1. 环境变量配置

### 创建环境变量文件

创建 `.env` 文件（或设置系统环境变量）：

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置文件
nano .env
```

### 环境变量列表

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `ACECODER_USE_REAL_LLM` | 是否使用真实 LLM | `false` | `true` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | 无 | `sk-...` |
| `ACECODER_API_KEY` | 备用 API 密钥 | 无 | `sk-...` |
| `ACECODER_MODEL_NAME` | 模型名称 | `gpt-3.5-turbo` | `gpt-4` |
| `ACECODER_API_BASE` | API 基础 URL | `https://api.openai.com/v1` | `https://your-api.com/v1` |
| `ACECODER_MAX_SAMPLES` | 最大评估样本数 | `10` | `5` |
| `ACECODER_DATASET_PATH` | 数据集路径 | `BMPP/sanitized-mbpp.json` | `path/to/dataset.json` |
| `ACECODER_TRAINING_DATA_PATH` | 训练数据路径 | `BMPP/mbpp.jsonl` | `path/to/training.jsonl` |
| `ACECODER_TEMPERATURE` | 生成温度 | `0.1` | `0.2` |
| `ACECODER_MAX_TOKENS` | 最大令牌数 | `1000` | `1500` |

## 2. 配置示例

### 示例 1: 使用规则生成器（默认）

```bash
# .env 文件内容
ACECODER_USE_REAL_LLM=false
ACECODER_MAX_SAMPLES=10
```

### 示例 2: 使用 GPT-3.5-turbo

```bash
# .env 文件内容
ACECODER_USE_REAL_LLM=true
OPENAI_API_KEY=sk-your-api-key-here
ACECODER_MODEL_NAME=gpt-3.5-turbo
ACECODER_MAX_SAMPLES=5
ACECODER_TEMPERATURE=0.1
```

### 示例 3: 使用 GPT-4

```bash
# .env 文件内容
ACECODER_USE_REAL_LLM=true
OPENAI_API_KEY=sk-your-api-key-here
ACECODER_MODEL_NAME=gpt-4
ACECODER_MAX_SAMPLES=3
ACECODER_TEMPERATURE=0.1
```

### 示例 4: 使用自定义 API 端点

```bash
# .env 文件内容
ACECODER_USE_REAL_LLM=true
OPENAI_API_KEY=your-api-key
ACECODER_API_BASE=https://your-api-endpoint.com/v1
ACECODER_MODEL_NAME=your-model-name
ACECODER_MAX_SAMPLES=5
```

## 3. 系统环境变量设置

### Linux/macOS

```bash
# 临时设置（当前会话有效）
export ACECODER_USE_REAL_LLM=true
export OPENAI_API_KEY="sk-your-api-key-here"
export ACECODER_MODEL_NAME="gpt-4"
export ACECODER_MAX_SAMPLES=5

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export ACECODER_USE_REAL_LLM=true' >> ~/.bashrc
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
echo 'export ACECODER_MODEL_NAME="gpt-4"' >> ~/.bashrc
echo 'export ACECODER_MAX_SAMPLES=5' >> ~/.bashrc
source ~/.bashrc
```

### Windows

```cmd
# 临时设置（当前会话有效）
set ACECODER_USE_REAL_LLM=true
set OPENAI_API_KEY=sk-your-api-key-here
set ACECODER_MODEL_NAME=gpt-4
set ACECODER_MAX_SAMPLES=5

# 永久设置（系统环境变量）
# 通过系统设置 -> 环境变量 添加
```

## 4. 运行评估

配置完成后，直接运行：

```bash
python evaluate_acecoder.py
```

程序会自动：
1. 加载环境变量配置
2. 验证配置有效性
3. 打印当前配置
4. 执行评估

## 5. 配置验证

程序会验证以下配置：

- ✅ API 密钥（当使用真实 LLM 时）
- ✅ 数据集文件存在
- ✅ 训练数据文件存在
- ✅ 数值参数有效性

## 6. 故障排除

### 配置未生效
```bash
# 检查环境变量是否正确设置
echo $ACECODER_USE_REAL_LLM
echo $OPENAI_API_KEY
```

### API 密钥错误
```
Error: API key is required when use_real_llm is True
```
**解决方案**: 确保设置了 `OPENAI_API_KEY` 或 `ACECODER_API_KEY`

### 文件路径错误
```
Error: Dataset file not found: BMPP/sanitized-mbpp.json
```
**解决方案**: 检查数据集文件路径是否正确

### 数值参数错误
```
Warning: Invalid ACECODER_MAX_SAMPLES value: abc
```
**解决方案**: 确保数值参数为有效数字

## 7. 高级配置

### 自定义数据集
```bash
ACECODER_DATASET_PATH=path/to/your/dataset.json
ACECODER_TRAINING_DATA_PATH=path/to/your/training.jsonl
```

### 调整生成参数
```bash
ACECODER_TEMPERATURE=0.2      # 增加创造性
ACECODER_MAX_TOKENS=1500      # 增加输出长度
```

### 使用不同模型
```bash
ACECODER_MODEL_NAME=gpt-4-turbo    # 最新模型
ACECODER_MODEL_NAME=gpt-3.5-turbo  # 经济模型
```

## 8. 安全建议

1. **不要提交 API 密钥到版本控制**
   ```bash
   # 确保 .env 在 .gitignore 中
   echo ".env" >> .gitignore
   ```

2. **使用环境变量而不是硬编码**
   ```bash
   # 正确
   export OPENAI_API_KEY="sk-..."
   
   # 错误
   # 不要在代码中硬编码 API 密钥
   ```

3. **定期轮换 API 密钥**
   - 定期更新 API 密钥
   - 监控 API 使用情况
   - 设置使用限制

## 9. 成本控制

### 估算成本
- **GPT-3.5-turbo**: ~$0.05-0.10 (10个样本)
- **GPT-4**: ~$1.00-2.00 (10个样本)

### 节省成本的建议
1. 先用小样本测试：`ACECODER_MAX_SAMPLES=3`
2. 使用经济模型：`ACECODER_MODEL_NAME=gpt-3.5-turbo`
3. 降低温度参数：`ACECODER_TEMPERATURE=0.1`
4. 限制输出长度：`ACECODER_MAX_TOKENS=500` 