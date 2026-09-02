from app.services.ai.query_analyzer import QueryAnalyzer

def test_query_analyzer_extraction():
    analyzer = QueryAnalyzer()
    res = analyzer.analyze("Show SUVs under ₹20 lakh with 6 airbags")

    assert res["parsed_constraints"]["body_type"] == "SUV"
    assert res["parsed_constraints"]["price_max"] == 2000000.0
    assert res["parsed_constraints"]["min_airbags"] == 6

def test_query_analyzer_ev():
    analyzer = QueryAnalyzer()
    res = analyzer.analyze("Best EV for city driving with mileage above 18 km/l")

    assert res["parsed_constraints"]["fuel_type"] == "EV"
    assert res["parsed_constraints"]["min_mileage"] == 18.0
