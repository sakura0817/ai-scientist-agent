from pathlib import Path

from agents.planner import run_planner
from agents.search_miner import run_search_miner
from agents.hypothesis import run_hypothesis_generator
from agents.critic import run_critic
from agents.report import run_report_writer
from agents.reference_checker import run_reference_checker

def main():
    print("AIGC 文本检测 AI Scientist MVP")
    print("=" * 40)

    research_question = input(
        "请输入研究问题（直接回车使用默认问题）：\n> "
        
    ).strip()

    if not research_question:
        research_question = "如何提升 AIGC 文本检测模型的跨模型泛化能力,用中文回答？"

    print("\n[1/6] Research Planner 正在拆解问题...")
    planner_result = run_planner(research_question)
    print("完成")

    print("\n[2/6] Web Search Miner 正在联网搜索和整理证据...")
    evidence = run_search_miner(research_question, planner_result)
    print("完成")

    print("\n[3/6] Hypothesis Generator 正在生成候选假设...")
    hypotheses = run_hypothesis_generator(research_question, evidence)
    print("完成")

    print("\n[4/6] Critic Reviewer 正在评审候选假设...")
    critique = run_critic(research_question, evidence, hypotheses)
    print("完成")

    print("\n[5/6] Report Writer 正在生成最终研究计划...")
    report = run_report_writer(research_question, evidence, hypotheses, critique)
    print("完成")

    print("\n[6/6] Reference Checker 正在联网核验参考文献...")
    reference_check = run_reference_checker(research_question, evidence, report)
    print("完成")

    Path("outputs").mkdir(exist_ok=True)

    report_path = Path("outputs") / "research_plan.md"
    check_path = Path("outputs") / "reference_check.md"
    final_path = Path("outputs") / "research_plan_with_check.md"

    report_path.write_text(report, encoding="utf-8")
    check_path.write_text(reference_check, encoding="utf-8")
    final_path.write_text(
        report
        + "\n\n---\n\n"
        + "# Reference Check\n\n"
        + reference_check,
        encoding="utf-8",
    )

    print(f"\n最终报告已保存：{report_path}")
    print(f"引用核验结果已保存：{check_path}")
    print(f"合并版报告已保存：{final_path}")



if __name__ == "__main__":
    main()