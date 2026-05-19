from __future__ import annotations

from typing import Dict, List

from app.schemas import EmergencyCase
from app.services.text_retriever import SimpleTextRetriever


class CaseAlignmentAgent:
    """案例对齐 Agent：融合文本相似度和风险链重合度，召回最相关历史案例。"""

    def __init__(self, cases: List[EmergencyCase]):
        self.cases = cases
        self.retriever = SimpleTextRetriever(cases)

    @staticmethod
    def _risk_overlap(current_risks: List[str], case: EmergencyCase) -> float:
        if not current_risks or not case.risk_chain:
            return 0.0
        hit = 0
        total = len(current_risks)
        for risk in current_risks:
            if any(token in case_risk or case_risk in token for case_risk in case.risk_chain for token in [risk]):
                hit += 1
            else:
                risk_chars = set(risk)
                best = 0.0
                for case_risk in case.risk_chain:
                    case_chars = set(case_risk)
                    union = len(risk_chars | case_chars)
                    inter = len(risk_chars & case_chars)
                    best = max(best, inter / union if union else 0.0)
                if best >= 0.25:
                    hit += best
        return min(hit / total, 1.0)

    def run(self, disaster_text: str, current_risk_chain: List[str], top_k: int = 3) -> List[Dict]:
        query = disaster_text + "\n" + "\n".join(current_risk_chain)
        text_results = self.retriever.search(query, top_k=max(top_k * 2, top_k))
        aligned = []
        for case, text_score in text_results:
            overlap_score = self._risk_overlap(current_risk_chain, case)
            final_score = 0.65 * text_score + 0.35 * overlap_score
            aligned.append({
                "case": case,
                "text_score": round(text_score, 4),
                "risk_overlap_score": round(overlap_score, 4),
                "final_score": round(final_score, 4),
                "matched_risks": self._matched_risks(current_risk_chain, case),
            })
        aligned.sort(key=lambda x: x["final_score"], reverse=True)
        return aligned[:top_k]

    @staticmethod
    def _matched_risks(current_risks: List[str], case: EmergencyCase) -> List[str]:
        matched = []
        for risk in current_risks:
            risk_chars = set(risk)
            for case_risk in case.risk_chain:
                case_chars = set(case_risk)
                union = len(risk_chars | case_chars)
                inter = len(risk_chars & case_chars)
                if union and inter / union >= 0.25:
                    matched.append(case_risk)
        return list(dict.fromkeys(matched))
