import math
from typing import Tuple, Optional

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) in meters.
    """
    R = 6371000.0  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c

def compute_spatial_similarity(distance_meters: float, max_radius_meters: float = 200.0) -> float:
    """
    Converts distance in meters to a spatial proximity score from 0.0 to 1.0.
    1.0 means same spot (0m), 0.0 means >= max_radius_meters.
    """
    if distance_meters <= 0.0:
        return 1.0
    if distance_meters >= max_radius_meters:
        return 0.0
    # Linear decay or exponential decay
    return max(0.0, 1.0 - (distance_meters / max_radius_meters))

def compute_temporal_similarity(time_diff_hours: float, max_window_hours: float = 720.0) -> float:
    """
    Converts time difference in hours to temporal similarity score from 0.0 to 1.0.
    30 days = 720 hours window.
    """
    if time_diff_hours <= 0.0:
        return 1.0
    if time_diff_hours >= max_window_hours:
        return 0.1
    return max(0.1, 1.0 - (time_diff_hours / max_window_hours))
