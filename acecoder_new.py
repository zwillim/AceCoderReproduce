#!/usr/bin/env python3
"""
AceCoder New: An Effective Prompting Technique Specialized for Code Generation

This implementation allows direct initialization with training data instead of loading from files.
This implementation is based on the paper:
"AceCoder: Utilizing Existing Code to Enhance Code Generation" by Li et al. (2024)

Key components:
1. Example Retrieval: Retrieves similar programs as examples
2. Guided Code Generation: Generates intermediate preliminaries (e.g., test cases)
3. Prompt Construction: Constructs prompts with <requirement, preliminary, code> triples
"""

"""
AceCoder New: 专门用于代码生成的有效提示技术

此实现允许直接使用训练数据初始化，而不需要从文件加载。
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


class ExampleSelector:
    """Example selector that uses n-gram overlap to select diverse examples"""
    """使用n-gram重叠选择多样化示例的示例选择器"""
    
    def __init__(self, decay_factor: float = 0.5, n: int = 4):
        self.decay_factor = decay_factor
        self.n = n
    
    def extract_ngrams(self, text: str) -> Dict[str, int]:
        """Extract n-grams from text"""
        """从文本中提取n-gram"""
        words = text.split()
        ngrams = {}
        for i in range(len(words) - self.n + 1):
            ngram = ' '.join(words[i:i + self.n])
            ngrams[ngram] = ngrams.get(ngram, 0) + 1
        return ngrams
    
    def extract_all_ngrams(self, text: str) -> Dict[int, Dict[str, int]]:
        """Extract n-grams for n=1,2,3,4"""
        """提取n=1,2,3,4的n-gram"""
        ngrams_all = {}
        for n in range(1, self.n + 1):
            words = text.split()
            ngrams = {}
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i + n])
                ngrams[ngram] = ngrams.get(ngram, 0) + 1
            ngrams_all[n] = ngrams
        return ngrams_all
    
    def ngram_overlap_score(self, query_ngrams: Dict[str, int], doc_ngrams: Dict[str, int]) -> float:
        """Calculate n-gram overlap score between query and document"""
        """计算查询和文档之间的n-gram重叠分数"""
        if not query_ngrams or not doc_ngrams:
            return 0.0
        
        intersection = 0
        for ngram in query_ngrams:
            if ngram in doc_ngrams:
                intersection += min(query_ngrams[ngram], doc_ngrams[ngram])
        
        union = sum(query_ngrams.values()) + sum(doc_ngrams.values()) - intersection
        return intersection / union if union > 0 else 0.0
    
    def ngram_overlap_score_geometric(self, query_ngrams_all: Dict[int, Dict[str, int]], 
                                     doc_ngrams_all: Dict[int, Dict[str, int]]) -> float:
        """Calculate geometric mean of n-gram overlap scores"""
        """计算n-gram重叠分数的几何平均值"""
        scores = []
        for n in range(1, self.n + 1):
            if n in query_ngrams_all and n in doc_ngrams_all:
                score = self.ngram_overlap_score(query_ngrams_all[n], doc_ngrams_all[n])
                scores.append(score)
        
        if not scores:
            return 0.0
        
        # Geometric mean
        # 几何平均值
        product = 1.0
        for score in scores:
            product *= score
        
        return product ** (1.0 / len(scores))
    
    def select_examples(self, query: str, similar_examples: List[Tuple[str, str]], k: int = 3) -> List[Tuple[str, str]]:
        """Select diverse examples using n-gram overlap"""
        """使用n-gram重叠选择多样化示例"""
        if not similar_examples:
            return []
        
        # Extract n-grams for query
        # 为查询提取n-gram
        query_ngrams_all = self.extract_all_ngrams(query)
        
        # Calculate overlap scores for all examples
        # 计算所有示例的重叠分数
        example_scores = []
        for text, code in similar_examples:
            doc_ngrams_all = self.extract_all_ngrams(text)
            score = self.ngram_overlap_score_geometric(query_ngrams_all, doc_ngrams_all)
            example_scores.append((score, text, code))
        
        # Sort by score (descending)
        # 按分数排序（降序）
        example_scores.sort(key=lambda x: x[0], reverse=True)
        
        # Select top-k examples with diversity penalty
        # 选择top-k示例，应用多样性惩罚
        selected = []
        selected_ngrams = set()
        
        for score, text, code in example_scores:
            if len(selected) >= k:
                break
            
            # Calculate diversity penalty
            # 计算多样性惩罚
            text_ngrams_all = self.extract_all_ngrams(text)
            penalty = 1.0
            
            for n in range(1, self.n + 1):
                if n in text_ngrams_all:
                    for ngram in text_ngrams_all[n]:
                        if ngram in selected_ngrams:
                            penalty *= self.decay_factor
            
            # Apply penalty to score
            # 对分数应用惩罚
            adjusted_score = score * penalty
            
            # Add to selected if score is still high enough
            # 如果分数仍然足够高，则添加到选中列表
            if adjusted_score > 0.1:  # Threshold
                selected.append((text, code))
                
                # Update selected n-grams
                # 更新选中的n-gram
                for n in range(1, self.n + 1):
                    if n in text_ngrams_all:
                        for ngram in text_ngrams_all[n]:
                            selected_ngrams.add(ngram)
        
        return selected


class TestCaseAnalyzer:
    """Analyzer for extracting test cases from test lists"""
    """从测试列表中提取测试用例的分析器"""
    
    def extract_test_cases(self, test_list: List[str]) -> str:
        """Extract and format test cases"""
        """提取并格式化测试用例"""
        if not test_list:
            return "No test cases provided"
        
        formatted_tests = []
        for i, test in enumerate(test_list, 1):
            # Clean up the test case
            # 清理测试用例
            test = test.strip()
            if test.startswith('assert '):
                test = test[7:]  # Remove 'assert '
            
            formatted_tests.append(f"Test {i}: {test}")
        
        return '\n'.join(formatted_tests)


class AceCoderNew:
    """Main AceCoder implementation that accepts training data directly"""
    """直接接受训练数据的主要AceCoder实现"""
    
    def __init__(self, training_data: List[Dict[str, Any]], *, use_lucene: bool = False, lucene_index_dir: str = "lucene_index"):
        """
        Initialize AceCoder with training data directly
        
        Args:
            training_data: List of training examples, each containing:
                - 'prompt' or 'text': The query/prompt text
                - 'code': The corresponding code
                - 'test_list': List of test cases (optional)
            use_lucene: Whether to use Lucene retriever (requires pyserini)
            lucene_index_dir: Directory for Lucene index
        """
        """
        直接使用训练数据初始化AceCoder
        
        参数:
            training_data: 训练示例列表，每个包含：
                - 'prompt' 或 'text': 查询/提示文本
                - 'code': 相应的代码
                - 'test_list': 测试用例列表（可选）
            use_lucene: 是否使用Lucene检索器（需要pyserini）
            lucene_index_dir: Lucene索引目录
        """
        self.training_data = training_data

        # Choose retriever implementation.
        # 选择检索器实现
        if use_lucene:
            try:
                from acecoder import LuceneRetriever
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

        # Prepare retrieval corpus from training data
        # 从训练数据准备检索语料库
        self.prepare_retrieval_corpus()
    
    def prepare_retrieval_corpus(self):
        """Prepare corpus for retrieval from training data"""
        """从训练数据准备检索语料库"""
        corpus = []
        for item in self.training_data:
            # Use the prompt/text as the retrieval key
            # 使用提示/文本作为检索键
            text = item.get('text', item.get('prompt', ''))
            corpus.append(text)
        
        self.retriever.fit(corpus)
        print(f"Prepared retrieval corpus with {len(self.training_data)} examples")
        print(f"已准备包含 {len(self.training_data)} 个示例的检索语料库")
    
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
            item = self.training_data[idx]
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


def convert_split_sets_to_training_data(training_items: List[Dict]) -> List[Dict]:
    """
    Convert split_sets training items to AceCoder training data format
    
    Args:
        training_items: List of training items from split_sets
        
    Returns:
        List of training data in AceCoder format
    """
    """
    将split_sets训练项转换为AceCoder训练数据格式
    
    参数:
        training_items: 来自split_sets的训练项列表
        
    返回:
        AceCoder格式的训练数据列表
    """
    training_data = []
    
    for item in training_items:
        # Extract content description
        content = item['content']
        
        # Create a description from content fields
        description_parts = []
        if 'src' in content:
            for field_info in content['src']:
                if isinstance(field_info, str):
                    # Extract field name and description
                    if '/' in field_info:
                        field_name, description = field_info.split('/', 1)
                        description_parts.append(f"{field_name}: {description}")
                    else:
                        description_parts.append(field_info)
        
        description = "\n".join(description_parts)
        
        # Extract code
        code = item['code']
        
        # Create training data item
        training_item = {
            'prompt': description,
            'code': str(code),  # Convert to string for compatibility
            'test_list': []  # No test cases in split_sets data
        }
        
        training_data.append(training_item)
    
    return training_data


def main():
    """Demo of AceCoderNew usage"""
    """AceCoderNew使用演示"""
    
    # Example training data
    # 示例训练数据
    training_data = [
        {
            'prompt': 'Write a function to find the maximum element in a list',
            'code': 'def find_max(lst):\n    return max(lst)',
            'test_list': ['assert find_max([1, 2, 3]) == 3', 'assert find_max([-1, -2, -3]) == -1']
        },
        {
            'prompt': 'Write a function to calculate the sum of all elements in a list',
            'code': 'def sum_list(lst):\n    return sum(lst)',
            'test_list': ['assert sum_list([1, 2, 3]) == 6', 'assert sum_list([0, 0, 0]) == 0']
        }
    ]
    
    # Initialize AceCoderNew
    # 初始化AceCoderNew
    acecoder = AceCoderNew(training_data)
    
    # Example query
    # 示例查询
    query = "Write a function to find the minimum element in a list"
    
    print("Query:", query)
    print("查询:", query)
    
    # Construct prompt
    # 构建提示
    prompt = acecoder.construct_prompt(query, k=2)
    print("\nGenerated prompt:")
    print("\n生成的提示:")
    print(prompt)


if __name__ == "__main__":
    main() 