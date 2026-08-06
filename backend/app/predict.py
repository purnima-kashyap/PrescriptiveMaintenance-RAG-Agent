def calculate_health(data):

    score = 100

    # Temperature
    if data["temperature"] > 75:
        score -= (data["temperature"] - 75) * 2

    # Vibration
    if data["vibration"] > 0.40:
        score -= (data["vibration"] - 0.40) * 60

    # Pressure
    if data["pressure"] < 5.0:
        score -= (5.0 - data["pressure"]) * 40

    # RPM
    if data["rpm"] < 1400:
        score -= (1400 - data["rpm"]) * 0.2

    return max(0, min(100, round(score)))


def predict_fault(data):

    health = calculate_health(data)

    if health >= 90:
        return "Healthy"

    elif health >= 75:
        return "Warning"

    elif health >= 50:
        return "Maintenance Required"

    elif health >= 25:
        return "Critical"

    else:
        return "Bearing Failure Predicted"