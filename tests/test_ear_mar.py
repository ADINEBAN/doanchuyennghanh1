from app.features.monitoring.metrics import eye_aspect_ratio, mouth_aspect_ratio


def test_eye_aspect_ratio_returns_positive_value():
    points = [
        (0.0, 0.0),
        (1.0, 2.0),
        (2.0, 2.0),
        (4.0, 0.0),
        (2.0, -2.0),
        (1.0, -2.0),
    ]

    value = eye_aspect_ratio(points)

    assert value > 0


def test_mouth_aspect_ratio_returns_positive_value():
    points = [
        (0.0, 0.0),
        (1.0, 2.0),
        (2.0, 2.5),
        (3.0, 2.0),
        (6.0, 0.0),
        (3.0, -2.0),
        (2.0, -2.5),
        (1.0, -2.0),
    ]

    value = mouth_aspect_ratio(points)

    assert value > 0
