#!/usr/bin/env python3
"""
Evaluation script for AceCoder on MBPP dataset
"""

import json
import random
from typing import List, Dict
from acecoder import AceCoder
from improved_generator import ImprovedCodeGenerator


def load_test_data(file_path: str, max_samples: int = 50) -> List[Dict]:
    """Load test data from MBPP dataset"""
    data = []
    
    if file_path.endswith('.jsonl'):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    elif file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    # Use a subset for evaluation
    if len(data) > max_samples:
        data = random.sample(data, max_samples)
    
    return data


def evaluate_acecoder():
    """Evaluate AceCoder performance"""
    print("Initializing AceCoder...")
    
    # Initialize AceCoder with training data
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    # Load test data (using sanitized version for cleaner evaluation)
    print("Loading test data...")
    test_data = load_test_data('BMPP/sanitized-mbpp.json', max_samples=10)
    
    # Initialize improved code generator
    generator = ImprovedCodeGenerator()
    
    print(f"Evaluating on {len(test_data)} test samples...")
    
    # Evaluate with AceCoder prompting
    correct_acecoder = 0
    correct_baseline = 0
    
    for i, item in enumerate(test_data):
        query = item.get('prompt', item.get('text', ''))
        expected_code = item.get('code', '')
        test_list = item.get('test_list', [])
        
        print(f"\nTest {i+1}/{len(test_data)}: {query[:60]}...")
        
        # Test AceCoder prompting
        try:
            acecoder_prompt = acecoder.construct_prompt(query, k=3)
            acecoder_response = generator.generate(acecoder_prompt)
            
            # Extract code from response
            if '[source code]' in acecoder_response:
                acecoder_code = acecoder_response.split('[source code]')[-1].strip()
            else:
                # Remove test case comments
                lines = acecoder_response.split('\n')
                code_lines = []
                for line in lines:
                    if not line.strip().startswith('#'):
                        code_lines.append(line)
                acecoder_code = '\n'.join(code_lines).strip()
            
            if acecoder.test_code(acecoder_code, test_list):
                correct_acecoder += 1
                print("  ✓ AceCoder: PASS")
            else:
                print("  ✗ AceCoder: FAIL")
                print(f"    Generated: {acecoder_code[:100]}...")
                
        except Exception as e:
            print(f"  ✗ AceCoder: ERROR - {e}")
        
        # Test baseline (simple prompting)
        try:
            baseline_prompt = f"Write a Python function for: {query}"
            baseline_response = generator.generate(baseline_prompt)
            
            # Remove test case comments
            lines = baseline_response.split('\n')
            code_lines = []
            for line in lines:
                if not line.strip().startswith('#'):
                    code_lines.append(line)
            baseline_code = '\n'.join(code_lines).strip()
            
            if acecoder.test_code(baseline_code, test_list):
                correct_baseline += 1
                print("  ✓ Baseline: PASS")
            else:
                print("  ✗ Baseline: FAIL")
                print(f"    Generated: {baseline_code[:100]}...")
                
        except Exception as e:
            print(f"  ✗ Baseline: ERROR - {e}")
    
    # Calculate results
    acecoder_accuracy = correct_acecoder / len(test_data)
    baseline_accuracy = correct_baseline / len(test_data)
    
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"Total test samples: {len(test_data)}")
    print(f"AceCoder Pass@1: {correct_acecoder}/{len(test_data)} ({acecoder_accuracy:.2%})")
    print(f"Baseline Pass@1: {correct_baseline}/{len(test_data)} ({baseline_accuracy:.2%})")
    
    if acecoder_accuracy > baseline_accuracy:
        improvement = ((acecoder_accuracy - baseline_accuracy) / baseline_accuracy * 100) if baseline_accuracy > 0 else float('inf')
        print(f"AceCoder improvement: +{improvement:.1f}%")
    else:
        print("No improvement observed")
    
    return acecoder_accuracy, baseline_accuracy


def demo_acecoder():
    """Demonstrate AceCoder with a specific example"""
    print("=" * 60)
    print("ACECODER DEMONSTRATION")
    print("=" * 60)
    
    # Initialize AceCoder
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    # Example query
    query = "Write a function to find the shared elements from the given two lists."
    
    print(f"Query: {query}")
    print("\nConstructing AceCoder prompt...")
    
    # Construct prompt
    prompt = acecoder.construct_prompt(query, k=3)
    
    print("\nGenerated AceCoder Prompt:")
    print("-" * 40)
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    print("-" * 40)
    
    # Show how the prompt would be used
    generator = ImprovedCodeGenerator()
    response = generator.generate(prompt)
    
    print(f"\nGenerated Response:")
    print(response)
    
    # Test the generated code
    test_cases = [
        "assert set(shared_elements([1, 2, 3, 4], [3, 4, 5, 6])) == set([3, 4])",
        "assert set(shared_elements([1, 2], [3, 4])) == set([])"
    ]
    
    try:
        # Remove comments from response
        lines = response.split('\n')
        code_lines = []
        for line in lines:
            if not line.strip().startswith('#'):
                code_lines.append(line)
        code = '\n'.join(code_lines).strip()
        
        print(f"\nTesting generated code...")
        exec_globals = {}
        exec(code, exec_globals)
        
        all_passed = True
        for test in test_cases:
            try:
                exec(test, exec_globals)
                print(f"  ✓ {test}")
            except Exception as e:
                print(f"  ✗ {test} - {e}")
                all_passed = False
        
        if all_passed:
            print("All tests passed!")
        else:
            print("Some tests failed.")
            
    except Exception as e:
        print(f"Code execution failed: {e}")


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    print("AceCoder Evaluation Script")
    print("=" * 60)
    
    # Run demonstration
    demo_acecoder()
    
    print("\n" + "=" * 60)
    
    # Run evaluation
    try:
        evaluate_acecoder()
    except Exception as e:
        print(f"Evaluation failed: {e}")
        import traceback
        traceback.print_exc()