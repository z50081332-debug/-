from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.orchestrator import EarthquakeGraphRAGOrchestrator
from app.schemas import AddCaseRequest, EmergencyCase, FeedbackRequest, GenerateStrategyRequest

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Earthquake GraphRAG Agent",
        description="风险因果链 + 事故案例图谱 + GraphRAG 的地震应急策略生成 Agent",
        version="0.1.0",
    )
    orchestrator = EarthquakeGraphRAGOrchestrator()

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")

    @app.post("/generate_strategy")
    def generate_strategy(req: GenerateStrategyRequest) -> Dict:
        try:
            result = orchestrator.generate_strategy(
                disaster_text=req.disaster_text,
                event_id=req.event_id,
                top_k=req.top_k,
            )
            return asdict(result)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @app.get("/cases")
    def list_cases() -> List[Dict]:
        return [asdict(case) for case in orchestrator.cases]

    @app.post("/cases")
    def add_case(req: AddCaseRequest) -> Dict:
        try:
            case = EmergencyCase(**req.model_dump())
            return orchestrator.add_case(case)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.get("/graph")
    def export_graph() -> Dict:
        return orchestrator.export_graph()

    @app.post("/feedback")
    def feedback(req: FeedbackRequest) -> Dict:
        try:
            return orchestrator.add_feedback(req.event_id, req.feedback_text, req.corrected_measures)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    return app


app = create_app()
