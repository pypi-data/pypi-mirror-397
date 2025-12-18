import math


def degrees_to_radians(deg):
    """Convert degrees to radians."""
    return deg * math.pi / 180


def radians_to_degrees(rad):
    """Convert radians to degrees."""
    return rad * 180 / math.pi


def km_to_m(km):
    """Convert kilometers to meters."""
    return km * 1000


def m_to_km(m):
    """Convert meters to kilometers."""
    return m / 1000


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth (km).
    Inputs are latitude and longitude in degrees.
    """
    R = 6371.0  # Earth radius in kilometers

    phi1 = degrees_to_radians(lat1)
    phi2 = degrees_to_radians(lat2)
    dphi = degrees_to_radians(lat2 - lat1)
    dlambda = degrees_to_radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
