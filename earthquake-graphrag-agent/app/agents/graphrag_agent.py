from __future__ import annotations

from typing import Dict, List

from app.schemas import EmergencyCase
from app.services.graph import SimpleCaseGraph


class GraphRAGAgent:
    """GraphRAG 检索 Agent：基于相似案例和事故图谱组织证据。"""

    def __init__(self, cases: List[EmergencyCase]):
        self.graph = SimpleCaseGraph(cases)

    def run(self, current_risk_chain: List[str], aligned_cases: List[Dict]) -> Dict:
        retrieved_cases = []
        risk_keywords = current_risk_chain[:]
        for item in aligned_cases:
            case: EmergencyCase = item["case"]
            retrieved_cases.append({
                "case_id": case.case_id,
                "title": case.title,
                "location": case.location,
                "scenario": case.scenario,
                "final_score": item["final_score"],
                "text_score": item["text_score"],
                "risk_overlap_score": item["risk_overlap_score"],
                "matched_risks": item["matched_risks"],
                "risk_chain": case.risk_chain,
                "measure_chain": case.measure_chain,
                "lessons": case.lessons,
            })
            risk_keywords.extend(case.risk_chain)

        related_measures = self.graph.find_related_measures(risk_keywords, limit=12)
        return {
            "retrieved_cases": retrieved_cases,
            "related_measures": related_measures,
            "graph_stats": {
                "node_count": len(self.graph.nodes),
                "edge_count": len(self.graph.edges),
            },
        }

    def export_graph(self) -> Dict:
        return self.graph.export()
