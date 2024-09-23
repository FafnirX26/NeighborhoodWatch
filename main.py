import pandas as pd
import requests
from tqdm import tqdm
import warnings
import folium
from folium.plugins import HeatMap
import tkinter as tk
from tkinter import messagebox, ttk, PhotoImage
from threading import Thread
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

warnings.filterwarnings("ignore")  # Ignore pandas warnings for a cleaner user experience


def data(u):
    # cut out some columns from the data that won't be useful to us
    if u.lower() == 'y':
        update()  # calls update function for latest file

    df = pd.read_csv("Crime.csv")
    df = df[
        ['Incident ID', 'Start_Date_Time', 'End_Date_Time', 'Victims', 'Crime Name2', 'Crime Name3', 'City', 'State',
         'Zip Code', 'Street Name', 'Location']]
    df['Start_Date_Time'] = pd.to_datetime(df['Start_Date_Time'], format='%m/%d/%Y %I:%M:%S %p')
    df['End_Date_Time'] = pd.to_datetime(df['End_Date_Time'], format='%m/%d/%Y %I:%M:%S %p')
    df = df.sort_values('Start_Date_Time', ascending=False)
    return df


def update():
    response = requests.get("https://data.montgomerycountymd.gov/api/views/icn6-v9z3/rows.csv?accessType=DOWNLOAD",
                            stream=True)
    response.raise_for_status()
    # attempting to download file and show error if it doesn't work

    total_size_in_bytes = int(response.headers.get('content-length', 0))
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    # makes progress bar for write process
    print("Downloaded Crime.csv")
    with open('Crime.csv', 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            progress_bar.update(len(chunk))
            f.write(chunk)

    progress_bar.close()


def start_app():
    def load_data(u):
        # Simulating data loading process
        df = data(u)
        return df

    def on_submit():
        u = update_db.get()
        show_heatmap_option = show_heatmap.get().lower() == 'y'
        crime_types = crime_type_entry.get().strip().lower().split(',')
        num_points = int(num_crimes_entry.get()) + 1
        address = address_entry.get().strip()
        range_miles = float(range_entry.get().strip())

        def update_data_progress():
            # Simulate loading data with a secondary thread and updating the progress bar
            progress_bar_data["value"] = 0
            status_label_data.config(text="Loading data...")
            df = load_data(u)
            progress_bar_data["value"] = 100
            status_label_data.config(text="Data loaded!")
            root.update_idletasks()

            # Proceed with map generation
            generate_map(df, show_heatmap_option, crime_types, num_points, address, range_miles)

        # Start the data loading process in a separate thread
        Thread(target=update_data_progress).start()

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

        def format_crime_data(s):
            parts = s.split()
            lat = float(parts[parts.index('Location') + 1][1:len(parts[parts.index('Location') + 1]) - 1])
            long = float(parts[parts.index('Location') + 2][0:len(parts[parts.index('Location') + 2]) - 1])

            d = {
                'Incident ID': parts[parts.index('ID') + 1],
                'Date': parts[parts.index('Start_Date_Time') + 1],
                'Time': parts[parts.index('Start_Date_Time') + 2],
                'Victim #': parts[parts.index('Victims') + 1],
                'Category': ' '.join(parts[parts.index('Name2') + 1: parts.index('Name3') - 1]),
                'Crime': ' '.join(parts[parts.index('Name3') + 1: parts.index('City')]),
                'City': parts[parts.index('City') + 1],
                'Street View': f'<a href="https://www.google.com/maps?q=&layer=c&cbll={lat},{long}" target="_blank">View Street</a>'
            }

            formatted_string = ""
            for key, value in d.items():
                formatted_string += f"<strong>{key}</strong>: {value}<br>"

            return formatted_string

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

        if len(lats) == 0 or len(longs) == 0:
            messagebox.showwarning("No Data", "No crimes match the selected criteria.")
            return

        # Use geopy to geocode the address into lat, long
        geolocator = Nominatim(user_agent="crime_mapper")
        location = geolocator.geocode(address)
        if location:
            center_lat, center_long = location.latitude, location.longitude
        else:
            # If the address is invalid, default to the average lat/long of the crimes
            center_lat, center_long = sum(lats) / len(lats), sum(longs) / len(longs)
            messagebox.showerror("Invalid Address", "Address not found. Centering on average crime location.")

        # Filter crimes based on the range from the provided address
        filtered_lats = []
        filtered_longs = []
        for lat, long in zip(lats, longs):
            if geodesic((center_lat, center_long), (lat, long)).miles <= range_miles:
                filtered_lats.append(lat)
                filtered_longs.append(long)

        if len(filtered_lats) == 0 or len(filtered_longs) == 0:
            messagebox.showwarning("No Data", "No crimes found within the specified range.")
            return

        # Create the base map centered on the address if valid, or the average of crime locations if not
        base_map = folium.Map(tiles='OpenStreetMap', location=(center_lat, center_long),
                              zoom_start=17, prefer_canvas=True)

        progress_bar_map["value"] = 0
        status_label_map.config(text="Generating map...")

        # Add the heatmap layer if opted in
        if show_heatmap_option:
            heat_data = [[lat, long] for lat, long in zip(filtered_lats, filtered_longs)]
            HeatMap(heat_data).add_to(base_map)

        # Add markers for individual crimes
        for i, (lat, long) in enumerate(zip(filtered_lats[0:num_points], filtered_longs[0:num_points])):
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

            # Update progress bar during map generation
            progress = (i + 1) / num_points * 100
            progress_bar_map["value"] = progress
            root.update_idletasks()

        # Save and display the map
        base_map.save("basemap.html")
        os.system("open basemap.html")
        status_label_map.config(text="Map generated!")
        root.quit()

    # Initialize the main Tkinter window
    root = tk.Tk()
    root.title("NeighborhoodWatch Configuration")
    root.geometry("500x400")
    root.resizable(False, False)

    # Create and place the GUI elements
    tk.Label(root, text="Update Database [y/n]:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    update_db = tk.Entry(root)
    update_db.grid(row=0, column=1, padx=10, pady=5)
    update_db.insert(0, "n")

    tk.Label(root, text="Show Heatmap [y/n]:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    show_heatmap = tk.Entry(root)
    show_heatmap.grid(row=1, column=1, padx=10, pady=5)
    show_heatmap.insert(0, "y")

    tk.Label(root, text="Crime Types to Filter (comma-separated):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    crime_type_entry = tk.Entry(root)
    crime_type_entry.grid(row=2, column=1, padx=10, pady=5)
    crime_type_entry.insert(0, "")

    tk.Label(root, text="Number of Crimes to Show:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    num_crimes_entry = tk.Entry(root)
    num_crimes_entry.grid(row=3, column=1, padx=10, pady=5)
    num_crimes_entry.insert(0, "100")

    tk.Label(root, text="Center Address:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    address_entry = tk.Entry(root)
    address_entry.grid(row=4, column=1, padx=10, pady=5)
    address_entry.insert(0, "")

    tk.Label(root, text="Range in Miles:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    range_entry = tk.Entry(root)
    range_entry.grid(row=5, column=1, padx=10, pady=5)
    range_entry.insert(0, "5")  # Default to 5 miles

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Progress bars for data loading and map generation
    progress_bar_data = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=280)
    progress_bar_data.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

    status_label_data = tk.Label(root, text="")
    status_label_data.grid(row=8, column=0, columnspan=2)

    progress_bar_map = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=280)
    progress_bar_map.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

    status_label_map = tk.Label(root, text="")
    status_label_map.grid(row=10, column=0, columnspan=2)

    # icon photo
    icon = PhotoImage(file="icon.png")
    root.iconphoto(False, icon)

    # Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    start_app()
