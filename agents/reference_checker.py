import sys
sys.path.append('../logs')


from bailian_client import call_qwen


def run_reference_checker(research_question, evidence, report):
    messages = [
        {
            "role": "system",
            "content": (
                "你是参考文献核验智能体。你的任务是基于联网搜索核验报告中的 References。"
                "你必须严格判断每条参考文献是否真实存在、题名是否准确、年份是否合理、"
                "是否与研究问题相关。不要为了显得完整而编造引用。"
            ),
        },
        {
            "role": "user",
            "content": f"""
研究问题：
{research_question}

前序联网搜索证据：
{evidence}

待核验研究计划：
{report}

请对研究计划中的 References 逐条核验。

输出要求：

## 1. 核验结论总览

用一句话说明参考文献整体可信度。

## 2. 逐条核验表

请用 Markdown 表格输出，字段如下：

| 编号 | 原始引用 | 核验状态 | 核验依据 | 风险说明 | 建议处理 |

核验状态只能使用：
- verified：联网搜索能确认基本真实，且与研究问题相关
- suspicious：题名、作者、年份、来源或相关性存在疑点
- not_found：联网搜索未找到可靠匹配结果

建议处理只能使用：
- keep：保留
- revise：修改后保留
- remove：删除

## 3. 建议保留的 References

只列出 verified 或经过明确修正后可保留的参考文献。
每条尽量包含：标题、作者、年份、来源链接或 arXiv/DOI 信息。

## 4. 需要删除或人工复查的 References

列出 suspicious 和 not_found 项，并说明原因。

重要要求：
- 必须联网搜索核验。
- 不能新增无法核验的文献。
- 如果报告中没有 References，请明确说明“未发现可核验参考文献”。
- 不要声称已经阅读全文，只能说“联网检索结果显示”。
""",
        },
    ]
    return call_qwen(messages, enable_search=True, temperature=0.1)