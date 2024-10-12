from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import requests
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from folium.plugins import HeatMap

app = Flask(__name__)

def update():
    response = requests.get("https://data.montgomerycountymd.gov/api/views/icn6-v9z3/rows.csv?accessType=DOWNLOAD", stream=True)
    response.raise_for_status()
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    with open('Crime.csv', 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            progress_bar.update(len(chunk))
            f.write(chunk)
    progress_bar.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        show_map = request.form.get("map")

        if show_map:
            redirect('/map')
        update_db = request.form.get('update_db', 'n')
        if update_db.lower() == 'y':
            update()  # Update the Crime.csv if the user chooses to

        # Get other form inputs
        show_heatmap = request.form.get('show_heatmap', 'y')
        crime_types = request.form.get('crime_types', '').strip().lower().split(',')
        num_points = int(request.form.get('num_points', 100))
        address = request.form.get('address', '').strip()
        range_miles = float(request.form.get('range_miles', 5).strip())

        # Load data
        df = data()  # You need to implement this function based on your needs
        generate_map(df, show_heatmap == 'y', crime_types, num_points, address, range_miles)

        return redirect(url_for('map'))

    return render_template('index.html')

@app.route('/map')
def map():
    return render_template('map.html')  # Render the map template

def generate_map(df, show_heatmap_option, crime_types, num_points, address, range_miles):
    CRIME_COLORS = {
        'assault': 'red',
        'burglary': 'blue',
        'theft': 'green',
        'larceny': 'green',
        'vandalism': 'purple',
        'drug': 'orange',
        'property': 'beige'
    }

    if crime_types != ['']:
        df = df[df['Crime Name3'].str.lower().apply(lambda x: any(ct.strip() in x for ct in crime_types))]

    lats = []
    longs = []

    for loc in df['Location']:
        lat = float(loc.strip('()').split(',')[0])
        long = float(loc.strip('()').split(',')[1])
        if lat > 0:
            lats.append(lat)
        if long < 0:
            longs.append(long)

    # Use geopy to geocode the address into lat, long
    geolocator = Nominatim(user_agent="crime_mapper")
    location = geolocator.geocode(address)
    if location:
        center_lat, center_long = location.latitude, location.longitude
    else:
        center_lat, center_long = sum(lats) / len(lats), sum(longs) / len(longs)

    # Filter crimes based on the range
    filtered_lats = []
    filtered_longs = []
    for lat, long in zip(lats, longs):
        if geodesic((center_lat, center_long), (lat, long)).miles <= range_miles:
            filtered_lats.append(lat)
            filtered_longs.append(long)

    # Create base map
    base_map = folium.Map(location=(center_lat, center_long), zoom_start=16)

    if show_heatmap_option:
        heat_data = [[lat, long] for lat, long in zip(filtered_lats, filtered_longs)]
        HeatMap(heat_data).add_to(base_map)

    for i, (lat, long) in enumerate(zip(filtered_lats[0:num_points], filtered_longs[0:num_points])):
        crime_data = df[df['Location'] == f'({lat}, {long})'].iloc[0]
        crime_type = crime_data['Crime Name3']
        color = 'gray'
        for cat in CRIME_COLORS:
            if cat in crime_type.lower():
                color = CRIME_COLORS[cat]

        # Prepare the popup content
        popup_content = f"<strong>Incident ID:</strong> {crime_data['Incident ID']}<br>" \
                        f"<strong>Date:</strong> {crime_data['Start_Date_Time']}<br>" \
                        f"<strong>Victims:</strong> {crime_data['Victims']}<br>" \
                        f"<strong>Crime Type:</strong> {crime_type}<br>" \
                        f"<strong>Location:</strong> {crime_data['Location']}<br>" \
                        f'<a href="https://www.google.com/maps?q=&layer=c&cbll={lat},{long}" target="_blank">View Street</a>'

        folium.Marker(location=[lat, long], icon=folium.Icon(color=color),
                      popup=folium.Popup(popup_content, min_width=120, max_width=160)).add_to(base_map)

    map_file = "templates/map.html"
    base_map.save(map_file)

def data():
    df = pd.read_csv("Crime.csv")
    df = df[['Incident ID', 'Start_Date_Time', 'End_Date_Time', 'Victims', 'Crime Name2', 'Crime Name3', 'City', 'State', 'Zip Code', 'Street Name', 'Location']]
    df['Start_Date_Time'] = pd.to_datetime(df['Start_Date_Time'], format='%m/%d/%Y %I:%M:%S %p')
    df['End_Date_Time'] = pd.to_datetime(df['End_Date_Time'], format='%m/%d/%Y %I:%M:%S %p')
    df = df.sort_values('Start_Date_Time', ascending=False)
    return df

if __name__ == "__main__":
    app.run(debug=True)
