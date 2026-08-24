def predict_green_time(vehicle_count):
    """
    Predicts the green time given a vehicle count from YOLOv8.
    Timer Logic:
    - Count == 0 -> 0s
    - 15s increments up to 120s based on count
    """
    if vehicle_count == 0:
        return 0, 'LOW'
        
    if vehicle_count <= 10:
        density = 'LOW'
        predicted_time = 15
    elif vehicle_count <= 20:
        density = 'LOW-MEDIUM'
        predicted_time = 30
    elif vehicle_count <= 30:
        density = 'MEDIUM'
        predicted_time = 45
    elif vehicle_count <= 40:
        density = 'HIGH'
        predicted_time = 60
    elif vehicle_count <= 50:
        density = 'HIGH'
        predicted_time = 75
    elif vehicle_count <= 60:
        density = 'VERY HIGH'
        predicted_time = 90
    elif vehicle_count <= 70:
        density = 'SEVERE'
        predicted_time = 105
    else:
        density = 'SEVERE'
        predicted_time = 120
        
    return predicted_time, density
