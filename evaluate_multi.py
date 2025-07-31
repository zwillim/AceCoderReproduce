#!/usr/bin/env python3
"""简化版多数据集评估脚本。

运行示例：
    python evaluate_multi.py -n 50
"""
import argparse
import json
import os
import random
from acecoder import AceCoder
from improved_generator import ImprovedCodeGenerator

# 指定要评估的数据集（名称: 路径）
DATASETS = {
    "mbpp": "BMPP/mbpp.jsonl",
    "mbjp": "mbxp/mbjp_release_v1.2.jsonl",
    "mbjsp": "mbxp/mbjsp_release_v1.2.jsonl",
}


def load_data(file_path: str, max_samples: int):
    """读取并随机采样 max_samples 条数据。"""
    rows = []
    if file_path.endswith(".jsonl"):
        with open(file_path, "r", encoding="utf-8") as fp:
            rows = [json.loads(line) for line in fp if line.strip()]
    else:
        with open(file_path, "r", encoding="utf-8") as fp:
            rows = json.load(fp)
    return random.sample(rows, max_samples) if len(rows) > max_samples else rows


def eval_dataset(name: str, path: str, max_samples: int):
    """返回 (acecoder_acc, baseline_acc)。"""
    acecoder = AceCoder(path, use_lucene=False)
    gen = ImprovedCodeGenerator()
    data = load_data(path, max_samples)

    ace_pass = base_pass = 0
    for item in data:
        query = item.get("prompt") or item.get("text", "")
        tests = item.get("test_list", [])

        # AceCoder prompting
        try:
            prompt = acecoder.construct_prompt(query, k=3)
            resp = gen.generate(prompt)
            code = resp.split("[source code]")[-1] if "[source code]" in resp else resp
            if acecoder.test_code(code, tests):
                ace_pass += 1
        except Exception:
            pass

        # Baseline prompting
        try:
            resp2 = gen.generate(f"Write a Python function for: {query}")
            if acecoder.test_code(resp2, tests):
                base_pass += 1
        except Exception:
            pass

    total = len(data)
    return ace_pass / total, base_pass / total


def main():
    parser = argparse.ArgumentParser(description="AceCoder 多数据集评估")
    parser.add_argument("-n", "--samples", type=int, default=50, help="每个数据集抽样数量")
    args = parser.parse_args()
    random.seed(42)

    # 尝试加载论文基准
    paper = {}
    if os.path.isfile("performance_results.json"):
        try:
            paper = json.load(open("performance_results.json", "r", encoding="utf-8"))
        except Exception:
            pass

    # 逐个评估
    results = {}
    for name, path in DATASETS.items():
        if not os.path.isfile(path):
            print(f"[跳过] 未找到数据集文件: {path}")
            continue
        ace_acc, base_acc = eval_dataset(name, path, args.samples)
        results[name] = (ace_acc, base_acc)
        print(f"{name}: AceCoder {ace_acc:.2%}, Baseline {base_acc:.2%}")

    # 输出对比
    print("\n=== 对比论文结果 ===")
    for name, (ace_acc, base_acc) in results.items():
        pa = paper.get(name, {}).get("acecoder")
        pb = paper.get(name, {}).get("baseline")
        pa_str = f"{pa:.2%}" if isinstance(pa, float) else "N/A"
        pb_str = f"{pb:.2%}" if isinstance(pb, float) else "N/A"
        print(f"{name:6s} | ours: {ace_acc:.2%}/{base_acc:.2%} | paper: {pa_str}/{pb_str}")


if __name__ == "__main__":
    main()