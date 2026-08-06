import random

cycle = 0

temperature = 68
rpm = 1450
pressure = 5.3
vibration = 0.18


def update():

    global cycle
    global temperature
    global rpm
    global pressure
    global vibration

    cycle += 1

    # -----------------------------
    # Healthy Phase
    # -----------------------------
    if cycle < 40:

        temperature += random.uniform(-0.2, 0.3)
        rpm += random.uniform(-4, 4)
        pressure += random.uniform(-0.03, 0.03)
        vibration += random.uniform(-0.01, 0.01)

    # -----------------------------
    # Warning Phase
    # -----------------------------
    elif cycle < 80:

        temperature += random.uniform(0.2, 0.5)
        rpm += random.uniform(-8, 2)
        pressure -= random.uniform(0.00, 0.02)
        vibration += random.uniform(0.01, 0.03)

    # -----------------------------
    # Critical Phase
    # -----------------------------
    else:

        temperature += random.uniform(0.4, 0.8)
        rpm -= random.uniform(2, 8)
        pressure -= random.uniform(0.01, 0.05)
        vibration += random.uniform(0.02, 0.06)

    temperature = round(max(60, min(95, temperature)), 1)
    rpm = int(max(1300, min(1500, rpm)))
    pressure = round(max(4.5, min(6.0, pressure)), 2)
    vibration = round(max(0.10, min(1.20, vibration)), 2)

    # Restart after complete failure
    if cycle > 120:

        cycle = 0
        temperature = 68
        rpm = 1450
        pressure = 5.3
        vibration = 0.18

    return {
        "temperature": temperature,
        "rpm": rpm,
        "pressure": pressure,
        "vibration": vibration
    }