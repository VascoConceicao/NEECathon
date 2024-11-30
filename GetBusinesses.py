import requests
import time
import pandas as pd

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
        name = place['name']
        address = place.get('formatted_address', 'No address available')

        return name, address
    else:
        return None, None

def get_businesses(api_key, address, radius):
    lat, lng = get_coordinates_from_address(address, api_key)
    
    if lat is None or lng is None:
        return

    location = f"{lat},{lng}"

    # Construct the Places API URL with location, radius, and optional keyword
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    places = []
    while response.status_code == 200 and data['status'] == 'OK':
        print(f"\nNumber of results returned: {len(data['results'])}")
        for place in data['results']:
            place_id = place['place_id']
            name, address = get_place_details(api_key, place_id)
            print("dsadas")
            if name:
                lat = place['geometry']['location']['lat']
                lng = place['geometry']['location']['lng']
                places.append({
                    'Name': name,
                    'Address': address,
                    'Latitude': place['geometry']['location']['lat'],
                    'Longitude': place['geometry']['location']['lng'],
                    'First Type': place.get('types', [])[0]
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

    df = pd.DataFrame(places)
    return df

api_key = "AIzaSyBaMemUQHCLGIPsjckQlRs1Hi6EQiZaag0"

address = input("Endereço: ")
if address == "":
    address = "Avenida Rovisco Pais 1, Lisbon"

radius = 0
try:
    radius = int(input("Raio: "))
except ValueError:
    radius = 1000

df = get_businesses(api_key, address, radius)
print(df)