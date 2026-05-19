from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

from app.schemas import EmergencyCase


@dataclass
class GraphEdge:
    source: str
    target: str
    relation: str
    case_id: str


class SimpleCaseGraph:
    """
    简单事故案例图谱。
    节点类型：case、risk、measure、lesson。
    边类型：has_risk、causes、handled_by、has_measure、has_lesson。
    """

    def __init__(self, cases: List[EmergencyCase]):
        self.cases = {case.case_id: case for case in cases}
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[GraphEdge] = []
        self.adj: Dict[str, List[GraphEdge]] = defaultdict(list)
        self._build(cases)

    def _add_node(self, node_id: str, node_type: str, text: str, **attrs) -> None:
        if node_id not in self.nodes:
            self.nodes[node_id] = {"id": node_id, "type": node_type, "text": text, **attrs}

    def _add_edge(self, source: str, target: str, relation: str, case_id: str) -> None:
        edge = GraphEdge(source=source, target=target, relation=relation, case_id=case_id)
        self.edges.append(edge)
        self.adj[source].append(edge)

    @staticmethod
    def _risk_node(text: str) -> str:
        return f"risk::{text}"

    @staticmethod
    def _measure_node(text: str) -> str:
        return f"measure::{text}"

    @staticmethod
    def _lesson_node(text: str) -> str:
        return f"lesson::{text}"

    @staticmethod
    def _case_node(case_id: str) -> str:
        return f"case::{case_id}"

    def _build(self, cases: List[EmergencyCase]) -> None:
        for case in cases:
            cnode = self._case_node(case.case_id)
            self._add_node(cnode, "case", case.title, case_id=case.case_id, location=case.location)

            previous_risk = None
            for risk in case.risk_chain:
                rnode = self._risk_node(risk)
                self._add_node(rnode, "risk", risk)
                self._add_edge(cnode, rnode, "has_risk", case.case_id)
                if previous_risk:
                    self._add_edge(previous_risk, rnode, "causes", case.case_id)
                previous_risk = rnode

            for measure in case.measure_chain:
                mnode = self._measure_node(measure)
                self._add_node(mnode, "measure", measure)
                self._add_edge(cnode, mnode, "has_measure", case.case_id)
                if case.risk_chain:
                    # 将每个处置措施关联到案例最后一个高层风险节点，便于检索“风险 -> 措施”。
                    self._add_edge(self._risk_node(case.risk_chain[-1]), mnode, "handled_by", case.case_id)

            for lesson in case.lessons:
                lnode = self._lesson_node(lesson)
                self._add_node(lnode, "lesson", lesson)
                self._add_edge(cnode, lnode, "has_lesson", case.case_id)

    def find_related_measures(self, risk_keywords: List[str], limit: int = 10) -> List[Dict]:
        results = []
        seen = set()
        for node_id, node in self.nodes.items():
            if node["type"] != "risk":
                continue
            risk_text = node["text"]
            if any(k in risk_text or risk_text in k for k in risk_keywords):
                for edge in self.adj.get(node_id, []):
                    if edge.relation == "handled_by":
                        target = self.nodes.get(edge.target)
                        if target and target["text"] not in seen:
                            seen.add(target["text"])
                            results.append({
                                "risk": risk_text,
                                "measure": target["text"],
                                "case_id": edge.case_id,
                            })
        return results[:limit]

    def export(self) -> Dict:
        return {
            "nodes": list(self.nodes.values()),
            "edges": [asdict(edge) for edge in self.edges],
        }
