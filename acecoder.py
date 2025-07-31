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

import json
import re
import math
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict
import heapq


class BM25Retriever:
    """BM25-based retrieval system for finding similar programs"""
    
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
        self.corpus = corpus
        self.doc_len = [len(doc.split()) for doc in corpus]
        self.avgdl = sum(self.doc_len) / len(self.doc_len)
        
        # Calculate document frequencies
        df = defaultdict(int)
        for doc in corpus:
            words = set(doc.split())
            for word in words:
                df[word] += 1
        
        # Calculate IDF
        for word, freq in df.items():
            self.idf[word] = math.log((len(corpus) - freq + 0.5) / (freq + 0.5))
    
    def get_scores(self, query: str) -> List[float]:
        """Get BM25 scores for query against all documents"""
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
        scores = self.get_scores(query)
        top_indices = heapq.nlargest(top_k, range(len(scores)), key=lambda i: scores[i])
        return top_indices


class LuceneRetriever:
    """Lucene-based retriever implemented via Pyserini.

    This class requires the `pyserini` package (https://github.com/castorini/pyserini).
    It will automatically build a temporary Lucene index for the provided corpus and
    perform BM25 retrieval using Lucene's default scorer.
    """

    def __init__(self, index_dir: str = "lucene_index"):
        self.index_dir = index_dir
        # The Pyserini imports are deferred so that the package is only required
        # when this retriever is actually used.
        try:
            from pyserini.search import SimpleSearcher  # noqa: F401
            from pyserini.index import SimpleIndexer  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "LuceneRetriever requires the `pyserini` package. Install it via\n"
                "  pip install pyserini\n"
                "More info: https://github.com/castorini/pyserini"
            ) from exc

        self._searcher = None  # Will be initialised after `fit`.

    # ------------------------------------------------------------------
    # Public interface expected by AceCoder (mirrors BM25Retriever)
    # ------------------------------------------------------------------
    def fit(self, corpus: List[str]):
        """Build a Lucene index for the given corpus.

        The corpus is converted to the JSONL format required by Pyserini's
        SimpleIndexer. All files are written under `<index_dir>_docs/`. If an
        index already exists, it will be reused to speed up subsequent runs.
        """
        import os
        import json
        import shutil
        import tempfile
        from pathlib import Path
        from pyserini.index import SimpleIndexer
        from pyserini.search import SimpleSearcher

        docs_dir = f"{self.index_dir}_docs"

        # Re-index only if necessary (i.e., docs directory does not exist).
        if not os.path.isdir(self.index_dir):
            # (Re)create docs directory.
            if os.path.exists(docs_dir):
                shutil.rmtree(docs_dir)
            os.makedirs(docs_dir, exist_ok=True)

            # Write JSONL documents (one file per doc so we can parallelise later).
            for i, doc in enumerate(corpus):
                json_path = os.path.join(docs_dir, f"doc_{i}.json")
                with open(json_path, "w", encoding="utf-8") as fp:
                    json.dump({"id": str(i), "contents": doc}, fp, ensure_ascii=False)

            # Build Lucene index.
            indexer = SimpleIndexer(docs_dir, self.index_dir)
            indexer.setStorePositions(False)
            indexer.setStoreDocvectors(False)
            indexer.setStoreRaw(False)
            indexer.build()

        # Create the searcher (BM25 by default).
        self._searcher = SimpleSearcher(self.index_dir)

    def retrieve(self, query: str, top_k: int = 20) -> List[int]:
        """Return indices of top-k most similar documents."""
        if self._searcher is None:
            raise RuntimeError("LuceneRetriever has not been fitted – call `fit()` first.")
        hits = self._searcher.search(query, k=top_k)
        return [int(hit.docid) for hit in hits]


class ExampleSelector:
    """Selector to filter out redundant programs and select informative examples"""
    
    def __init__(self, decay_factor: float = 0.5, n: int = 4):
        self.decay_factor = decay_factor
        self.n = n  # n-gram size
    
    def extract_ngrams(self, text: str) -> Dict[str, int]:
        """Extract n-grams with counts"""
        words = text.split()
        ngrams = defaultdict(int)
        
        for i in range(len(words) - self.n + 1):
            ngram = ' '.join(words[i:i + self.n])
            ngrams[ngram] += 1
            
        return ngrams
    
    def ngram_overlap_score(self, query_ngrams: Dict[str, int], doc_ngrams: Dict[str, int]) -> float:
        """Calculate recall-based ROUGE-n score"""
        if not query_ngrams:
            return 0.0
            
        overlap = 0
        total = 0
        
        for ngram, count in query_ngrams.items():
            overlap += min(count, doc_ngrams.get(ngram, 0))
            total += count
            
        return overlap / total if total > 0 else 0.0
    
    def select_examples(self, query: str, similar_examples: List[Tuple[str, str]], k: int = 3) -> List[Tuple[str, str]]:
        """Select k examples from similar_examples, filtering out redundant ones"""
        if len(similar_examples) <= k:
            return similar_examples
            
        selected = []
        query_ngrams = self.extract_ngrams(query)
        
        # Make a copy to avoid modifying original list
        remaining_examples = similar_examples.copy()
        
        # Extract n-grams for all examples
        example_ngrams = []
        for req, code in remaining_examples:
            example_ngrams.append(self.extract_ngrams(req))
        
        while len(selected) < k and len(remaining_examples) > 0:
            # Calculate scores for remaining examples
            scores = []
            for i, (req, code) in enumerate(remaining_examples):
                if i < len(example_ngrams):
                    score = self.ngram_overlap_score(query_ngrams, example_ngrams[i])
                    scores.append((score, i))
            
            if not scores:
                break
                
            # Select example with highest score
            best_score, best_idx = max(scores)
            selected.append(remaining_examples[best_idx])
            
            # Decay matched n-grams
            matched_ngrams = set(query_ngrams.keys()) & set(example_ngrams[best_idx].keys())
            for ngram in matched_ngrams:
                query_ngrams[ngram] *= self.decay_factor
            
            # Remove selected example
            remaining_examples.pop(best_idx)
            example_ngrams.pop(best_idx)
        
        return selected


class TestCaseAnalyzer:
    """Analyzer to extract test cases from code examples"""
    
    def extract_test_cases(self, test_list: List[str]) -> str:
        """Extract and format test cases as preliminary"""
        if not test_list:
            return ""
            
        test_cases = []
        for test in test_list[:3]:  # Use first 3 test cases
            # Clean up the test case
            test = test.strip()
            if test.startswith('assert '):
                # Extract the function call and expected result
                test = test[7:]  # Remove 'assert '
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
    
    def __init__(self, dataset_path: str, *, use_lucene: bool = True, lucene_index_dir: str = "lucene_index"):
        self.dataset_path = dataset_path

        # Choose retriever implementation.
        if use_lucene:
            try:
                self.retriever = LuceneRetriever(index_dir=lucene_index_dir)
                print("Using LuceneRetriever (Pyserini) for example retrieval")
            except ImportError as e:
                print(str(e))
                print("Falling back to internal BM25Retriever.\n")
                self.retriever = BM25Retriever()
        else:
            self.retriever = BM25Retriever()

        self.selector = ExampleSelector()
        self.analyzer = TestCaseAnalyzer()
        self.dataset: List[Dict[str, Any]] = []

        # Load dataset and build retrieval corpus.
        self.load_dataset()
        self.prepare_retrieval_corpus()
    
    def load_dataset(self):
        """Load MBPP dataset"""
        if self.dataset_path.endswith('.jsonl'):
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.dataset.append(json.loads(line))
        elif self.dataset_path.endswith('.json'):
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                self.dataset = json.load(f)
        
        print(f"Loaded {len(self.dataset)} examples from dataset")
    
    def prepare_retrieval_corpus(self):
        """Prepare corpus for retrieval"""
        corpus = []
        for item in self.dataset:
            # Use the prompt/text as the retrieval key
            text = item.get('text', item.get('prompt', ''))
            corpus.append(text)
        
        self.retriever.fit(corpus)
        print("Prepared retrieval corpus")
    
    def retrieve_examples(self, query: str, top_k: int = 20) -> List[Tuple[str, str, List[str]]]:
        """Retrieve similar examples for the given query"""
        # Get top-k similar indices
        similar_indices = self.retriever.retrieve(query, top_k)
        
        # Extract examples
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
        # Step 1: Retrieve similar examples
        similar_examples = self.retrieve_examples(query, top_k=20)
        
        # Step 2: Select k examples using selector
        example_pairs = [(text, code) for text, code, _ in similar_examples]
        selected_pairs = self.selector.select_examples(query, example_pairs, k)
        
        # Step 3: Add preliminaries (test cases) to selected examples
        prompt_parts = []
        
        for text, code in selected_pairs:
            # Find the original example to get test cases
            test_list = []
            for orig_text, orig_code, orig_tests in similar_examples:
                if orig_text == text and orig_code == code:
                    test_list = orig_tests
                    break
            
            # Extract test cases as preliminary
            preliminary = self.analyzer.extract_test_cases(test_list)
            
            # Construct triple
            triple = f"[requirement]\n{text}\n\n[test case]\n{preliminary}\n\n[source code]\n{code}"
            prompt_parts.append(triple)
        
        # Step 4: Add the new query
        prompt = '\n\n'.join(prompt_parts)
        prompt += f"\n\n[requirement]\n{query}\n\n[test case]\n"
        
        return prompt
    
    def generate_code(self, query: str, model_generate_func, k: int = 3) -> str:
        """Generate code using AceCoder prompting technique"""
        # Construct the AceCoder prompt
        prompt = self.construct_prompt(query, k)
        
        # Use the provided model to generate response
        response = model_generate_func(prompt)
        
        return response
    
    def evaluate_pass_at_k(self, test_queries: List[Dict], model_generate_func, k: int = 1) -> float:
        """Evaluate Pass@k metric"""
        passed = 0
        total = len(test_queries)
        
        for query_item in test_queries:
            query = query_item.get('text', query_item.get('prompt', ''))
            expected_code = query_item.get('code', '')
            test_list = query_item.get('test_list', [])
            
            # Generate code
            generated_response = self.generate_code(query, model_generate_func)
            
            # Extract code from response (assume it's after [source code])
            if '[source code]' in generated_response:
                generated_code = generated_response.split('[source code]')[-1].strip()
            else:
                generated_code = generated_response.strip()
            
            # Test the generated code
            if self.test_code(generated_code, test_list):
                passed += 1
        
        return passed / total if total > 0 else 0.0
    
    def test_code(self, code: str, test_list: List[str]) -> bool:
        """Test if the generated code passes all test cases"""
        try:
            # Create a safe execution environment
            exec_globals = {}
            exec(code, exec_globals)
            
            # Run all test cases
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
    # Initialize AceCoder with MBPP dataset
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    # Example query
    query = "Write a function to find the minimum cost path to reach (m, n) from (0, 0) for the given cost matrix."
    
    # Construct prompt
    prompt = acecoder.construct_prompt(query)
    print("Generated AceCoder Prompt:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)
    
    # Example of how to use with a language model
    def dummy_model_generate(prompt):
        """Dummy model function - replace with actual LLM"""
        return """# Test cases for minimum cost path
# min_cost([[1, 2, 3], [4, 8, 2], [1, 5, 3]], 2, 2) -> 8

def min_cost(cost, m, n):
    # Create a 2D DP table
    dp = [[0 for _ in range(n+1)] for _ in range(m+1)]
    
    # Initialize first cell
    dp[0][0] = cost[0][0]
    
    # Fill first row
    for j in range(1, n+1):
        dp[0][j] = dp[0][j-1] + cost[0][j]
    
    # Fill first column  
    for i in range(1, m+1):
        dp[i][0] = dp[i-1][0] + cost[i][0]
    
    # Fill the rest of the table
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