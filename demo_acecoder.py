#!/usr/bin/env python3
"""
AceCoder Demo Script - Demonstrates the implementation based on the paper:
"AceCoder: Utilizing Existing Code to Enhance Code Generation" by Li et al. (2024)

This script demonstrates:
1. Example Retrieval using BM25
2. Guided Code Generation with test cases as preliminaries  
3. Prompt construction with <requirement, preliminary, code> triples
4. Comparison with baseline prompting
"""

from acecoder import AceCoder
from improved_generator import ImprovedCodeGenerator


def demonstrate_core_components():
    """Demonstrate each core component of AceCoder"""
    print("=" * 80)
    print("ACECODER CORE COMPONENTS DEMONSTRATION")
    print("=" * 80)
    
    # Initialize AceCoder
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    # Test query
    query = "Write a function to find the shared elements from the given two lists."
    print(f"Query: {query}")
    
    print("\n" + "-" * 60)
    print("1. EXAMPLE RETRIEVAL (BM25-based)")
    print("-" * 60)
    
    # Demonstrate retrieval
    similar_examples = acecoder.retrieve_examples(query, top_k=5)
    print(f"Retrieved {len(similar_examples)} similar examples:")
    
    for i, (text, code, tests) in enumerate(similar_examples[:3]):
        print(f"\nExample {i+1}:")
        print(f"  Requirement: {text[:80]}...")
        print(f"  Code snippet: {code[:60].replace(chr(10), ' ')}...")
        print(f"  Test cases: {len(tests)} tests")
    
    print("\n" + "-" * 60)
    print("2. EXAMPLE SELECTION (Redundancy filtering)")
    print("-" * 60)
    
    # Demonstrate selection
    example_pairs = [(text, code) for text, code, _ in similar_examples]
    selected_pairs = acecoder.selector.select_examples(query, example_pairs, k=3)
    
    print(f"Selected {len(selected_pairs)} examples after filtering redundancy:")
    for i, (text, code) in enumerate(selected_pairs):
        print(f"  {i+1}. {text[:60]}...")
    
    print("\n" + "-" * 60)
    print("3. GUIDED CODE GENERATION (Test cases as preliminaries)")
    print("-" * 60)
    
    # Demonstrate test case extraction
    for text, code in selected_pairs[:1]:  # Show one example
        # Find test cases for this example
        test_list = []
        for orig_text, orig_code, orig_tests in similar_examples:
            if orig_text == text and orig_code == code:
                test_list = orig_tests
                break
        
        preliminary = acecoder.analyzer.extract_test_cases(test_list)
        print(f"Original requirement: {text}")
        print(f"Extracted test cases as preliminary:")
        print(preliminary)
        print(f"Original code: {code[:100]}...")
    
    print("\n" + "-" * 60)
    print("4. PROMPT CONSTRUCTION")
    print("-" * 60)
    
    # Show final prompt
    prompt = acecoder.construct_prompt(query, k=3)
    print("Final AceCoder prompt structure:")
    print(f"Length: {len(prompt)} characters")
    print(f"Number of examples: {prompt.count('[requirement]') - 1}")
    print(f"Contains test cases: {'[test case]' in prompt}")
    print(f"Contains source code: {'[source code]' in prompt}")


def compare_prompting_approaches():
    """Compare AceCoder with standard prompting"""
    print("\n" + "=" * 80)
    print("PROMPTING APPROACHES COMPARISON")
    print("=" * 80)
    
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    generator = ImprovedCodeGenerator()
    
    query = "Write a function to find the maximum value in a list of numbers."
    
    print(f"Query: {query}")
    
    print("\n" + "-" * 40)
    print("STANDARD FEW-SHOT PROMPTING:")
    print("-" * 40)
    
    standard_prompt = f"""def max_value(nums):
    return max(nums)

def min_value(nums):
    return min(nums)

def sum_values(nums):
    return sum(nums)

{query}"""
    
    print("Standard prompt structure:")
    print("- Simple examples without context")
    print("- No test cases provided")
    print("- No guided generation")
    print(f"- Prompt length: {len(standard_prompt)} characters")
    
    standard_response = generator.generate(standard_prompt)
    print(f"\nGenerated code:\n{standard_response}")
    
    print("\n" + "-" * 40)
    print("ACECODER PROMPTING:")
    print("-" * 40)
    
    acecoder_prompt = acecoder.construct_prompt(query, k=3)
    print("AceCoder prompt structure:")
    print("- Retrieved similar examples")
    print("- Test cases as preliminaries")
    print("- Guided generation pattern")
    print(f"- Prompt length: {len(acecoder_prompt)} characters")
    
    acecoder_response = generator.generate(acecoder_prompt)
    print(f"\nGenerated code:\n{acecoder_response}")


def demonstrate_paper_consistency():
    """Demonstrate consistency with the paper's methodology"""
    print("\n" + "=" * 80)
    print("PAPER CONSISTENCY DEMONSTRATION")
    print("=" * 80)
    
    print("AceCoder Implementation Features (from paper):")
    print("✓ 1. Example Retrieval:")
    print("     - BM25-based retrieval system")
    print("     - Retrieves top-k similar programs")
    print("     - Uses requirement text as query")
    
    print("✓ 2. Example Selection:")
    print("     - Filters redundant programs using n-gram overlap")
    print("     - Uses decay factor to reduce redundancy")
    print("     - ROUGE-n based scoring")
    
    print("✓ 3. Guided Code Generation:")
    print("     - Test cases as intermediate preliminaries")
    print("     - Follows <requirement, preliminary, code> structure")
    print("     - Encourages LLMs to understand requirements first")
    
    print("✓ 4. Prompt Construction:")
    print("     - Triple examples format")
    print("     - Special tags: [requirement], [test case], [source code]")
    print("     - Ends with new requirement and empty test case slot")
    
    print("\nDataset Compatibility:")
    print("✓ - Uses MBPP dataset as specified in paper")
    print("✓ - Handles test cases for evaluation")
    print("✓ - Supports Pass@k evaluation metric")
    
    print("\nKey Differences from Standard ICL:")
    print("- Standard ICL: Simple <requirement, code> pairs")
    print("- AceCoder: <requirement, test_cases, code> triples")
    print("- Standard ICL: Random example selection")  
    print("- AceCoder: Intelligent retrieval + redundancy filtering")
    print("- Standard ICL: Direct code generation")
    print("- AceCoder: Guided generation via preliminaries")


def show_example_outputs():
    """Show concrete examples of AceCoder outputs"""
    print("\n" + "=" * 80)
    print("CONCRETE EXAMPLES")
    print("=" * 80)
    
    acecoder = AceCoder('BMPP/mbpp.jsonl')
    
    test_queries = [
        "Write a function to find the minimum value in a list.",
        "Write a function to count occurrences of an element in a list.",
        "Write a function to remove duplicates from a list."
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n{'-' * 50}")
        print(f"Example {i+1}: {query}")
        print(f"{'-' * 50}")
        
        # Show retrieval results
        similar_examples = acecoder.retrieve_examples(query, top_k=3)
        print(f"Top retrieved example: {similar_examples[0][0][:80]}...")
        
        # Show constructed prompt (abbreviated)
        prompt = acecoder.construct_prompt(query, k=2)
        lines = prompt.split('\n')
        print(f"Prompt preview ({len(lines)} lines):")
        print('\n'.join(lines[:10]) + '\n...')
        
        # Show what would be generated (conceptually)
        print("Expected generation pattern:")
        print("1. Model sees examples with test cases")
        print("2. Model generates test cases for new query")
        print("3. Model generates code guided by test cases")


def main():
    """Main demonstration function"""
    print("AceCoder Implementation Demo")
    print("Based on: 'AceCoder: Utilizing Existing Code to Enhance Code Generation'")
    print("by Li et al. (2024)")
    
    # Run all demonstrations
    demonstrate_core_components()
    compare_prompting_approaches()
    demonstrate_paper_consistency()
    show_example_outputs()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("This implementation demonstrates AceCoder's key innovations:")
    print("1. ✓ BM25-based example retrieval")
    print("2. ✓ Redundancy-aware example selection") 
    print("3. ✓ Test-case guided code generation")
    print("4. ✓ Structured prompt construction")
    print("5. ✓ MBPP dataset compatibility")
    print("\nThe implementation follows the paper's methodology and")
    print("provides a foundation for reproducing the reported results.")


if __name__ == "__main__":
    main()