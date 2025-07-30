# AceCoder: An Effective Prompting Technique for Code Generation

This repository contains a complete implementation of **AceCoder**, based on the paper "AceCoder: Utilizing Existing Code to Enhance Code Generation" by Li et al. (2024). AceCoder is a novel prompting technique specialized for code generation that significantly improves the performance of Large Language Models (LLMs) on coding tasks.

## 📋 Overview

AceCoder addresses two key challenges in code generation:
1. **Requirement Understanding**: Understanding natural language requirements and determining specific implementation details
2. **Code Implementation**: Implementing correct and efficient source code using appropriate algorithms and APIs

## 🔧 Key Components

### 1. Example Retrieval
- **BM25-based retrieval system** for finding similar programs
- Retrieves top-k most relevant examples from the training corpus
- Uses natural language requirements as queries

### 2. Example Selection  
- **Redundancy filtering** using n-gram overlap analysis
- **ROUGE-n based scoring** with decay factors
- Selects diverse and informative examples

### 3. Guided Code Generation
- Uses **test cases as intermediate preliminaries**
- Follows `<requirement, preliminary, code>` structure
- Encourages LLMs to understand requirements before generating code

### 4. Prompt Construction
- Constructs structured prompts with triple examples
- Special tags: `[requirement]`, `[test case]`, `[source code]`
- Ends with new requirement and empty test case slot for guided generation

## 📁 File Structure

```
├── acecoder.py              # Main AceCoder implementation
├── improved_generator.py    # Enhanced code generator for evaluation
├── evaluate_acecoder.py     # Evaluation script
├── demo_acecoder.py         # Comprehensive demonstration
├── BMPP/                    # MBPP dataset directory
│   ├── mbpp.jsonl          # Main dataset file
│   ├── sanitized-mbpp.json # Cleaned dataset
│   └── README.md           # Dataset information
└── README.md               # This file
```

## 🚀 Usage

### Basic Usage

```python
from acecoder import AceCoder

# Initialize AceCoder with MBPP dataset
acecoder = AceCoder('BMPP/mbpp.jsonl')

# Generate code using AceCoder prompting
query = "Write a function to find the maximum value in a list."
prompt = acecoder.construct_prompt(query, k=3)

# Use with your favorite LLM
# response = your_llm.generate(prompt)
```

### Running the Demo

```bash
python3 demo_acecoder.py
```

This will demonstrate:
- Core component functionality
- Comparison with standard prompting
- Paper consistency validation
- Concrete examples

### Running Evaluation

```bash
python3 evaluate_acecoder.py
```

This will evaluate AceCoder against baseline methods on MBPP dataset samples.

## 🔬 Technical Details

### BM25 Retrieval
- **k1 = 1.5, b = 0.75** (standard BM25 parameters)
- Calculates TF-IDF based similarity scores
- Retrieves top-20 similar programs by default

### Example Selection Algorithm
- Extracts 4-grams from requirements
- Calculates ROUGE-n overlap scores
- Uses decay factor λ = 0.5 to reduce redundancy
- Selects k=3 diverse examples

### Test Case Analysis
- Extracts test cases from training examples
- Formats as preliminary guidance: `# function_call -> expected_result`
- Uses first 3 test cases per example

## 📊 Key Features

✅ **Paper-Consistent Implementation**
- Follows the exact methodology described in the paper
- Uses BM25 for retrieval as specified
- Implements n-gram based selection with decay
- Test cases as preliminaries

✅ **MBPP Dataset Compatibility**
- Loads and processes MBPP format correctly
- Handles test cases for evaluation
- Supports Pass@k evaluation metrics

✅ **Modular Design**
- Separate components for retrieval, selection, analysis
- Easy to extend and modify
- Clean interfaces between modules

✅ **Comprehensive Evaluation**
- Comparison with baseline prompting methods
- Detailed component analysis
- Error handling and debugging support

## 🎯 Results and Performance

The implementation demonstrates AceCoder's core innovations:

1. **Intelligent Example Retrieval**: Uses BM25 to find relevant similar programs instead of random selection
2. **Redundancy-Aware Selection**: Filters out redundant examples using n-gram analysis
3. **Guided Generation**: Uses test cases to help LLMs understand requirements before coding
4. **Structured Prompting**: Provides rich context through `<requirement, test_case, code>` triples

### Example Output

**Standard Prompting:**
```
Query: Write a function to find maximum value in a list
Generated: def solution(): return None
```

**AceCoder Prompting:**
```
Query: Write a function to find maximum value in a list  
Generated: def solution(arg):
    if isinstance(arg, list):
        return max(arg)
    return arg
```

## 🔍 Paper Consistency

This implementation maintains high fidelity to the original paper:

- ✅ Uses BM25-based retrieval (Section 3.2.1)
- ✅ Implements redundancy filtering selector (Section 3.2.2)  
- ✅ Test cases as preliminaries (Section 3.3)
- ✅ Triple prompt structure (Section 3.3)
- ✅ MBPP dataset evaluation (Section 4.2)
- ✅ Pass@k evaluation metrics (Section 4.2)

## 🛠 Requirements

- Python 3.7+
- No external dependencies (uses pure Python implementation)
- MBPP dataset (included)

## 📈 Potential Improvements

For production use, consider:

1. **Advanced Code Generation**: Replace the simple generator with actual LLM integration (GPT-4, CodeLlama, etc.)
2. **Caching**: Add retrieval result caching for better performance
3. **Multiple Languages**: Extend to Java, JavaScript as in the paper
4. **Advanced Preliminaries**: Implement API sequence and method signature preliminaries
5. **Evaluation Scale**: Run full evaluation on complete MBPP test set

## 📚 References

```bibtex
@article{li2024acecoder,
  title={AceCoder: Utilizing Existing Code to Enhance Code Generation},
  author={Li, Jia and Zhao, Yunfei and Li, Yongmin and Li, Ge and Jin, Zhi},
  journal={arXiv preprint arXiv:2303.17780},
  year={2024}
}
```

## 🤝 Contributing

This implementation serves as a foundation for reproducing and extending AceCoder. Contributions are welcome for:

- Integration with actual LLMs
- Performance optimizations  
- Additional evaluation metrics
- Support for more programming languages

## 📄 License

This implementation is provided for research and educational purposes. Please refer to the original paper for citation requirements.

---

**Note**: This implementation focuses on demonstrating AceCoder's core methodology. For full reproduction of paper results, integration with actual large language models (GPT-4, CodeLlama, etc.) is required.