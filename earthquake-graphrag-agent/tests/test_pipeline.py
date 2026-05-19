from app.orchestrator import EarthquakeGraphRAGOrchestrator


def test_generate_strategy():
    orch = EarthquakeGraphRAGOrchestrator()
    result = orch.generate_strategy(
        "某山区发生6.8级地震，震中附近乡镇房屋倒塌，道路塌方，通信中断，部分群众被困，并且仍有余震风险。",
        top_k=2,
    )
    assert result.current_risk_chain
    assert result.retrieved_cases
    assert "地震应急处置策略" in result.strategy
