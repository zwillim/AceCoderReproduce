# 使用真实 LLM API 的 AceCoder 评估

本指南将帮助你使用真实的 LLM API 来运行 AceCoder 评估。

## 1. 设置 API 密钥

### 方法 1: 环境变量（推荐）
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 方法 2: 命令行参数
```bash
python evaluate_acecoder.py --use-real-llm --api-key "your-api-key-here"
```

## 2. 运行评估

### 基本用法
```bash
# 使用环境变量中的 API 密钥
python evaluate_acecoder.py --use-real-llm

# 指定 API 密钥
python evaluate_acecoder.py --use-real-llm --api-key "your-api-key-here"

# 使用不同的模型
python evaluate_acecoder.py --use-real-llm --model-name "gpt-4"

# 限制评估样本数量（节省 API 调用）
python evaluate_acecoder.py --use-real-llm --max-samples 5
```

### 完整示例
```bash
# 使用 GPT-4 评估 5 个样本
python evaluate_acecoder.py \
  --use-real-llm \
  --api-key "your-api-key-here" \
  --model-name "gpt-4" \
  --max-samples 5
```

## 3. 支持的模型

- `gpt-3.5-turbo` (默认)
- `gpt-4`
- `gpt-4-turbo`
- 其他 OpenAI 兼容的模型

## 4. 成本估算

### GPT-3.5-turbo
- 输入: ~$0.0015 per 1K tokens
- 输出: ~$0.002 per 1K tokens
- 10个样本约需 $0.05-0.10

### GPT-4
- 输入: ~$0.03 per 1K tokens  
- 输出: ~$0.06 per 1K tokens
- 10个样本约需 $1.00-2.00

## 5. 故障排除

### API 密钥错误
```
Error calling real LLM: 401 Client Error: Unauthorized
```
**解决方案**: 检查 API 密钥是否正确设置

### 网络错误
```
Error calling real LLM: Connection timeout
```
**解决方案**: 检查网络连接，或使用代理

### 回退机制
如果 LLM API 调用失败，系统会自动回退到基于规则的生成器。

## 6. 代码修改位置

主要修改在 `improved_generator.py` 中：

```python
class ImprovedCodeGenerator:
    def __init__(self, use_real_llm: bool = False, api_key: Optional[str] = None, 
                 model_name: str = "gpt-3.5-turbo", api_base: Optional[str] = None):
        # 初始化配置
        
    def call_real_llm(self, prompt: str) -> str:
        # 调用真实 LLM API
        
    def generate(self, prompt: str) -> str:
        # 根据配置选择使用真实 LLM 还是规则生成器
```

## 7. 自定义 API 端点

如果你使用其他兼容 OpenAI API 的服务：

```python
generator = ImprovedCodeGenerator(
    use_real_llm=True,
    api_key="your-api-key",
    model_name="your-model-name",
    api_base="https://your-api-endpoint.com/v1"
)
```

## 8. 性能对比

### 规则生成器
- ✅ 快速（毫秒级）
- ✅ 免费
- ✅ 可重现
- ❌ 质量有限

### 真实 LLM
- ✅ 高质量代码
- ✅ 理解复杂需求
- ❌ 较慢（秒级）
- ❌ 需要 API 密钥
- ❌ 有成本

## 9. 建议

1. **开发阶段**: 使用规则生成器进行快速迭代
2. **最终评估**: 使用真实 LLM 获得准确结果
3. **成本控制**: 先用小样本测试，确认效果后再扩大
4. **备份方案**: 保留规则生成器作为回退选项 