from app.services.scoring import compute_nis, impact_level


def test_compute_nis_matches_formula():
    score = compute_nis(0.8, 0.7, 0.9, 0.6, 0.5)
    assert score == 0.735


def test_impact_level_bucket():
    assert impact_level(0.81) == "强影响"
    assert impact_level(0.55) == "中等影响"

