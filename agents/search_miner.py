
import sys
sys.path.append('../logs')

from bailian_client import call_qwen


def run_search_miner(research_question, planner_result):
    messages = [
        {
            "role": "system",
            "content": (
                "你是文献挖掘智能体。你必须使用联网搜索结果整理真实论文、"
                "数据集、方法和指标。不要编造参考文献。"
            ),
        },
        {
            "role": "user",
            "content": f"""
研究问题：
{research_question}

规划结果：
{planner_result}

请基于联网搜索，整理 AIGC 文本检测领域的证据材料。

输出要求：
1. 5-8 篇真实相关论文或技术报告
2. 每篇论文的标题、年份、主要方法、与本问题的关系
3. 相关数据集，例如 HC3、M4、Ghostbuster 等
4. 常见基线方法，例如 DetectGPT、FastDetectGPT、RoBERTa detector、统计特征方法
5. 当前领域局限，重点关注跨模型泛化、对抗鲁棒性、跨域泛化
6. 最后列出 References，尽量包含 URL 或可检索来源
""",
        },
    ]
    return call_qwen(messages, enable_search=True, temperature=0.2)
