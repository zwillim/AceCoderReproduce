# AceCoder 安装和使用指南

## 系统要求

- Python 3.7 或更高版本
- 至少 2GB 可用内存
- 至少 1GB 磁盘空间（用于数据集和索引）

## 快速安装

### 1. 克隆项目
```bash
git clone <repository-url>
cd AceCoderReproduce
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 验证安装
```bash
python3 -c "from acecoder import AceCoder; print('安装成功！')"
```

## 详细安装步骤

### 可选依赖安装

#### 1. 安装 Pyserini (推荐)
Pyserini 提供了更高效的 Lucene 检索引擎支持：

```bash
pip install pyserini>=0.20.0
```

**注意**: 如果安装 Pyserini 遇到问题，项目会自动回退到内部 BM25 实现。

#### 2. 安装开发工具 (可选)
```bash
pip install pytest black flake8
```

### 3. 验证数据集
确保数据集文件存在：
```bash
ls BMPP/mbpp.jsonl
ls mbxp/mbjp_release_v1.2.jsonl
```

## 使用方法

### 基础使用

#### 1. 运行演示
```bash
python3 demo_acecoder.py
```

这将展示：
- 核心组件功能
- 与标准提示方法的比较
- 论文一致性验证
- 具体示例

#### 2. 运行评估
```bash
python3 evaluate_acecoder.py
```

这将评估 AceCoder 在 MBPP 数据集上的性能。

#### 3. 多数据集评估
```bash
python3 evaluate_multi.py -n 50
```

这将评估多个数据集上的性能。

### 编程接口使用

#### 1. 基本用法
```python
from acecoder import AceCoder

# 初始化 AceCoder
acecoder = AceCoder('BMPP/mbpp.jsonl')

# 构建提示
query = "编写一个函数来查找列表中的最大值"
prompt = acecoder.construct_prompt(query, k=3)

# 使用您的 LLM 生成代码
# response = your_llm.generate(prompt)
```

#### 2. 自定义检索器
```python
from acecoder import AceCoder, BM25Retriever

# 使用内部 BM25 检索器
acecoder = AceCoder('BMPP/mbpp.jsonl', use_lucene=False)

# 或者使用 Lucene 检索器
acecoder = AceCoder('BMPP/mbpp.jsonl', use_lucene=True)
```

#### 3. 测试代码
```python
# 测试生成的代码
test_list = [
    "assert find_max([1, 2, 3]) == 3",
    "assert find_max([5, 2, 8, 1]) == 8"
]

code = "def find_max(lst): return max(lst)"
is_correct = acecoder.test_code(code, test_list)
print(f"代码正确性: {is_correct}")
```

## 故障排除

### 常见问题

#### 1. Pyserini 安装失败
**问题**: `pip install pyserini` 失败
**解决方案**: 
```bash
# 尝试使用 conda 安装
conda install -c conda-forge pyserini

# 或者跳过 Pyserini，使用内部 BM25
acecoder = AceCoder('BMPP/mbpp.jsonl', use_lucene=False)
```

#### 2. 内存不足
**问题**: 处理大数据集时内存不足
**解决方案**:
```python
# 减少检索的示例数量
prompt = acecoder.construct_prompt(query, k=1)

# 或者使用较小的数据集
acecoder = AceCoder('BMPP/sanitized-mbpp.json')
```

#### 3. 数据集文件不存在
**问题**: `FileNotFoundError: BMPP/mbpp.jsonl`
**解决方案**:
```bash
# 检查文件是否存在
ls -la BMPP/

# 如果文件不存在，可能需要下载数据集
# 或者使用其他可用的数据集文件
```

### 性能优化

#### 1. 启用 Lucene 检索
```python
# 使用更高效的 Lucene 检索
acecoder = AceCoder('BMPP/mbpp.jsonl', use_lucene=True)
```

#### 2. 调整检索参数
```python
# 减少检索数量以提高速度
prompt = acecoder.construct_prompt(query, k=2)

# 或者使用更少的示例
acecoder.selector = ExampleSelector(decay_factor=0.3, n=3)
```

#### 3. 缓存结果
```python
# 对于重复查询，可以缓存结果
import pickle

cache_file = 'acecoder_cache.pkl'
try:
    with open(cache_file, 'rb') as f:
        cache = pickle.load(f)
except FileNotFoundError:
    cache = {}

if query in cache:
    prompt = cache[query]
else:
    prompt = acecoder.construct_prompt(query)
    cache[query] = prompt
    
    with open(cache_file, 'wb') as f:
        pickle.dump(cache, f)
```

## 环境配置

### 虚拟环境 (推荐)
```bash
# 创建虚拟环境
python3 -m venv acecoder_env

# 激活虚拟环境
source acecoder_env/bin/activate  # Linux/Mac
# 或
acecoder_env\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### Conda 环境
```bash
# 创建 conda 环境
conda create -n acecoder python=3.9

# 激活环境
conda activate acecoder

# 安装依赖
pip install -r requirements.txt
```

## 测试

### 运行单元测试
```bash
python3 -m pytest tests/ -v
```

### 运行集成测试
```bash
python3 evaluate_acecoder.py
python3 evaluate_multi.py -n 10
```

## 更新

### 更新依赖
```bash
pip install --upgrade -r requirements.txt
```

### 更新项目
```bash
git pull origin main
pip install --upgrade -r requirements.txt
```

## 支持

如果遇到问题，请：

1. 检查系统要求是否满足
2. 查看故障排除部分
3. 查看项目文档
4. 提交 Issue 到项目仓库

## 许可证

本项目基于 MIT 许可证开源。详见 LICENSE 文件。 