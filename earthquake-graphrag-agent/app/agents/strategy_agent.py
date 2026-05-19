from __future__ import annotations

from typing import Dict, List, Optional

from app.services.llm import LLMClient


class StrategyAgent:
    """策略生成 Agent：优先调用 LLM；失败时使用可控模板生成。"""

    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm

    def run(self, disaster_text: str, extracted_event: Dict, current_risk_chain: List[str], graph_evidence: Dict) -> str:
        if self.llm:
            prompt = self._build_prompt(disaster_text, extracted_event, current_risk_chain, graph_evidence)
            response = self.llm.generate(prompt)
            if response and len(response.strip()) > 100:
                return response.strip()
        return self._template_strategy(disaster_text, extracted_event, current_risk_chain, graph_evidence)

    @staticmethod
    def _build_prompt(disaster_text: str, extracted_event: Dict, current_risk_chain: List[str], graph_evidence: Dict) -> str:
        return f"""
你是地震应急决策辅助系统。请基于输入灾情、当前风险链和历史案例图谱证据，生成一份简洁、可执行、可追溯的应急处置策略。
要求：
1. 不要编造未给出的事实。
2. 必须说明策略依据来自哪些相似案例或风险链。
3. 输出结构包括：灾情判断、关键风险链、相似案例依据、优先处置措施、动态更新建议。
4. 语言正式、简洁，适合作为应急管理辅助决策文本。

【输入灾情】
{disaster_text}

【抽取要素】
{extracted_event}

【当前风险链】
{current_risk_chain}

【图谱检索证据】
{graph_evidence}
""".strip()

    @staticmethod
    def _template_strategy(disaster_text: str, extracted_event: Dict, current_risk_chain: List[str], graph_evidence: Dict) -> str:
        cases = graph_evidence.get("retrieved_cases", [])
        related_measures = graph_evidence.get("related_measures", [])
        magnitude = extracted_event.get("magnitude")
        location = extracted_event.get("location_hint", "未知区域")
        scenarios = "、".join(extracted_event.get("scenarios", []))

        lines: List[str] = []
        lines.append("# 地震应急处置策略生成结果")
        lines.append("")
        lines.append("## 1. 灾情判断")
        if magnitude is not None:
            lines.append(f"本次事件地点线索为{location}，震级约为{magnitude}级，场景类型可初步归类为：{scenarios}。")
        else:
            lines.append(f"本次事件地点线索为{location}，震级信息暂不完整，场景类型可初步归类为：{scenarios}。")
        lines.append("根据输入灾情，当前处置重点不应仅停留在震后救援本身，还需要同步考虑交通、通信、医疗、安置和次生灾害等链式风险。")
        lines.append("")

        lines.append("## 2. 当前关键风险链")
        for i, risk in enumerate(current_risk_chain, 1):
            lines.append(f"{i}. {risk}")
        lines.append("")

        lines.append("## 3. 相似案例与图谱依据")
        if not cases:
            lines.append("当前案例库中未检索到高相关案例，建议优先补充历史地震案例库。")
        else:
            for i, case in enumerate(cases, 1):
                lines.append(f"{i}. {case['title']}（匹配分数：{case['final_score']}）：场景为{case['scenario']}。")
                if case.get("matched_risks"):
                    lines.append(f"   - 匹配风险：{'；'.join(case['matched_risks'][:3])}")
                if case.get("lessons"):
                    lines.append(f"   - 可复用经验：{'；'.join(case['lessons'][:2])}")
        lines.append("")

        lines.append("## 4. 优先处置措施")
        measures = []
        for case in cases:
            measures.extend(case.get("measure_chain", []))
        measures.extend([item["measure"] for item in related_measures])
        measures = list(dict.fromkeys(measures))
        if not measures:
            measures = [
                "启动地震应急响应，建立统一指挥和信息报送机制",
                "开展人员搜救、伤员救治和危险区域封控",
                "核查道路、通信、电力、供水等生命线工程受损情况",
                "组织群众转移安置并保障基本生活物资",
                "持续监测余震和滑坡、崩塌、堰塞湖等次生灾害风险",
            ]
        for i, measure in enumerate(measures[:10], 1):
            lines.append(f"{i}. {measure}")
        lines.append("")

        lines.append("## 5. 动态更新建议")
        lines.append("1. 持续接入余震、道路抢通、通信恢复、伤亡统计、避难人数和物资缺口等实时信息。")
        lines.append("2. 当新增灾情改变风险链时，应重新执行案例对齐和 GraphRAG 检索，更新处置优先级。")
        lines.append("3. 对人工确认有效的处置措施和复盘结论，应写回案例库，形成可复用的事故案例图谱。")
        lines.append("4. 对低置信度或缺少依据的生成内容，应标记为人工复核项，避免直接作为最终指令。")
        return "\n".join(lines)
