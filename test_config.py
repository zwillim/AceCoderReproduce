#!/usr/bin/env python3
"""
Test script to verify AceCoder configuration
测试脚本来验证 AceCoder 配置
"""

from config import config
from improved_generator import ImprovedCodeGenerator


def test_config():
    """Test configuration loading and validation"""
    """测试配置加载和验证"""
    
    print("Testing AceCoder Configuration")
    print("测试 AceCoder 配置")
    print("=" * 50)
    
    # 打印当前配置
    config.print_config()
    
    # 验证配置
    print("\nValidating configuration...")
    print("正在验证配置...")
    
    if config.validate():
        print("✅ Configuration is valid!")
        print("✅ 配置有效！")
    else:
        print("❌ Configuration validation failed!")
        print("❌ 配置验证失败！")
        return False
    
    # 测试生成器初始化
    print("\nTesting generator initialization...")
    print("正在测试生成器初始化...")
    
    try:
        generator = ImprovedCodeGenerator()
        print("✅ Generator initialized successfully!")
        print("✅ 生成器初始化成功！")
        
        # 测试简单生成
        print("\nTesting code generation...")
        print("正在测试代码生成...")
        
        test_prompt = """[requirement]
Write a function to find the maximum value in a list.

[test case]
# find_max([1, 2, 3, 4, 5]) -> 5
# find_max([10, 20, 30]) -> 30

[source code]
def find_max(numbers):
    return max(numbers)

[requirement]
Write a function to find the minimum value in a list.

[test case]
# find_min([1, 2, 3, 4, 5]) -> 1
"""
        
        result = generator.generate(test_prompt)
        print("✅ Code generation successful!")
        print("✅ 代码生成成功！")
        print(f"\nGenerated code preview:")
        print(f"生成的代码预览:")
        print("-" * 30)
        print(result[:200] + "..." if len(result) > 200 else result)
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Generator test failed: {e}")
        print(f"❌ 生成器测试失败: {e}")
        return False


def test_real_llm():
    """Test real LLM API if configured"""
    """如果配置了真实 LLM API 则进行测试"""
    
    if not config.use_real_llm:
        print("\nSkipping real LLM test (not configured)")
        print("跳过真实 LLM 测试（未配置）")
        return True
    
    print("\nTesting real LLM API...")
    print("正在测试真实 LLM API...")
    
    try:
        generator = ImprovedCodeGenerator()
        
        # 简单测试
        test_prompt = "Write a Python function to add two numbers."
        
        result = generator.generate(test_prompt)
        print("✅ Real LLM API test successful!")
        print("✅ 真实 LLM API 测试成功！")
        print(f"\nGenerated code:")
        print(f"生成的代码:")
        print("-" * 30)
        print(result)
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Real LLM API test failed: {e}")
        print(f"❌ 真实 LLM API 测试失败: {e}")
        print("This might be due to:")
        print("这可能是因为:")
        print("1. Invalid API key")
        print("1. API 密钥无效")
        print("2. Network connectivity issues")
        print("2. 网络连接问题")
        print("3. API rate limits")
        print("3. API 速率限制")
        return False


def main():
    """Main test function"""
    """主测试函数"""
    
    print("AceCoder Configuration Test")
    print("AceCoder 配置测试")
    print("=" * 50)
    
    # 测试基本配置
    config_ok = test_config()
    
    if config_ok:
        # 测试真实 LLM（如果配置了）
        llm_ok = test_real_llm()
        
        if llm_ok:
            print("\n🎉 All tests passed! You can now run the evaluation.")
            print("🎉 所有测试通过！你现在可以运行评估了。")
            print("\nTo run evaluation:")
            print("运行评估:")
            print("python evaluate_acecoder.py")
        else:
            print("\n⚠️  Basic configuration is OK, but LLM API has issues.")
            print("⚠️  基本配置正常，但 LLM API 有问题。")
            print("You can still run evaluation with rule-based generator.")
            print("你仍然可以使用基于规则的生成器运行评估。")
    else:
        print("\n❌ Configuration test failed. Please fix the issues above.")
        print("❌ 配置测试失败。请修复上述问题。")


if __name__ == "__main__":
    main() 