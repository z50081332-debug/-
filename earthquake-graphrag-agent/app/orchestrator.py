from __future__ import annotations

import datetime as dt
import json
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from app.agents.case_alignment_agent import CaseAlignmentAgent
from app.agents.dynamic_update_agent import DynamicUpdateAgent
from app.agents.event_extractor import EventExtractorAgent
from app.agents.graphrag_agent import GraphRAGAgent
from app.agents.risk_chain_agent import RiskChainAgent
from app.agents.strategy_agent import StrategyAgent
from app.config import settings
from app.schemas import EmergencyCase, StrategyResult
from app.services.llm import ClaudeClient, LLMClient, OllamaClient


class EarthquakeGraphRAGOrchestrator:
    """多 Agent 总编排器。"""

    def __init__(self, cases_file: Path | None = None):
        self.cases_file = cases_file or settings.cases_file
        self.cases = self.load_cases(self.cases_file)
        self.event_extractor = EventExtractorAgent()
        self.risk_chain_agent = RiskChainAgent()
        self.case_alignment_agent = CaseAlignmentAgent(self.cases)
        self.graphrag_agent = GraphRAGAgent(self.cases)
        llm: LLMClient | None = None
        if settings.use_anthropic and settings.anthropic_api_key:
            llm = ClaudeClient(
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model,
                base_url=settings.anthropic_base_url,
            )
        elif settings.use_ollama:
            llm = OllamaClient(model=settings.ollama_model, url=settings.ollama_url)
        self.strategy_agent = StrategyAgent(llm=llm)
        self.dynamic_update_agent = DynamicUpdateAgent(
            memory_file=settings.runtime_memory_file,
            feedback_file=settings.feedback_file,
        )

    @staticmethod
    def load_cases(path: Path) -> List[EmergencyCase]:
        if not path.exists():
            raise FileNotFoundError(f"案例文件不存在：{path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return [EmergencyCase(**item) for item in data]

    def save_cases(self) -> None:
        self.cases_file.parent.mkdir(parents=True, exist_ok=True)
        self.cases_file.write_text(
            json.dumps([asdict(case) for case in self.cases], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def reload_agents(self) -> None:
        self.case_alignment_agent = CaseAlignmentAgent(self.cases)
        self.graphrag_agent = GraphRAGAgent(self.cases)

    def add_case(self, case: EmergencyCase) -> Dict:
        if any(c.case_id == case.case_id for c in self.cases):
            raise ValueError(f"case_id 已存在：{case.case_id}")
        self.cases.append(case)
        self.save_cases()
        self.reload_agents()
        return asdict(case)

    def generate_strategy(self, disaster_text: str, event_id: str | None = None, top_k: int = 3) -> StrategyResult:
        event_id = event_id or f"evt_{uuid.uuid4().hex[:10]}"
        extracted_event = self.event_extractor.run(disaster_text)
        risk_chain = self.risk_chain_agent.run(extracted_event)
        aligned_cases = self.case_alignment_agent.run(disaster_text, risk_chain, top_k=top_k)
        graph_evidence = self.graphrag_agent.run(risk_chain, aligned_cases)
        strategy = self.strategy_agent.run(disaster_text, extracted_event, risk_chain, graph_evidence)

        result = StrategyResult(
            event_id=event_id,
            disaster_text=disaster_text,
            extracted_event=extracted_event,
            current_risk_chain=risk_chain,
            retrieved_cases=graph_evidence.get("retrieved_cases", []),
            graph_evidence=graph_evidence,
            strategy=strategy,
            created_at=dt.datetime.now().isoformat(timespec="seconds"),
        )
        self.dynamic_update_agent.save_result(result)
        return result

    def add_feedback(self, event_id: str, feedback_text: str, corrected_measures: List[str] | None = None) -> Dict:
        return self.dynamic_update_agent.add_feedback(event_id, feedback_text, corrected_measures)

    def export_graph(self) -> Dict:
        return self.graphrag_agent.export_graph()
