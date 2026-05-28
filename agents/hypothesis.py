import sys
sys.path.append('../logs')

from bailian_client import call_qwen


def run_hypothesis_generator(research_question, evidence):
    messages = [
        {
            "role": "system",
            "content": (
                "你是科学假设生成智能体。你只能基于给定证据生成假设，"
                "不能编造论文和实验结果。每个假设必须可验证。"
            ),
        },
        {
            "role": "user",
            "content": f"""
研究问题：
{research_question}

联网搜索证据：
{evidence}

请生成 3 个候选科学假设。每个假设包含：
1. Problem Statement：当前具体局限
2. Rationale：为什么这个思路可能有效
3. Technical Details：需要的技术手段
4. Datasets：可用数据集
5. Baselines：对比方法
6. Metrics：评价指标
7. Expected Results：预期结果，不能夸大
8. Supporting Evidence：引用上面证据中的论文或事实
""",
        },
    ]
    return call_qwen(messages, enable_search=False, temperature=0.5)
