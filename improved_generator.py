#!/usr/bin/env python3
"""
Improved Code Generator for AceCoder evaluation
This generator tries to understand the pattern from examples and generate appropriate code
"""

import re
import json
from typing import List, Dict, Tuple


class ImprovedCodeGenerator:
    """Improved code generator that learns from AceCoder prompts"""
    
    def __init__(self):
        self.function_patterns = {}
        
    def extract_function_signature(self, code: str) -> Tuple[str, List[str]]:
        """Extract function name and parameters from code"""
        # Find function definition
        func_match = re.search(r'def\s+(\w+)\s*\((.*?)\):', code)
        if func_match:
            func_name = func_match.group(1)
            params = [p.strip() for p in func_match.group(2).split(',') if p.strip()]
            return func_name, params
        return "solution", ["*args"]
    
    def analyze_test_cases(self, test_cases: List[str]) -> Dict:
        """Analyze test cases to understand the expected behavior"""
        analysis = {
            'function_name': None,
            'input_types': [],
            'output_type': None,
            'examples': []
        }
        
        for test_case in test_cases:
            if '->' in test_case:
                call_part, result_part = test_case.split('->', 1)
                call_part = call_part.strip().lstrip('#').strip()
                result_part = result_part.strip()
                
                # Extract function name
                if '(' in call_part:
                    func_name = call_part.split('(')[0].strip()
                    if func_name and not analysis['function_name']:
                        analysis['function_name'] = func_name
                
                # Extract arguments
                arg_match = re.search(r'\((.*)\)', call_part)
                if arg_match:
                    args_str = arg_match.group(1)
                    analysis['examples'].append({
                        'input': args_str,
                        'output': result_part
                    })
        
        return analysis
    
    def extract_examples_from_prompt(self, prompt: str) -> List[Dict]:
        """Extract examples from AceCoder prompt"""
        examples = []
        
        # Split by requirement sections
        sections = prompt.split('[requirement]')[1:]  # Skip first empty part
        
        for section in sections[:-1]:  # Skip the last section (query)
            parts = section.split('[test case]')
            if len(parts) >= 2:
                requirement = parts[0].strip()
                
                test_and_code = parts[1].split('[source code]')
                if len(test_and_code) >= 2:
                    test_cases_str = test_and_code[0].strip()
                    code = test_and_code[1].strip()
                    
                    # Extract test cases
                    test_cases = []
                    for line in test_cases_str.split('\n'):
                        if line.strip().startswith('#') and '->' in line:
                            test_cases.append(line.strip())
                    
                    examples.append({
                        'requirement': requirement,
                        'test_cases': test_cases,
                        'code': code
                    })
        
        return examples
    
    def generate_similar_function(self, requirement: str, test_cases: List[str], examples: List[Dict]) -> str:
        """Generate function based on requirement, test cases, and examples"""
        analysis = self.analyze_test_cases(test_cases)
        
        # If we have a function name from test cases, use it
        func_name = analysis.get('function_name', 'solution')
        
        # Look for similar patterns in examples
        best_example = None
        max_similarity = 0
        
        for example in examples:
            similarity = self.calculate_similarity(requirement, example['requirement'])
            if similarity > max_similarity:
                max_similarity = similarity
                best_example = example
        
        # Generate code based on the best example and test cases
        if best_example and analysis['examples']:
            return self.adapt_code_from_example(best_example, func_name, analysis)
        
        # Fallback to simple pattern-based generation
        return self.generate_simple_function(func_name, requirement, analysis)
    
    def calculate_similarity(self, req1: str, req2: str) -> float:
        """Calculate similarity between two requirements"""
        words1 = set(req1.lower().split())
        words2 = set(req2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def adapt_code_from_example(self, example: Dict, func_name: str, analysis: Dict) -> str:
        """Adapt code from example to match current requirements"""
        original_code = example['code']
        
        # Extract the original function
        func_match = re.search(r'def\s+\w+\s*\([^)]*\):(.*?)(?=\n\n|\n$|$)', original_code, re.DOTALL)
        if func_match:
            func_body = func_match.group(1)
            
            # Try to determine parameters from test cases
            if analysis['examples']:
                first_example = analysis['examples'][0]
                input_str = first_example['input']
                
                # Count parameters
                param_count = input_str.count(',') + 1 if input_str.strip() else 0
                
                if param_count == 1:
                    params = "arg"
                elif param_count == 2:
                    params = "arg1, arg2"
                elif param_count == 3:
                    params = "arg1, arg2, arg3"
                else:
                    params = "*args"
                
                # Generate adapted function
                adapted_code = f"def {func_name}({params}):{func_body}"
                return adapted_code
        
        return self.generate_simple_function(func_name, example['requirement'], analysis)
    
    def generate_simple_function(self, func_name: str, requirement: str, analysis: Dict) -> str:
        """Generate simple function based on patterns"""
        req_lower = requirement.lower()
        
        # Use a default function name if none provided
        if not func_name or func_name == 'None':
            func_name = 'solution'
        
        # Determine parameters
        if analysis['examples']:
            first_example = analysis['examples'][0]
            input_str = first_example['input']
            param_count = input_str.count(',') + 1 if input_str.strip() else 0
            
            if param_count == 1:
                params = "arg"
            elif param_count == 2:
                params = "arg1, arg2"
            elif param_count == 3:
                params = "arg1, arg2, arg3"
            else:
                params = "arg1, arg2, arg3"  # Default to 3 params instead of *args
        else:
            params = "arg"
        
        param_list = [p.strip() for p in params.split(',')]
        first_param = param_list[0]
        
        # Generate based on keywords in requirement
        if 'find' in req_lower and 'maximum' in req_lower:
            return f"""def {func_name}({params}):
    if isinstance({first_param}, list):
        return max({first_param})
    return {first_param}"""
        
        elif 'find' in req_lower and 'minimum' in req_lower:
            return f"""def {func_name}({params}):
    if isinstance({first_param}, list):
        return min({first_param})
    return {first_param}"""
        
        elif 'count' in req_lower:
            if len(param_list) >= 2:
                second_param = param_list[1]
                return f"""def {func_name}({params}):
    return {first_param}.count({second_param})"""
            else:
                return f"""def {func_name}({params}):
    return len({first_param})"""
        
        elif 'sum' in req_lower:
            return f"""def {func_name}({params}):
    if isinstance({first_param}, (list, tuple)):
        return sum({first_param})
    return {first_param}"""
        
        elif 'sort' in req_lower:
            return f"""def {func_name}({params}):
    if isinstance({first_param}, list):
        return sorted({first_param})
    return {first_param}"""
        
        elif 'shared' in req_lower or 'common' in req_lower or 'intersection' in req_lower:
            if len(param_list) >= 2:
                second_param = param_list[1]
                return f"""def {func_name}({params}):
    return list(set({first_param}) & set({second_param}))"""
            else:
                return f"""def {func_name}({params}):
    return {first_param}"""
        
        elif 'remove' in req_lower or 'delete' in req_lower:
            if len(param_list) >= 2:
                second_param = param_list[1]
                return f"""def {func_name}({params}):
    if isinstance({first_param}, list):
        return [x for x in {first_param} if x != {second_param}]
    elif isinstance({first_param}, str):
        return {first_param}.replace(str({second_param}), '')
    return {first_param}"""
            else:
                return f"""def {func_name}({params}):
    return {first_param}"""
        
        # Default case
        return f"""def {func_name}({params}):
    # Simple implementation
    return {first_param}"""
    
    def generate(self, prompt: str) -> str:
        """Generate code from AceCoder prompt"""
        # Extract examples from prompt
        examples = self.extract_examples_from_prompt(prompt)
        
        # Extract the query (last requirement)
        sections = prompt.split('[requirement]')
        if len(sections) < 2:
            return "def solution(): return None"
        
        last_section = sections[-1]
        parts = last_section.split('[test case]')
        
        requirement = parts[0].strip()
        
        # Extract test cases if available
        test_cases = []
        if len(parts) > 1:
            test_cases_str = parts[1].strip()
            for line in test_cases_str.split('\n'):
                if line.strip().startswith('#') and '->' in line:
                    test_cases.append(line.strip())
        
        # Generate code
        generated_code = self.generate_similar_function(requirement, test_cases, examples)
        
        # Add test cases as comments
        if test_cases:
            comments = '\n'.join(test_cases)
            return f"# Test cases:\n{comments}\n\n{generated_code}"
        else:
            return generated_code


def test_improved_generator():
    """Test the improved generator"""
    generator = ImprovedCodeGenerator()
    
    # Test with a simple prompt
    test_prompt = """[requirement]
Write a function to find the shared elements from the given two lists.

[test case]
# similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) -> (4, 5)
# similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) -> (3, 4)

[source code]
def similar_elements(test_tup1, test_tup2):
  res = tuple(set(test_tup1) & set(test_tup2))
  return (res)

[requirement]
Write a function to find the common elements in two lists.

[test case]
# common_elements([1, 2, 3, 4], [3, 4, 5, 6]) -> [3, 4]
"""
    
    result = generator.generate(test_prompt)
    print("Generated code:")
    print(result)


if __name__ == "__main__":
    test_improved_generator()