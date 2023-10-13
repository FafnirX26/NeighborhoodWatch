import data_manager
import folium
from tqdm import tqdm
import webbrowser

u = input("Before we get started, would you like to update the database (not necessary if you did recently) [Y/n]: ")
df = data_manager.data(u)  # uses data manager module i wrote to load data


def format_crime_data(s):
    # split the string into parts
    parts = s.split()
    # create a dictionary to hold the parts
    d = {'Incident ID': parts[parts.index('ID')+1],
         'Date': parts[parts.index('Start_Date_Time')+1],
         'Time': parts[parts.index('Start_Date_Time')+2],
         'Victim #': parts[parts.index('Victims')+1],
         'Crime': parts[parts.index('Crime')+2]+' '+parts[parts.index('Crime')+3]+' '+parts[parts.index('Crime')+4],
         'City': parts[parts.index('City')+1]}
    formatted_string = ""
    for key, value in d.items():
        formatted_string += f"<strong>{key}</strong>: {value}<br>"

    return formatted_string


# initiate app
print("Thank you for using NeighborhoodWatch!")
num_of_points = int(input("Enter amount of crimes to view (from latest): "))
lats = []
longs = []

for loc in df['Location']:
    lat = float(loc.strip('()').split(',')[0])
    long = float(loc.strip('()').split(',')[1])
    if lat > 0:
        lats.append(lat)
    if long < 0:
        longs.append(long)
base_map = folium.Map(tiles='OpenStreetMap', location=(sum(lats) / len(lats), sum(longs) / len(longs)), zoom_start=12,
                      prefer_canvas=True)

for lat, long in tqdm(zip(lats[0:num_of_points], longs[0:num_of_points])):
    crime_data = df[df['Location'] == f'({lat}, {long})']
    folium.Marker(location=[lat, long],
                  icon=folium.Icon(color='red'),
                  popup=folium.Popup(format_crime_data(str(crime_data.iloc[0])), min_width=120, max_width=120)
                  ).add_to(base_map)

base_map.save("basemap.html")
webbrowser.open("basemap.html")
