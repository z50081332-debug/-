from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


@dataclass
class EmergencyCase:
    case_id: str
    title: str
    location: str
    magnitude: Optional[float]
    time: str
    scenario: str
    description: str
    risk_chain: List[str]
    measure_chain: List[str]
    lessons: List[str] = field(default_factory=list)
    source: str = "local"

    def to_text(self) -> str:
        return "\n".join([
            f"案例标题：{self.title}",
            f"地点：{self.location}",
            f"震级：{self.magnitude if self.magnitude is not None else '未知'}",
            f"时间：{self.time}",
            f"场景：{self.scenario}",
            f"案例描述：{self.description}",
            f"风险链：{' -> '.join(self.risk_chain)}",
            f"处置链：{' -> '.join(self.measure_chain)}",
            f"经验教训：{'；'.join(self.lessons)}",
        ])


@dataclass
class StrategyResult:
    event_id: str
    disaster_text: str
    extracted_event: Dict[str, Any]
    current_risk_chain: List[str]
    retrieved_cases: List[Dict[str, Any]]
    graph_evidence: Dict[str, Any]
    strategy: str
    created_at: str


class GenerateStrategyRequest(BaseModel):
    disaster_text: str = Field(..., description="输入新的地震灾情文本")
    event_id: Optional[str] = Field(default=None, description="可选事件 ID")
    top_k: int = Field(default=3, ge=1, le=10, description="检索相似案例数量")


class AddCaseRequest(BaseModel):
    case_id: str
    title: str
    location: str
    magnitude: Optional[float] = None
    time: str = "未知"
    scenario: str
    description: str
    risk_chain: List[str]
    measure_chain: List[str]
    lessons: List[str] = []
    source: str = "user"


class FeedbackRequest(BaseModel):
    event_id: str
    feedback_text: str
    corrected_measures: Optional[List[str]] = None
