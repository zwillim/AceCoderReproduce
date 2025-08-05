#!/usr/bin/env python3
"""
Configuration Examples for AceCoder Evaluation
AceCoder评估的配置示例

This script shows how to configure different method combinations for evaluation.
这个脚本展示如何为评估配置不同的方法组合。
"""

from config import config


def example_acecoder_only():
    """Example: Run only AceCoder"""
    """示例：仅运行AceCoder"""
    print("=" * 60)
    print("EXAMPLE 1: AceCoder Only")
    print("示例1：仅AceCoder")
    print("=" * 60)
    
    # Configure to run only AceCoder
    config.methods_to_run = ['acecoder']
    config.max_samples = 5  # Small sample for demo
    
    print("Configuration:")
    print("配置:")
    print(f"Methods to run: {config.methods_to_run}")
    print(f"运行方法: {config.methods_to_run}")
    print(f"Max samples: {config.max_samples}")
    print(f"最大样本数: {config.max_samples}")


def example_acecoder_vs_zero_shot():
    """Example: Compare AceCoder with Zero-shot"""
    """示例：比较AceCoder与Zero-shot"""
    print("=" * 60)
    print("EXAMPLE 2: AceCoder vs Zero-shot")
    print("示例2：AceCoder vs Zero-shot")
    print("=" * 60)
    
    # Configure to run AceCoder and Zero-shot
    config.methods_to_run = ['acecoder', 'zero_shot']
    config.max_samples = 10
    
    print("Configuration:")
    print("配置:")
    print(f"Methods to run: {config.methods_to_run}")
    print(f"运行方法: {config.methods_to_run}")
    print(f"Max samples: {config.max_samples}")
    print(f"最大样本数: {config.max_samples}")


def example_all_methods():
    """Example: Run all available methods"""
    """示例：运行所有可用方法"""
    print("=" * 60)
    print("EXAMPLE 3: All Methods")
    print("示例3：所有方法")
    print("=" * 60)
    
    # Configure to run all methods
    config.methods_to_run = ['acecoder', 'zero_shot', 'few_shot', 'cot']
    config.max_samples = 15
    
    print("Configuration:")
    print("配置:")
    print(f"Methods to run: {config.methods_to_run}")
    print(f"运行方法: {config.methods_to_run}")
    print(f"Max samples: {config.max_samples}")
    print(f"最大样本数: {config.max_samples}")


def example_baseline_comparison():
    """Example: Compare all baseline methods"""
    """示例：比较所有基线方法"""
    print("=" * 60)
    print("EXAMPLE 4: Baseline Methods Only")
    print("示例4：仅基线方法")
    print("=" * 60)
    
    # Configure to run only baseline methods
    config.methods_to_run = ['zero_shot', 'few_shot', 'cot']
    config.max_samples = 8
    
    print("Configuration:")
    print("配置:")
    print(f"Methods to run: {config.methods_to_run}")
    print(f"运行方法: {config.methods_to_run}")
    print(f"Max samples: {config.max_samples}")
    print(f"最大样本数: {config.max_samples}")


def example_custom_configuration():
    """Example: Custom configuration with specific methods"""
    """示例：使用特定方法的自定义配置"""
    print("=" * 60)
    print("EXAMPLE 5: Custom Configuration")
    print("示例5：自定义配置")
    print("=" * 60)
    
    # Custom configuration
    config.methods_to_run = ['acecoder', 'few_shot']  # Only AceCoder and Few-shot
    config.max_samples = 12
    config.temperature = 0.2  # Higher temperature for more diversity
    config.max_tokens = 800   # Shorter responses
    
    print("Configuration:")
    print("配置:")
    print(f"Methods to run: {config.methods_to_run}")
    print(f"运行方法: {config.methods_to_run}")
    print(f"Max samples: {config.max_samples}")
    print(f"最大样本数: {config.max_samples}")
    print(f"Temperature: {config.temperature}")
    print(f"温度参数: {config.temperature}")
    print(f"Max tokens: {config.max_tokens}")
    print(f"最大令牌数: {config.max_tokens}")


def show_usage_examples():
    """Show usage examples with command line"""
    """展示命令行使用示例"""
    print("=" * 60)
    print("COMMAND LINE USAGE EXAMPLES")
    print("命令行使用示例")
    print("=" * 60)
    
    print("1. Run only AceCoder:")
    print("1. 仅运行AceCoder:")
    print("   python evaluate_acecoder.py --eval --methods acecoder")
    print()
    
    print("2. Compare AceCoder with Zero-shot:")
    print("2. 比较AceCoder与Zero-shot:")
    print("   python evaluate_acecoder.py --eval --methods acecoder zero_shot")
    print()
    
    print("3. Run all methods:")
    print("3. 运行所有方法:")
    print("   python evaluate_acecoder.py --eval --methods acecoder zero_shot few_shot cot")
    print()
    
    print("4. Run only baseline methods:")
    print("4. 仅运行基线方法:")
    print("   python evaluate_acecoder.py --eval --methods zero_shot few_shot cot")
    print()
    
    print("5. Run demonstration only:")
    print("5. 仅运行演示:")
    print("   python evaluate_acecoder.py --demo")
    print()
    
    print("6. Default behavior (demo + evaluation with config methods):")
    print("6. 默认行为（演示 + 使用配置方法评估）:")
    print("   python evaluate_acecoder.py")


if __name__ == "__main__":
    print("AceCoder Configuration Examples")
    print("AceCoder配置示例")
    print("=" * 60)
    
    # Show all examples
    example_acecoder_only()
    print()
    
    example_acecoder_vs_zero_shot()
    print()
    
    example_all_methods()
    print()
    
    example_baseline_comparison()
    print()
    
    example_custom_configuration()
    print()
    
    show_usage_examples()
    
    print("\n" + "=" * 60)
    print("To use any of these configurations, modify config.py or use command line arguments.")
    print("要使用这些配置中的任何一个，请修改config.py或使用命令行参数。")
    print("=" * 60)