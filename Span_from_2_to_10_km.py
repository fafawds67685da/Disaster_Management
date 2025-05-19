import requests
import folium
from folium import PolyLine, Marker

# Step 1: User Location
user_location = (30.3245, 78.0430)  # Example: somewhere in Dehradun

# Step 2: Use Overpass API to get help stations and their phone numbers
def fetch_help_stations(lat, lon, radius=2000):
    query = f"""
    [out:json];
    (
      node(around:{radius},{lat},{lon})[amenity~"hospital|clinic|doctors|police"];
      way(around:{radius},{lat},{lon})[amenity~"hospital|clinic|doctors|police"];
    );
    out center tags;
    """
    response = requests.post("https://overpass.kumi.systems/api/interpreter", data=query)
    data = response.json()

    locations = []
    for el in data['elements']:
        if 'lat' in el and 'lon' in el:
            latlon = (el['lat'], el['lon'])
        elif 'center' in el:
            latlon = (el['center']['lat'], el['center']['lon'])
        else:
            continue

        tags = el.get('tags', {})
        phone = tags.get('contact:phone') or tags.get('phone')
        if phone:  # Only add stations with phone numbers
            locations.append((latlon, phone))
    return locations

# Function to find help stations within an expanding radius
def find_nearest_help_stations(lat, lon, min_stations=3, initial_radius=2000, max_radius=10000, radius_step=1500):
    radius = initial_radius
    while radius <= max_radius:
        help_stations_raw = fetch_help_stations(lat, lon, radius)
        if len(help_stations_raw) >= min_stations:
            return help_stations_raw
        radius += radius_step
    return fetch_help_stations(lat, lon, max_radius)  # Return whatever was found within max_radius

# Fetch help stations with an expanding radius if needed
help_stations_raw = find_nearest_help_stations(user_location[0], user_location[1])

print(f"✅ Found {len(help_stations_raw)} help stations with phone numbers")

# Step 3: Calculate OSRM driving distances
def osrm_distance(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=false"
    response = requests.get(url)
    if response.status_code == 200:
        routes = response.json()
        return routes['routes'][0]['distance'] / 1000  # in km
    return float('inf')

# Step 4: Compute distances to each help station
distance_list = []
for (station_coords, phone) in help_stations_raw:
    dist = osrm_distance(user_location, station_coords)
    distance_list.append(((station_coords, phone), dist))

# Step 5: Sort and keep top stations
nearest_stations = sorted(distance_list, key=lambda x: x[1])

# Step 6: Build Map
m = folium.Map(location=user_location, zoom_start=15)

# Add user
folium.Marker(user_location, tooltip="You", icon=folium.Icon(color="blue")).add_to(m)

# Add all help stations (red or green)
for (loc, phone), dist in distance_list:
    color = "green" if loc in [station[0] for station, _ in nearest_stations[:min(3, len(nearest_stations))]] else "red"
    tooltip = f"Phone: {phone}" if phone else "No contact info"
    folium.CircleMarker(loc, radius=6, color=color, fill=True, fill_opacity=0.9, tooltip=tooltip).add_to(m)

    # Print coordinates and distance from user location
    print(f"Help Station Location: {loc} | Distance: {dist:.2f} km")

# Add and connect nearest help stations
for i, ((station, phone), dist) in enumerate(nearest_stations[:min(3, len(nearest_stations))]):
    # Add green marker with label
    info = f"Help Station {i+1} ({dist:.2f} km)"
    info += f" | 📞 {phone}"
    Marker(station, tooltip=info, icon=folium.Icon(color="green")).add_to(m)

    # Fetch route coordinates from OSRM
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{user_location[1]},{user_location[0]};{station[1]},{station[0]}?overview=full&geometries=geojson"
    route_resp = requests.get(osrm_url).json()
    route_coords = route_resp['routes'][0]['geometry']['coordinates']
    route_latlon = [(lat, lon) for lon, lat in route_coords]

    # Draw polyline
    PolyLine(route_latlon, color="green", weight=4, opacity=0.8).add_to(m)

# Print the coordinates, distance, and phone numbers of the nearest help stations
print("\nThe nearest help stations with their details are:")
for i, ((station, phone), dist) in enumerate(nearest_stations[:min(3, len(nearest_stations))]):
    print(f"\nHelp Station {i+1}:")
    print(f"Coordinates: {station}")
    print(f"Distance: {dist:.2f} km")
    print(f"Phone Number: {phone}")

# If there are fewer than 3 help stations with phone numbers, print a message
if len(nearest_stations) < 3:
    print(f"\nOnly {len(nearest_stations)} help stations with phone numbers were found. No third station available.")

# Save map
m.save("auto_helpstations_map.html")
print("✅ Map with nearest help stations saved as 'auto_helpstations_map.html'")
m
