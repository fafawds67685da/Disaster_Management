import folium
from folium import Circle, PolyLine
import heapq

# Simulated graph (adjacency list)
graph = {
    (30.3245, 78.0430): [((30.3250, 78.0440), 0.15), ((30.3230, 78.0420), 0.18)],
    (30.3250, 78.0440): [((30.3245, 78.0430), 0.15), ((30.3260, 78.0450), 0.2)],
    (30.3230, 78.0420): [((30.3245, 78.0430), 0.18), ((30.3220, 78.0410), 0.25)],
    (30.3260, 78.0450): [((30.3250, 78.0440), 0.2), ((30.3280, 78.0460), 0.3)],
    (30.3280, 78.0460): [((30.3260, 78.0450), 0.3)],
    (30.3220, 78.0410): [((30.3230, 78.0420), 0.25)],
    (30.3200, 78.0400): [((30.3230, 78.0420), 0.2)],
    (30.3270, 78.0470): [((30.3280, 78.0460), 0.1)],
    (30.3210, 78.0435): [((30.3230, 78.0420), 0.22)],
    (30.3290, 78.0480): [((30.3280, 78.0460), 0.2)],
    (30.3240, 78.0415): [((30.3220, 78.0410), 0.18)],
    (30.3300, 78.0500): [((30.3290, 78.0480), 0.2)],
    (30.3285, 78.0455): [((30.3285, 78.0455), 0)]  # Adding missing help station to the graph
}

help_stations = [
    (30.3280, 78.0460), (30.3220, 78.0410), (30.3260, 78.0450),
    (30.3200, 78.0400), (30.3270, 78.0470), (30.3210, 78.0435),
    (30.3290, 78.0480), (30.3240, 78.0415), (30.3300, 78.0500),
    (30.3285, 78.0455)  # Ensure each station is a tuple of lat, long
]
user_location = (30.3245, 78.0430)

# Dijkstra's algorithm
def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0
    queue = [(0, start)]

    while queue:
        curr_distance, curr_node = heapq.heappop(queue)

        for neighbor, weight in graph.get(curr_node, []):
            distance = curr_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = curr_node
                heapq.heappush(queue, (distance, neighbor))

    return distances, previous

# Run Dijkstra
distances, prev = dijkstra(graph, user_location)

# Get top 3 nearest help stations
nearest = sorted(
    [(station, distances[station]) for station in help_stations],
    key=lambda x: x[1]
)[:3]

# Reconstruct shortest paths
def get_path(prev, end):
    path = []
    while end:
        path.append(end)
        end = prev[end]
    return path[::-1]

paths = [get_path(prev, station) for station, _ in nearest]

# --- Print the Graph separately ---
print("Graph (Adjacency List):")
for node, neighbors in graph.items():
    print(f"{node}: {neighbors}")

# --- Create Map ---
m = folium.Map(location=user_location, zoom_start=15)

# --- Full Graph Visualization ---
# Draw edges between all connected nodes
for node, neighbors in graph.items():
    for neighbor, _ in neighbors:
        PolyLine([node, neighbor], color="gray", weight=1, opacity=0.4).add_to(m)

# Draw all nodes (gray)
for node in graph:
    folium.CircleMarker(node, radius=4, color='gray', fill=True, fill_opacity=1).add_to(m)

# --- Highlighted Features ---
# User location
folium.Marker(user_location, tooltip="User", icon=folium.Icon(color='blue')).add_to(m)
Circle(user_location, radius=1500, color="blue", fill=False).add_to(m)

# Plot all help stations (without path)
for station in help_stations:
    folium.Marker([station[0], station[1]], tooltip=f"Help Station", icon=folium.Icon(color="gray")).add_to(m)

# Help stations & shortest paths
colors = ['green'] * 3 + ['red'] * (len(help_stations) - 3)
for idx, (station, dist) in enumerate(nearest):  # Corrected to iterate over the 'nearest' list
    color = colors[idx]
    # Corrected code: ensure station is treated as a tuple of lat, long
    folium.Marker([station[0], station[1]], tooltip=f"Help Station {idx+1} ({dist:.2f} km)", icon=folium.Icon(color=color)).add_to(m)
    # Only draw path for the nearest stations
    if idx < 3:
        PolyLine(paths[idx], color=color, weight=3, opacity=0.8).add_to(m)

# Save and display
m.save("nearest_help_stations_map.html")
print("✅ Map saved as 'nearest_help_stations_map.html'")
m
