#!/usr/bin/env python3
"""
Configuration file for AceCoder evaluation
AceCoder评估的配置文件
"""

import os
from typing import Optional, List


class AceCoderConfig:
    """Configuration class for AceCoder evaluation"""
    """AceCoder评估的配置类"""
    
    def __init__(self):
        # LLM API 配置
        self.api_key: str = None
        self.model_name: str = "gpt-3.5-turbo"
        self.api_base: str = "https://api.openai.com/v1"
        
        # 评估配置
        self.max_samples: int = 10
        self.dataset_path: str = "BMPP/sanitized-mbpp.json"
        self.training_data_path: str = "BMPP/mbpp.jsonl"
        
        # 方法配置 - 指定要运行的方法列表
        # 可选方法: 'acecoder', 'zero_shot', 'few_shot', 'cot'
        self.methods_to_run: List[str] = ['acecoder', 'zero_shot', 'few_shot', 'cot']
        
        # 生成器配置
        self.temperature: float = 0.1
        self.max_tokens: int = 1000
        
        # 从环境变量加载配置
        self._load_from_env()
    
    def set_llm_config(self, use_real_llm: bool = False, api_key: Optional[str] = None,
                       model_name: str = "gpt-3.5-turbo", api_base: str = "https://api.openai.com/v1"):
        """直接设置LLM配置"""
        """Set LLM configuration directly"""
        self.use_real_llm = use_real_llm
        self.api_key = api_key
        self.model_name = model_name
        self.api_base = api_base
    
    def set_evaluation_config(self, max_samples: int = 10, dataset_path: str = "BMPP/sanitized-mbpp.json",
                             training_data_path: str = "BMPP/mbpp.jsonl", methods_to_run: List[str] = None):
        """直接设置评估配置"""
        """Set evaluation configuration directly"""
        self.max_samples = max_samples
        self.dataset_path = dataset_path
        self.training_data_path = training_data_path
        if methods_to_run is not None:
            self.methods_to_run = methods_to_run
    
    def set_generator_config(self, temperature: float = 0.1, max_tokens: int = 1000):
        """直接设置生成器配置"""
        """Set generator configuration directly"""
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        """Load configuration from environment variables"""
        
        # LLM API 配置
        if os.getenv('ACECODER_USE_REAL_LLM', '').lower() in ('true', '1', 'yes'):
            self.use_real_llm = True
        
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ACECODER_API_KEY')
        self.model_name = os.getenv('ACECODER_MODEL_NAME', self.model_name)
        self.api_base = os.getenv('ACECODER_API_BASE', self.api_base)
        
        # 评估配置
        max_samples_env = os.getenv('ACECODER_MAX_SAMPLES')
        if max_samples_env:
            try:
                self.max_samples = int(max_samples_env)
            except ValueError:
                print(f"Warning: Invalid ACECODER_MAX_SAMPLES value: {max_samples_env}")
        
        self.dataset_path = os.getenv('ACECODER_DATASET_PATH', self.dataset_path)
        self.training_data_path = os.getenv('ACECODER_TRAINING_DATA_PATH', self.training_data_path)
        
        # 生成器配置
        temperature_env = os.getenv('ACECODER_TEMPERATURE')
        if temperature_env:
            try:
                self.temperature = float(temperature_env)
            except ValueError:
                print(f"Warning: Invalid ACECODER_TEMPERATURE value: {temperature_env}")
        
        max_tokens_env = os.getenv('ACECODER_MAX_TOKENS')
        if max_tokens_env:
            try:
                self.max_tokens = int(max_tokens_env)
            except ValueError:
                print(f"Warning: Invalid ACECODER_MAX_TOKENS value: {max_tokens_env}")
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        """Validate configuration"""
        
        if self.use_real_llm and not self.api_key:
            print("Error: API key is required when use_real_llm is True")
            print("错误: 当 use_real_llm 为 True 时需要 API 密钥")
            return False
        
        if self.max_samples <= 0:
            print("Error: max_samples must be positive")
            print("错误: max_samples 必须为正数")
            return False
        
        if not os.path.exists(self.dataset_path):
            print(f"Error: Dataset file not found: {self.dataset_path}")
            print(f"错误: 找不到数据集文件: {self.dataset_path}")
            return False
        
        if not os.path.exists(self.training_data_path):
            print(f"Error: Training data file not found: {self.training_data_path}")
            print(f"错误: 找不到训练数据文件: {self.training_data_path}")
            return False
        
        return True
    
    def print_config(self):
        """打印当前配置"""
        """Print current configuration"""
        print("=" * 50)
        print("ACECODER CONFIGURATION")
        print("ACECODER 配置")
        print("=" * 50)
        print(f"Use Real LLM: {self.use_real_llm}")
        print(f"使用真实LLM: {self.use_real_llm}")
        print(f"Model Name: {self.model_name}")
        print(f"模型名称: {self.model_name}")
        print(f"API Base: {self.api_base}")
        print(f"API基础URL: {self.api_base}")
        print(f"Max Samples: {self.max_samples}")
        print(f"最大样本数: {self.max_samples}")
        print(f"Dataset Path: {self.dataset_path}")
        print(f"数据集路径: {self.dataset_path}")
        print(f"Training Data Path: {self.training_data_path}")
        print(f"训练数据路径: {self.training_data_path}")
        print(f"Temperature: {self.temperature}")
        print(f"温度参数: {self.temperature}")
        print(f"Max Tokens: {self.max_tokens}")
        print(f"最大令牌数: {self.max_tokens}")
        print(f"Methods to Run: {', '.join(self.methods_to_run)}")
        print(f"运行方法: {', '.join(self.methods_to_run)}")
        if self.api_key:
            print(f"API Key: {'*' * (len(self.api_key) - 8) + self.api_key[-8:]}")
            print(f"API密钥: {'*' * (len(self.api_key) - 8) + self.api_key[-8:]}")
        else:
            print("API Key: Not set")
            print("API密钥: 未设置")
        print("=" * 50)


# 全局配置实例
config = AceCoderConfig() 