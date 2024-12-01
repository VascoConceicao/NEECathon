import folium
from folium.plugins import HeatMap

import math

def generate_circles(center, outer_radius, circle_radius=100):
    earth_radius = 6371000
    lat, lon = math.radians(center[0]), math.radians(center[1])
    
    lat_increment = circle_radius / earth_radius * (180 / math.pi)
    lon_increment = circle_radius / (earth_radius * math.cos(lat)) * (180 / math.pi)
    
    steps = int(outer_radius / circle_radius)
    points = []

    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            new_lat = center[0] + i * lat_increment
            new_lon = center[1] + j * lon_increment
            
            d_lat = math.radians(new_lat - center[0])
            d_lon = math.radians(new_lon - center[1])
            a = (math.sin(d_lat / 2) ** 2 +
                 math.cos(lat) * math.cos(math.radians(new_lat)) * math.sin(d_lon / 2) ** 2)
            distance = 2 * earth_radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            if distance <= outer_radius:
                points.append([new_lat, new_lon])
    
    return points

circle_centers = generate_circles((38.755283, -9.164438) , 6000)

#### Map ####
central_location = (38.7365005, -9.1371965)
map = folium.Map(location=central_location, zoom_start=15, tiles='cartodb positron')

folium.Marker(
    location=central_location,
    popup="Central Location (Lisbon)",
    icon=folium.Icon(color='red')
).add_to(map)

size = len(circle_centers)
for i, coordinate in enumerate(circle_centers):
    # print(f"Progress: {i}/{size}")
    folium.Marker(
        location=coordinate,
        icon=folium.Icon(color='blue')
    ).add_to(map)
    if i == 100:
        break

# # Create a heatmap with the nearby points
# heat_data = [[lat, lon] for lat, lon in locations]
# HeatMap(heat_data).add_to(map)

# Save the map to an HTML file
map.save("map.html")
