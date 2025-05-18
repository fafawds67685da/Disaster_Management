import requests
from database import help_stations

# Function to get distance using OSRM
def get_osrm_distance(origin, destination):
    url = f"http://router.project-osrm.org/route/v1/foot/{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
    params = {"overview": "full", "geometries": "geojson"}
    response = requests.get(url, params=params)
    data = response.json()
    if 'routes' in data and len(data['routes']) > 0:
        distance_km = data['routes'][0]['distance'] / 1000
        coords = [(coord[1], coord[0]) for coord in data['routes'][0]['geometry']['coordinates']]
        return distance_km, coords
    else:
        return float('inf'), []

# Function to get the nearest stations
def get_nearest_stations(user_location):
    distances = []
    for station in help_stations:
        dist_km, _ = get_osrm_distance(user_location, station)
        distances.append(dist_km)

    nearest = sorted(zip(help_stations, distances), key=lambda x: x[1])[:3]
    return nearest
