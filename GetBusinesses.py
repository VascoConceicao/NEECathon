import requests
import time
import pandas as pd
import math
import csv

def get_coordinates_from_address(address, api_key):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(geocode_url)
    data = response.json()

    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        lat = location['lat']
        lng = location['lng']
        return lat, lng
    else:
        print("Address not found.")
        return None, None

def get_place_details(api_key, place_id):
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"
    response = requests.get(details_url)
    data = response.json()

    if data['status'] == 'OK':
        place = data['result']
        rating = place.get('rating', 'No rating')
        user_ratings_total = place.get('user_ratings_total', 0)

        return rating, user_ratings_total
    else:
        return None, 0

def get_junta_de_freguesia(api_key, lat, lng):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
    
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK':
        for result in data['results']:
            for component in result['address_components']:
                if 'administrative_area_level_3' in component['types']:
                    freguesia = component['long_name']
                    
        return freguesia
    else:
        return None, None

def generate_circles(center, outer_radius, circle_radius):
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

def create_header(file):
    fieldnames = ['Place ID', 'Name', 'Latitude', 'Longitude', 'Type', 'Rating', 'Reviews', 'Freguesia']

    with open('businesses.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
    
def save_data(file, data):
    df = pd.DataFrame(data)
    df.to_csv('businesses.csv', mode='a', header=not pd.io.common.file_exists('businesses.csv'), index=False)
    df = pd.read_csv('businesses.csv')
    df = df.drop_duplicates(subset=['Place ID'])
    freguesias = []
    for _, row in df.iterrows():
        freguesia = get_junta_de_freguesia(api_key, row['Latitude'], row['Longitude'])
        # print(freguesia)
        freguesias.append(freguesia)

    df['Freguesia'] = freguesias
    df.to_csv('businesses.csv', index=False)

def get_businesses(api_key, address, file):
    if address == "default":
        lat, lng = 38.755283, -9.164438
    else:
        lat, lng = get_coordinates_from_address(address, api_key)
        if lat is None or lng is None:
            return
    inner_radius = 20
    points = generate_circles([lat, lng], 6000, inner_radius)
    # points = [[lat, lng]]
    while True:
        try:
            places = []
            size = len(points)
            for i, lat_lng in enumerate(points):
                print(f"Progress: {i}/{size}")
                if i % 1000 == 0 and i != 0:
                    save_data(file, places)
                    places = []

                location = f"{lat_lng[0]},{lat_lng[1]}"
                url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={inner_radius}&key={api_key}"
                response = requests.get(url)
                data = response.json()

                while response.status_code == 200 and data['status'] == 'OK':
                    print(f"\nNumber of results returned: {len(data['results'])}")
                    for j, place in enumerate(data['results']):
                        print(j)
                        place_id = place['place_id']
                        rating, user_ratings_total = get_place_details(api_key, place_id)

                        places.append({
                            'Place ID': place_id,
                            'Name': place['name'],
                            'Latitude': place['geometry']['location']['lat'],
                            'Longitude': place['geometry']['location']['lng'],
                            'Type': place.get('types', []),
                            'Rating': rating,
                            'Reviews': user_ratings_total
                        })

                    if 'next_page_token' in data:
                        next_page_token = data['next_page_token']
                        time.sleep(2)   
                        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page_token}&key={api_key}"
                        response = requests.get(url)
                        data = response.json()
                    else:
                        break
                else:
                    print("No businesses found or error occurred.")
        except ConnectionError:
            print("CONNECTION ERROR!!!")
            continue
        break
    save_data(file, places)

def main(api_key):
    address = input("Endereço: ")
    if address == "":
        address = "default"

    # create_header('businesses.csv')
    places = get_businesses(api_key, address, 'businesses.csv')

api_key = "AIzaSyBaMemUQHCLGIPsjckQlRs1Hi6EQiZaag0"
main(api_key)