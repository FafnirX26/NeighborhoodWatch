import data_manager
import folium
from folium.plugins import HeatMap
from tqdm import tqdm
import webbrowser

u = input("Before we get started, would you like to update the database (not necessary if you did recently) [Y/n]: ")
df = data_manager.data(u)  # uses data manager module to load data

CRIME_COLORS = {
    'assault': 'red',
    'burglary': 'blue',
    'theft': 'green',
    'larceny': 'green',
    'vandalism': 'purple',
    'drug': 'orange',
    'property': 'beige'
}

def format_crime_data(s):
    parts = s.split()
    lat = float(parts[parts.index('Location') + 1][1:len(parts[parts.index('Location') + 1])-1])
    long = float(parts[parts.index('Location') + 2][0:len(parts[parts.index('Location') + 2])-1])

    d = {
        'Incident ID': parts[parts.index('ID') + 1],
        'Date': parts[parts.index('Start_Date_Time') + 1],
        'Time': parts[parts.index('Start_Date_Time') + 2],
        'Victim #': parts[parts.index('Victims') + 1],
        'Category': ' '.join(parts[parts.index('Name2') + 1: parts.index('Name3')-1]),
        'Crime': ' '.join(parts[parts.index('Name3') + 1: parts.index('City')]),
        'City': parts[parts.index('City') + 1],
        'Street View': f'<a href="https://www.google.com/maps?q=&layer=c&cbll={lat},{long}" target="_blank">View Street</a>'
    }

    formatted_string = ""
    for key, value in d.items():
        formatted_string += f"<strong>{key}</strong>: {value}<br>"

    return formatted_string

# Opt for heatmap
show_heatmap = input("Would you like to display the heatmap? [Y/n]: ").lower() == 'y'

# Filter by crime type
selected_types = input("Enter crime types to filter (comma-separated, leave blank for all): ").strip().lower().split(',')

if selected_types != ['']:
    df = df[df['Crime Name3'].str.lower().apply(lambda x: any(ct in x for ct in selected_types))]

# initiate app
print("Thank you for using NeighborhoodWatch!")
num_of_points = int(input("Enter the number of crimes to view (from latest): "))

lats = []
longs = []

for loc in df['Location']:
    lat = float(loc.strip('()').split(',')[0])
    long = float(loc.strip('()').split(',')[1])
    if lat > 0:
        lats.append(lat)
    if long < 0:
        longs.append(long)

if len(lats) == 0 or len(longs) == 0:
    print("No crimes match the selected criteria. Exiting.")
    exit()

# Create the base map
base_map = folium.Map(tiles='OpenStreetMap', location=(sum(lats) / len(lats), sum(longs) / len(longs)), zoom_start=12, prefer_canvas=True)

# Add the heatmap layer if opted in
if show_heatmap:
    heat_data = [[lat, long] for lat, long in zip(lats, longs)]
    HeatMap(heat_data).add_to(base_map)

# Add markers for individual crimes
for lat, long in tqdm(zip(lats[0:num_of_points], longs[0:num_of_points])):
    crime_data = df[df['Location'] == f'({lat}, {long})'].iloc[0]
    crime_type = crime_data['Crime Name3']
    color = 'gray'
    for cat in CRIME_COLORS:
        if cat in crime_type.lower():
            color = CRIME_COLORS[cat]

    folium.Marker(
        location=[lat, long],
        icon=folium.Icon(color=color),
        popup=folium.Popup(format_crime_data(str(crime_data)), min_width=120, max_width=160)
    ).add_to(base_map)

# Save and display the map
base_map.save("basemap.html")
webbrowser.open("basemap.html")
