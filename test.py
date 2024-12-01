import math

def generate_circles(center, outer_radius, circle_radius=50):
    """
    Generate a list of [latitude, longitude] for circles of radius 50m
    within the given radius around a center coordinate.
    
    Parameters:
    - center: tuple of (latitude, longitude) in decimal degrees.
    - outer_radius: radius of the larger circle in meters.
    - circle_radius: radius of each smaller circle in meters (default 50m).
    
    Returns:
    - List of [latitude, longitude] for the centers of the smaller circles.
    """
    earth_radius = 6371000  # Earth's radius in meters
    lat, lon = math.radians(center[0]), math.radians(center[1])
    
    # Calculate the degree increments for the grid
    lat_increment = circle_radius / earth_radius * (180 / math.pi)
    lon_increment = circle_radius / (earth_radius * math.cos(lat)) * (180 / math.pi)
    
    # Determine the number of steps in each direction
    steps = int(outer_radius / circle_radius)
    points = []

    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            # Calculate new point
            new_lat = center[0] + i * lat_increment
            new_lon = center[1] + j * lon_increment
            
            # Check if the point is within the outer_radius
            d_lat = math.radians(new_lat - center[0])
            d_lon = math.radians(new_lon - center[1])
            a = (math.sin(d_lat / 2) ** 2 +
                 math.cos(lat) * math.cos(math.radians(new_lat)) * math.sin(d_lon / 2) ** 2)
            distance = 2 * earth_radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            if distance <= outer_radius:
                points.append([new_lat, new_lon])
    
    return points

# Example Usage
center_coordinate = (38.845508, -9.244438)  # Example: New York City
outer_radius = 18000  # Radius in meters
circle_centers = generate_circles(center_coordinate, outer_radius)

print(f"Generated {len(circle_centers)} circle centers:")
print(circle_centers)
print(len(circle_centers))