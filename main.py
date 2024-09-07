import data_manager
import folium
from folium.plugins import HeatMap
from tqdm import tqdm
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog


def start_app():
    def on_submit():
        u = update_db.get()
        show_heatmap_option = show_heatmap.get()
        crime_types = crime_type_entry.get().strip().lower().split(',')
        num_points = int(num_crimes_entry.get())

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

        # Create the base map
        base_map = folium.Map(tiles='OpenStreetMap', location=(sum(lats) / len(lats), sum(longs) / len(longs)),
                              zoom_start=12, prefer_canvas=True)

        # Add the heatmap layer if opted in
        if show_heatmap_option:
            heat_data = [[lat, long] for lat, long in zip(lats, longs)]
            HeatMap(heat_data).add_to(base_map)

        # Add markers for individual crimes
        for lat, long in tqdm(zip(lats[0:num_points], longs[0:num_points])):
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
        root.destroy()

    # Initialize the main Tkinter window
    root = tk.Tk()
    root.title("NeighborhoodWatch Configuration")

    # Create and place the GUI elements
    tk.Label(root, text="Update Database [Y/n]:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    update_db = tk.Entry(root)
    update_db.grid(row=0, column=1, padx=10, pady=5)
    update_db.insert(0, "Y")

    tk.Label(root, text="Show Heatmap [Y/n]:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    show_heatmap = tk.Entry(root)
    show_heatmap.grid(row=1, column=1, padx=10, pady=5)
    show_heatmap.insert(0, "Y")

    tk.Label(root, text="Crime Types to Filter (comma-separated):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    crime_type_entry = tk.Entry(root)
    crime_type_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(root, text="Number of Crimes to View:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    num_crimes_entry = tk.Entry(root)
    num_crimes_entry.grid(row=3, column=1, padx=10, pady=5)
    num_crimes_entry.insert(0, "100")

    submit_button = tk.Button(root, text="Generate Map", command=on_submit)
    submit_button.grid(row=4, column=0, columnspan=2, pady=20)

    # Run the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    start_app()
