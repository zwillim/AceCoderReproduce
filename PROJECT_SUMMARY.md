# AceCoder 项目总结

## 项目概述

本项目是基于论文"AceCoder: Utilizing Existing Code to Enhance Code Generation" (Li et al., 2024) 的完整实现。AceCoder是一种专门用于代码生成的有效提示技术，通过利用现有代码来增强大语言模型在编程任务上的性能。

## 项目结构

```
AceCoderReproduce/
├── acecoder.py              # 核心AceCoder实现
├── improved_generator.py    # 改进的代码生成器
├── evaluate_acecoder.py     # AceCoder评估脚本
├── demo_acecoder.py         # 综合演示脚本
├── performance_analysis.py  # 性能分析脚本
├── paper_code_demo.py       # 论文代码对应关系演示
├── evaluate_multi.py        # 多数据集评估脚本
├── requirements.txt         # 项目依赖
├── README.md               # 项目说明
├── PROJECT_SUMMARY.md      # 项目总结（本文件）
├── PAPER_CODE_MAPPING.md   # 论文代码映射
├── performance_results.json # 性能结果
├── test_file.txt           # 测试文件
├── BMPP/                   # MBPP数据集目录
│   ├── mbpp.jsonl         # 主数据集文件
│   ├── sanitized-mbpp.json # 清理后的数据集
│   └── README.md          # 数据集信息
└── mbxp/                   # 多语言代码生成数据集
    ├── mbjp_release_v1.2.jsonl
    ├── mbjsp_release_v1.2.jsonl
    └── ... (其他语言数据集)
```

## 核心组件

### 1. 示例检索 (Example Retrieval)
- **BM25Retriever**: 内部实现的BM25检索算法
- **LuceneRetriever**: 基于Pyserini的Lucene检索引擎
- 从训练语料库中检索top-k个最相关的示例

### 2. 示例选择 (Example Selection)
- **ExampleSelector**: 使用n-gram重叠分析的冗余过滤
- 基于ROUGE-n评分的多样性选择
- 使用衰减因子减少冗余

### 3. 引导代码生成 (Guided Code Generation)
- **TestCaseAnalyzer**: 提取测试用例作为中间预备内容
- 遵循 `<requirement, preliminary, code>` 三元组结构
- 鼓励LLM在生成代码前理解需求

### 4. 提示构建 (Prompt Construction)
- 构建结构化的提示，包含三元组示例
- 特殊标签: `[requirement]`, `[test case]`, `[source code]`
- 以新需求和空的测试用例槽位结束，引导生成

## 主要功能

### 基础使用
```python
from acecoder import AceCoder

# 初始化AceCoder
acecoder = AceCoder('BMPP/mbpp.jsonl')

# 使用AceCoder提示生成代码
query = "编写一个函数来查找列表中的最大值"
prompt = acecoder.construct_prompt(query, k=3)

# 与您喜欢的LLM一起使用
# response = your_llm.generate(prompt)
```

### 运行演示
```bash
python3 demo_acecoder.py
```

### 运行评估
```bash
python3 evaluate_acecoder.py
```

### 多数据集评估
```bash
python3 evaluate_multi.py -n 50
```

## 技术特点

### Lucene检索
- 通过Pyserini使用Lucene引擎
- 使用Lucene默认参数的BM25评分
- 自动为训练语料库构建索引
- 默认检索top-20个相似程序
- 回退选项：如果Lucene不可用，使用内部BM25实现

### 示例选择算法
- 从需求中提取4-gram
- 计算ROUGE-n重叠评分
- 使用衰减因子λ = 0.5减少冗余
- 选择k=3个多样化示例

### 代码执行测试
- 安全的代码执行环境
- 支持测试用例验证
- 语法和功能正确性检查

## 数据集

### MBPP (Mostly Basic Python Problems)
- 主要训练数据集
- 包含975个Python编程问题
- 每个问题包含需求描述、解决方案代码和测试用例

### MBXP (Multi-language Code Generation)
- 多语言代码生成数据集
- 支持Java、JavaScript、PHP、C#、C++、Go、Kotlin、Rust、Scala、Swift等语言
- 用于跨语言代码生成评估

## 性能表现

根据论文结果，AceCoder相比基线方法在多个数据集上都有显著提升：
- MBPP: 提升约15-20%
- MBJP: 提升约10-15%
- MBJSP: 提升约12-18%

## 依赖关系

### 必需依赖
- **pyserini>=0.20.0**: Lucene检索引擎的Python接口（可选）

### 标准库模块（无需安装）
- json, re, math, typing, collections, heapq
- os, shutil, tempfile, pathlib
- argparse, random, traceback, ast, compile, exec

### 可选依赖
- numpy>=1.21.0: 数值计算
- scikit-learn>=1.0.0: 机器学习工具
- pytest>=6.0.0: 测试框架
- black>=21.0.0: 代码格式化
- flake8>=3.8.0: 代码检查

## 安装和使用

1. 克隆项目
```bash
git clone <repository-url>
cd AceCoderReproduce
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行演示
```bash
python3 demo_acecoder.py
```

4. 运行评估
```bash
python3 evaluate_acecoder.py
```

## 论文对应关系

项目实现与原始论文高度一致：
- 使用Lucene进行示例检索
- 实现BM25评分算法
- 使用n-gram重叠分析进行示例选择
- 采用测试用例作为中间预备内容
- 构建三元组结构化提示

## 扩展性

项目具有良好的扩展性：
- 支持多种编程语言
- 可插拔的检索器实现
- 模块化的组件设计
- 易于集成到现有LLM系统

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议。请确保：
- 代码符合项目风格
- 添加适当的测试
- 更新相关文档
- 遵循Python编码规范