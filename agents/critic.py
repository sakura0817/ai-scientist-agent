import sys
sys.path.append('../logs')


from bailian_client import call_qwen


def run_critic(research_question, evidence, hypotheses):
    messages = [
        {
            "role": "system",
            "content": (
                "你是严格的科研评审智能体。你要从创新性、自洽性、可验证性、"
                "引用真实性和实验可落地性角度批判候选假设。"
            ),
        },
        {
            "role": "user",
            "content": f"""
研究问题：
{research_question}

证据材料：
{evidence}

候选假设：
{hypotheses}

请完成评审：
1. 给每个假设打分：创新性 0-5，可验证性 0-5，应用潜力 0-5
2. 指出每个假设的主要风险
3. 判断哪个假设最适合作为 MVP 演示案例
4. 给出修改后的最终推荐假设
5. 检查 References 是否可能存在编造风险
""",
        },
    ]
    return call_qwen(messages, enable_search=False, temperature=0.2)