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
        rating = place.get('rating', 'No rating')
        user_ratings_total = place.get('user_ratings_total', 0)

        return rating, user_ratings_total
    else:
        return None, 0

def get_junta_de_freguesia(api_key, lat, lng):
    # Montar a URL para a API de Geocoding
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
    
    # Fazer a requisição
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK':
        # Iterar pelos componentes do endereço
        for result in data['results']:
            for component in result['address_components']:
                if 'administrative_area_level_3' in component['types']:
                    freguesia = component['long_name']
                    
        return freguesia
    else:
        return None, None

def get_businesses(api_key, address, radius):   
    lat, lng = get_coordinates_from_address(address, api_key)
    
    if lat is None or lng is None:
        return

    location = f"{lat},{lng}"

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    places = []
    while response.status_code == 200 and data['status'] == 'OK':
        print(f"\nNumber of results returned: {len(data['results'])}")
        for i, place in enumerate(data['results']):
            print(i)
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

    df = pd.DataFrame(places)
    return df

def main(api_key):

    address = input("Endereço: ")
    if address == "":
        address = "Avenida Rovisco Pais 1, Lisbon"

    radius = 0
    try:
        radius = int(input("Raio: "))
    except ValueError:
        radius = 1000

    df = get_businesses(api_key, address, radius)
    print(df.iloc[:, 1:])

    freguesias = []
    for _, row in df.iterrows():
        freguesia = get_junta_de_freguesia(api_key, row['Latitude'], row['Longitude'])
        print(freguesia)
        freguesias.append(freguesia)
    df.insert(7, 'Freguesias', freguesias)

    # df.to_csv('businesses.csv', index=False)
    df.to_csv('businesses.csv', mode='a', header=not pd.io.common.file_exists('businesses.csv'), index=False)
    df = pd.read_csv('businesses.csv')
    df = df.drop_duplicates(subset=['Place ID'])
    df.to_csv('businesses.csv', index=False)

api_key = "AIzaSyBaMemUQHCLGIPsjckQlRs1Hi6EQiZaag0"
main(api_key)