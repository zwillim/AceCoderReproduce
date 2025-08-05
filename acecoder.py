#!/usr/bin/env python3
"""
AceCoder: An Effective Prompting Technique Specialized for Code Generation

This implementation is based on the paper:
"AceCoder: Utilizing Existing Code to Enhance Code Generation" by Li et al. (2024)

Key components:
1. Example Retrieval: Retrieves similar programs as examples
2. Guided Code Generation: Generates intermediate preliminaries (e.g., test cases)
3. Prompt Construction: Constructs prompts with <requirement, preliminary, code> triples
"""

"""
AceCoder: 专门用于代码生成的有效提示技术

此实现基于论文：
Li等人(2024)的"AceCoder: 利用现有代码增强代码生成"

核心组件：
1. 示例检索：检索相似程序作为示例
2. 引导代码生成：生成中间预备内容（如测试用例）
3. 提示构建：构建包含<需求、预备内容、代码>三元组的提示
"""

import json
import re
import math
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict
import heapq


class BM25Retriever:
    """BM25-based retrieval system for finding similar programs"""
    """基于BM25的检索系统，用于查找相似程序"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.avgdl = 0
        
    def fit(self, corpus: List[str]):
        """Fit the BM25 model on the corpus"""
        """在语料库上拟合BM25模型"""
        self.corpus = corpus
        self.doc_len = [len(doc.split()) for doc in corpus]
        self.avgdl = sum(self.doc_len) / len(self.doc_len)
        
        # Calculate document frequencies
        # 计算文档频率
        df = defaultdict(int)
        for doc in corpus:
            words = set(doc.split())
            for word in words:
                df[word] += 1
        
        # Calculate IDF
        # 计算逆文档频率
        for word, freq in df.items():
            self.idf[word] = math.log((len(corpus) - freq + 0.5) / (freq + 0.5))
    
    def get_scores(self, query: str) -> List[float]:
        """Get BM25 scores for query against all documents"""
        """获取查询对所有文档的BM25分数"""
        query_words = query.split()
        scores = []
        
        for i, doc in enumerate(self.corpus):
            doc_words = doc.split()
            score = 0
            
            for word in query_words:
                if word in self.idf:
                    tf = doc_words.count(word)
                    idf = self.idf[word]
                    score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * self.doc_len[i] / self.avgdl))
            
            scores.append(score)
        
        return scores
    
    def retrieve(self, query: str, top_k: int = 20) -> List[int]:
        """Retrieve top-k most similar document indices"""
        """检索top-k最相似文档的索引"""
        scores = self.get_scores(query)
        top_indices = heapq.nlargest(top_k, range(len(scores)), key=lambda i: scores[i])
        return top_indices


class LuceneRetriever:
    """Lucene-based retriever implemented via Pyserini.

    This class requires the `pyserini` package (https://github.com/castorini/pyserini).
    It will automatically build a temporary Lucene index for the provided corpus and
    perform BM25 retrieval using Lucene's default scorer.
    """

    """基于Lucene的检索器，通过Pyserini实现。

    此类需要`pyserini`包(https://github.com/castorini/pyserini)。
    它将为提供的语料库自动构建临时Lucene索引，
    并使用Lucene的默认评分器执行BM25检索。
    """

    def __init__(self, index_dir: str = "lucene_index"):
        self.index_dir = index_dir
        # The Pyserini imports are deferred so that the package is only required
        # when this retriever is actually used.
        # Pyserini导入被延迟，因此只有在实际使用此检索器时才需要该包
        try:
            from pyserini.search.lucene import LuceneSearcher  # noqa: F401
            from pyserini.index.lucene import LuceneIndexer  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "LuceneRetriever requires the `pyserini` package. Install it via\n"
                "  pip install pyserini\n"
                "More info: https://github.com/castorini/pyserini"
            ) from exc

        self._searcher = None  # Will be initialised after `fit`.
        # 将在`fit`后初始化

    # ------------------------------------------------------------------
    # Public interface expected by AceCoder (mirrors BM25Retriever)
    # ------------------------------------------------------------------
    # AceCoder期望的公共接口（镜像BM25Retriever）
    def fit(self, corpus: List[str]):
        """Build a Lucene index for the given corpus.

        The corpus is converted to the JSONL format required by Pyserini's
        SimpleIndexer. All files are written under `<index_dir>_docs/`. If an
        index already exists, it will be reused to speed up subsequent runs.
        """
        """为给定语料库构建Lucene索引。

        语料库被转换为Pyserini的SimpleIndexer所需的JSONL格式。
        所有文件都写入`<index_dir>_docs/`下。如果索引已存在，
        将被重用以加速后续运行。
        """
        import os
        import json
        import shutil
        import tempfile
        from pathlib import Path
        from pyserini.index.lucene import LuceneIndexer
        from pyserini.search.lucene import LuceneSearcher

        docs_dir = f"{self.index_dir}_docs"

        # Always rebuild index for consistency
        # 始终重建索引以确保一致性
        if os.path.exists(docs_dir):
            shutil.rmtree(docs_dir)
        if os.path.exists(self.index_dir):
            shutil.rmtree(self.index_dir)
        
        os.makedirs(docs_dir, exist_ok=True)

        # Write JSONL documents
        # 写入JSONL文档
        for i, doc in enumerate(corpus):
            json_path = os.path.join(docs_dir, f"doc_{i}.json")
            with open(json_path, "w", encoding="utf-8") as fp:
                json.dump({"id": str(i), "contents": doc}, fp, ensure_ascii=False)

        # Build Lucene index using new API
        # 使用新API构建Lucene索引
        indexer = LuceneIndexer(self.index_dir)
        
        # Add documents to index
        # 将文档添加到索引
        for i, doc in enumerate(corpus):
            doc_dict = {"id": str(i), "contents": doc}
            indexer.add_doc_dict(doc_dict)
        
        indexer.close()

        # Create the searcher (BM25 by default).
        # 创建搜索器（默认使用BM25）
        self._searcher = LuceneSearcher(self.index_dir)

    def retrieve(self, query: str, top_k: int = 20) -> List[int]:
        """Return indices of top-k most similar documents."""
        """返回top-k最相似文档的索引"""
        if self._searcher is None:
            raise RuntimeError("LuceneRetriever has not been fitted – call `fit()` first.")
        hits = self._searcher.search(query, k=top_k)
        return [int(hit.docid) for hit in hits]


class ExampleSelector:
    """Selector to filter out redundant programs and select informative examples"""
    """选择器，用于过滤冗余程序并选择信息丰富的示例"""
    
    def __init__(self, decay_factor: float = 0.5, n: int = 4):
        self.decay_factor = decay_factor
        self.n = n  # n-gram size
        # n-gram大小
    
    def extract_ngrams(self, text: str) -> Dict[str, int]:
        """Extract n-grams with counts (legacy method, kept for compatibility)"""
        """提取n-gram及其计数（遗留方法，为兼容性保留）"""
        words = text.split()
        ngrams = defaultdict(int)
        
        for i in range(len(words) - self.n + 1):
            ngram = ' '.join(words[i:i + self.n])
            ngrams[ngram] += 1
            
        return ngrams
    
    def extract_all_ngrams(self, text: str) -> Dict[int, Dict[str, int]]:
        """Extract all n-grams from 1-gram to n-gram according to paper formula"""
        """根据论文公式提取从1-gram到n-gram的所有n-gram"""
        words = text.split()
        all_ngrams = {}
        
        for n in range(1, self.n + 1):
            ngrams = defaultdict(int)
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i + n])
                ngrams[ngram] += 1
            all_ngrams[n] = dict(ngrams)  # Convert defaultdict to dict
            # 将defaultdict转换为dict
        
        return all_ngrams
    
    def ngram_overlap_score(self, query_ngrams: Dict[str, int], doc_ngrams: Dict[str, int]) -> float:
        """Calculate recall-based ROUGE-n score (legacy method, kept for compatibility)"""
        """计算基于召回的ROUGE-n分数（遗留方法，为兼容性保留）"""
        if not query_ngrams:
            return 0.0
            
        overlap = 0
        total = 0
        
        for ngram, count in query_ngrams.items():
            overlap += min(count, doc_ngrams.get(ngram, 0))
            total += count
            
        return overlap / total if total > 0 else 0.0
    
    def ngram_overlap_score_geometric(self, query_ngrams_all: Dict[int, Dict[str, int]], 
                                     doc_ngrams_all: Dict[int, Dict[str, int]]) -> float:
        """Calculate BLEU-style geometric mean score according to paper formula:
        
        Score = exp(1/n * sum(log(R_i))) 
        where R_i = sum(S(ngram) for ngram in S∩Q) / sum(S(ngram) for ngram in S)
        
        S: example (doc), Q: query, S∩Q: intersection of example and query n-grams
        R_i measures how much of the example content is relevant to the query"""
        """根据论文公式计算BLEU风格的几何平均分数：
        
        Score = exp(1/n * sum(log(R_i))) 
        其中 R_i = sum(S(ngram) for ngram in S∩Q) / sum(S(ngram) for ngram in S)
        
        S: 示例(文档), Q: 查询, S∩Q: 示例和查询n-gram的交集
        R_i 衡量示例内容与查询的相关程度"""
        log_scores = []
        
        for i in range(1, self.n + 1):  # 1-gram 到 n-gram
            query_ngrams = query_ngrams_all.get(i, {})
            doc_ngrams = doc_ngrams_all.get(i, {})
            
            # 如果查询或示例中没有该层级的 n-gram，跳过
            if not query_ngrams or not doc_ngrams:
                continue
                
            # 计算 i-gram 召回率 R_i (论文公式: sum(S(ngram) for ngram in S∩Q) / sum(S(ngram) for ngram in S))
            overlap = 0
            total = 0
            
            # 遍历示例中的所有 n-gram (S)
            for ngram, count in doc_ngrams.items():
                total += count  # 分母：示例中所有 n-gram 的计数
                # 如果该 n-gram 也在查询中存在 (S ∩ Q)
                if ngram in query_ngrams:
                    overlap += count  # 分子：交集中 n-gram 在示例中的计数
                
            r_i = overlap / total if total > 0 else 1e-10  # 避免 log(0)
            # 只有当 r_i > 0 时才计算 log，避免 log(0) 错误
            if r_i > 1e-10:
                log_scores.append(math.log(r_i))
            else:
                log_scores.append(math.log(1e-10))  # 使用很小的值避免 log(0)
        
        # 应用论文公式：exp(1/n * sum(log(R_i)))
        if not log_scores:
            return 0.0
            
        geometric_mean = math.exp(sum(log_scores) / len(log_scores))
        return geometric_mean
    
    def select_examples(self, query: str, similar_examples: List[Tuple[str, str]], k: int = 3) -> List[Tuple[str, str]]:
        """Select k examples from similar_examples, filtering out redundant ones using geometric mean scoring"""
        """从similar_examples中选择k个示例，使用几何平均分数过滤冗余示例"""
        if len(similar_examples) <= k:
            return similar_examples
            
        selected = []
        query_ngrams_all = self.extract_all_ngrams(query)
        
        # Make a copy to avoid modifying original list
        # 制作副本以避免修改原始列表
        remaining_examples = similar_examples.copy()
        
        # Extract all n-grams for all examples
        # 为所有示例提取所有n-gram
        example_ngrams_all = []
        for req, code in remaining_examples:
            example_ngrams_all.append(self.extract_all_ngrams(req))
        
        while len(selected) < k and len(remaining_examples) > 0:
            # Calculate geometric mean scores for remaining examples
            # 计算剩余示例的几何平均分数
            scores = []
            for i, (req, code) in enumerate(remaining_examples):
                score = self.ngram_overlap_score_geometric(query_ngrams_all, example_ngrams_all[i])
                scores.append((score, i))
            
            if not scores:
                break
                
            # Select example with highest score
            # 选择分数最高的示例
            best_score, best_idx = max(scores)
            selected.append(remaining_examples[best_idx])
            
            # Decay matched n-grams for all n-gram levels
            # 对所有n-gram级别衰减匹配的n-gram
            for n in range(1, self.n + 1):
                if n in query_ngrams_all and n in example_ngrams_all[best_idx]:
                    matched_ngrams = set(query_ngrams_all[n].keys()) & set(example_ngrams_all[best_idx][n].keys())
                    for ngram in matched_ngrams:
                        query_ngrams_all[n][ngram] = query_ngrams_all[n][ngram] * self.decay_factor
            
            # Remove selected example
            # 移除已选择的示例
            remaining_examples.pop(best_idx)
            example_ngrams_all.pop(best_idx)
        
        return selected


class TestCaseAnalyzer:
    """Analyzer to extract test cases from code examples"""
    """从代码示例中提取测试用例的分析器"""
    
    def extract_test_cases(self, test_list: List[str]) -> str:
        """Extract and format test cases as preliminary"""
        """提取并格式化测试用例作为预备内容"""
        if not test_list:
            return ""
            
        test_cases = []
        for test in test_list[:3]:  # Use first 3 test cases
            # 使用前3个测试用例
            # Clean up the test case
            # 清理测试用例
            test = test.strip()
            if test.startswith('assert '):
                # Extract the function call and expected result
                # 提取函数调用和期望结果
                test = test[7:]  # Remove 'assert '
                # 移除 'assert '
                if ' == ' in test:
                    call, expected = test.split(' == ', 1)
                    test_cases.append(f"# {call.strip()} -> {expected.strip()}")
                else:
                    test_cases.append(f"# {test}")
            else:
                test_cases.append(f"# {test}")
        
        return '\n'.join(test_cases)


class AceCoder:
    """Main AceCoder implementation"""
    """主要的AceCoder实现"""
    
    def __init__(self, dataset_path: str, *, use_lucene: bool = False, lucene_index_dir: str = "lucene_index"):
        self.dataset_path = dataset_path

        # Choose retriever implementation.
        # 选择检索器实现
        if use_lucene:
            try:
                self.retriever = LuceneRetriever(index_dir=lucene_index_dir)
                print("Using LuceneRetriever (Pyserini) for example retrieval")
                print("使用LuceneRetriever (Pyserini)进行示例检索")
            except ImportError as e:
                print(str(e))
                print("Falling back to internal BM25Retriever.\n")
                print("回退到内部BM25Retriever。\n")
                self.retriever = BM25Retriever()
        else:
            self.retriever = BM25Retriever()

        self.selector = ExampleSelector()
        self.analyzer = TestCaseAnalyzer()
        self.dataset: List[Dict[str, Any]] = []

        # Load dataset and build retrieval corpus.
        # 加载数据集并构建检索语料库
        self.load_dataset()
        self.prepare_retrieval_corpus()
    
    def load_dataset(self):
        """Load MBPP dataset"""
        """加载MBPP数据集"""
        if self.dataset_path.endswith('.jsonl'):
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.dataset.append(json.loads(line))
        elif self.dataset_path.endswith('.json'):
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                self.dataset = json.load(f)
        
        print(f"Loaded {len(self.dataset)} examples from dataset")
        print(f"从数据集加载了 {len(self.dataset)} 个示例")
    
    def prepare_retrieval_corpus(self):
        """Prepare corpus for retrieval"""
        """准备检索语料库"""
        corpus = []
        for item in self.dataset:
            # Use the prompt/text as the retrieval key
            # 使用提示/文本作为检索键
            text = item.get('text', item.get('prompt', ''))
            corpus.append(text)
        
        self.retriever.fit(corpus)
        print("Prepared retrieval corpus")
        print("已准备检索语料库")
    
    def retrieve_examples(self, query: str, top_k: int = 20) -> List[Tuple[str, str, List[str]]]:
        """Retrieve similar examples for the given query"""
        """为给定查询检索相似示例"""
        # Get top-k similar indices
        # 获取top-k相似索引
        similar_indices = self.retriever.retrieve(query, top_k)
        
        # Extract examples
        # 提取示例
        examples = []
        for idx in similar_indices:
            item = self.dataset[idx]
            text = item.get('text', item.get('prompt', ''))
            code = item.get('code', '')
            test_list = item.get('test_list', [])
            
            examples.append((text, code, test_list))
        
        return examples
    
    def construct_prompt(self, query: str, k: int = 3) -> str:
        """Construct AceCoder prompt with <requirement, preliminary, code> triples"""
        """构建包含<需求、预备内容、代码>三元组的AceCoder提示"""
        # Step 1: Retrieve similar examples
        # 步骤1：检索相似示例
        similar_examples = self.retrieve_examples(query, top_k=20)
        
        # Step 2: Select k examples using selector
        # 步骤2：使用选择器选择k个示例
        example_pairs = [(text, code) for text, code, _ in similar_examples]
        selected_pairs = self.selector.select_examples(query, example_pairs, k)
        
        # Step 3: Add preliminaries (test cases) to selected examples
        # 步骤3：为选定的示例添加预备内容（测试用例）
        prompt_parts = []
        
        for text, code in selected_pairs:
            # Find the original example to get test cases
            # 查找原始示例以获取测试用例
            test_list = []
            for orig_text, orig_code, orig_tests in similar_examples:
                if orig_text == text and orig_code == code:
                    test_list = orig_tests
                    break
            
            # Extract test cases as preliminary
            # 提取测试用例作为预备内容
            preliminary = self.analyzer.extract_test_cases(test_list)
            
            # Construct triple
            # 构建三元组
            triple = f"[requirement]\n{text}\n\n[test case]\n{preliminary}\n\n[source code]\n{code}"
            prompt_parts.append(triple)
        
        # Step 4: Add the new query
        # 步骤4：添加新查询
        prompt = '\n\n'.join(prompt_parts)
        prompt += f"\n\n[requirement]\n{query}\n\n[test case]\n"
        
        return prompt
    
    def generate_code(self, query: str, model_generate_func, k: int = 3) -> str:
        """Generate code using AceCoder prompting technique"""
        """使用AceCoder提示技术生成代码"""
        # Construct the AceCoder prompt
        # 构建AceCoder提示
        prompt = self.construct_prompt(query, k)
        
        # Use the provided model to generate response
        # 使用提供的模型生成响应
        response = model_generate_func(prompt)
        
        return response
    
    def evaluate_pass_at_k(self, test_queries: List[Dict], model_generate_func, k: int = 1) -> float:
        """Evaluate Pass@k metric"""
        """评估Pass@k指标"""
        passed = 0
        total = len(test_queries)
        
        for query_item in test_queries:
            query = query_item.get('text', query_item.get('prompt', ''))
            expected_code = query_item.get('code', '')
            test_list = query_item.get('test_list', [])
            
            # Generate code
            # 生成代码
            generated_response = self.generate_code(query, model_generate_func)
            
            # Extract code from response (assume it's after [source code])
            # 从响应中提取代码（假设在[source code]之后）
            if '[source code]' in generated_response:
                generated_code = generated_response.split('[source code]')[-1].strip()
            else:
                generated_code = generated_response.strip()
            
            # Test the generated code
            # 测试生成的代码
            if self.test_code(generated_code, test_list):
                passed += 1
        
        return passed / total if total > 0 else 0.0
    
    def test_code(self, code: str, test_list: List[str]) -> bool:
        """Test if the generated code passes all test cases"""
        """测试生成的代码是否通过所有测试用例"""
        try:
            # Create a safe execution environment
            # 创建安全的执行环境
            exec_globals = {}
            exec(code, exec_globals)
            
            # Run all test cases
            # 运行所有测试用例
            for test in test_list:
                try:
                    exec(test, exec_globals)
                except:
                    return False
            
            return True
        except:
            return False


def main():
    """Main function to demonstrate AceCoder usage"""
    """演示AceCoder使用的主要函数"""
    # Initialize AceCoder with MBPP dataset
    # 使用MBPP数据集初始化AceCoder
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    # Example query
    # 示例查询
    query = "Write a function to find the minimum cost path to reach (m, n) from (0, 0) for the given cost matrix."
    
    # Construct prompt
    # 构建提示
    prompt = acecoder.construct_prompt(query)
    print("Generated AceCoder Prompt:")
    print("生成的AceCoder提示:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)
    
    # Example of how to use with a language model
    # 如何与语言模型一起使用的示例
    def dummy_model_generate(prompt):
        """Dummy model function - replace with actual LLM"""
        """虚拟模型函数 - 替换为实际的LLM"""
        return """# Test cases for minimum cost path
# min_cost([[1, 2, 3], [4, 8, 2], [1, 5, 3]], 2, 2) -> 8

def min_cost(cost, m, n):
    # Create a 2D DP table
    # 创建2D动态规划表
    dp = [[0 for _ in range(n+1)] for _ in range(m+1)]
    
    # Initialize first cell
    # 初始化第一个单元格
    dp[0][0] = cost[0][0]
    
    # Fill first row
    # 填充第一行
    for j in range(1, n+1):
        dp[0][j] = dp[0][j-1] + cost[0][j]
    
    # Fill first column  
    # 填充第一列
    for i in range(1, m+1):
        dp[i][0] = dp[i-1][0] + cost[i][0]
    
    # Fill the rest of the table
    # 填充剩余的表格
    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + cost[i][j]
    
    return dp[m][n]"""
    
    # Generate code
    result = acecoder.generate_code(query, dummy_model_generate)
    print("\nGenerated Code:")
    print(result)


if __name__ == "__main__":
    main()