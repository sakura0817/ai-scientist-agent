import sys
sys.path.append('../logs')


from bailian_client import call_qwen


def run_report_writer(research_question, evidence, hypotheses, critique):
    messages = [
        {
            "role": "system",
            "content": (
                "你是科研计划写作智能体。你要按照比赛要求，生成标准化的"
                "《科学假设与研究计划》。必须结构清晰，引用真实可追溯。"
            ),
        },
        {
            "role": "user",
            "content": f"""
研究问题：
{research_question}

联网搜索证据：
{evidence}

候选假设：
{hypotheses}

评审意见：
{critique}

请生成最终《科学假设与研究计划》，必须包含以下字段：

1. 标题（Paper Title）
2. 摘要（Paper Abstract）
3. 待研究问题（Problem Statement）
4. 解决思路（Rationale）
5. 必要的技术手段（Technical Details）
6. 数据集（Datasets）
   - Source：假设推演依据的历史数据
   - Target：验证实验所需的数据特征
7. 方法论（Methods）
8. 实验设计（Experiments）
   - Baselines
   - Metrics
9. 实验结果或可行性验证（Results）
10. 参考论文（References）

要求：
- 不要编造实验已经完成。
- 如果没有真实实验结果，Results 写“预期可行性验证方案”。
- References 必须来自上面的联网搜索证据。
""",
        },
    ]
    return call_qwen(messages, enable_search=False, temperature=0.3)
