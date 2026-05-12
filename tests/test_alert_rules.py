from app.features.monitoring.engine import DetectionMetrics, DrowsinessEngine


def test_engine_triggers_closed_eyes_alert():
    engine = DrowsinessEngine(
        ear_threshold=0.23,
        ear_consec_frames=20,
        mar_threshold=0.65,
        yawn_consec_frames=15,
        drowsy_alert_seconds=2,
    )

    result = engine.evaluate(
        DetectionMetrics(
            ear_value=0.2,
            mar_value=0.2,
            eyes_closed_frames=20,
            yawn_frames=0,
        )
    )

    assert result.should_alert is True
    assert result.alert_type == "closed_eyes"
