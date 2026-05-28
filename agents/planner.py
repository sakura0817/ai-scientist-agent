import sys
sys.path.append('../logs')
from bailian_client import call_qwen


def run_planner(research_question):
    messages = [
        {
            "role": "system",
            "content": (
                "你是科研规划智能体，专注 AIGC 文本检测方向。"
                "你的任务是把用户问题拆解为可检索、可验证的研究子问题，"
                "并生成联网搜索关键词。"
            ),
        },
        {
            "role": "user",
            "content": f"""
用户研究问题：
{research_question}

请输出：
1. 研究问题边界
2. 3 个子问题
3. 8 个中英文搜索关键词
4. 需要重点关注的数据集、基线方法和评价指标
""",
        },
    ]
    return call_qwen(messages, enable_search=False)
