# NeighborhoodWatch for Montgomery County  
An interactive web app built using Flask and Folium to visualize crime incidents in Montgomery County, Maryland. This project aims to provide residents, law enforcement, and policymakers with an easy-to-use tool to explore and analyze crime data trends across the region.

---

## Table of Contents  
- [Features](#features)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Technologies Used](#technologies-used)  
- [Data Source](#data-source)  
- [Future Improvements](#future-improvements)  
- [License](#license)  

---

## Features  
- **Interactive Crime Map**: Displays crime data on a Folium map with clickable markers showing details for each incident.  
- **Heatmap Layer**: Visualizes crime density in different areas using a heatmap.  
- **Crime Filtering**: Users can filter crimes by type (e.g., robbery, burglary) to focus on specific incidents.  
- **Street View Integration**: Explore street-level perspectives of crime locations using Google Street View.  
- **Responsive UI**: Works seamlessly on desktops, and planned improvements will enhance mobile access.  

---

## Installation  
1. **[Install Python if you haven't already](https://www.python.org/downloads/)**
   
2. **Clone the repository:**  
   ```bash
   git clone https://github.com/FafnirX26/NeighborhoodWatch.git
   cd NeighborhoodWatch
   ```  

3. **Create a virtual environment (optional but recommended):**  
   ```bash
   python3 -m venv venv  
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install the dependencies:**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```
   
5. **Run the app:**  
   ```bash
   python main.py
   ```  
   The app will be available at `http://127.0.0.1:5000`.  

---

## Usage  
1. Open your web browser and go to `http://127.0.0.1:5000`.  
2. Explore crime data by zooming, panning, or clicking on individual markers.  
3. Use the **crime type filter** to focus on specific categories of crime.  
4. Enable the **heatmap layer** to see areas with higher crime density.  
5. Click on a marker to view additional information (e.g., date, type of crime).  
6. Use **Street View** for a closer look at specific crime locations.  

---

## Technologies Used  
- **Python**: Backend logic and data processing.  
- **Flask**: Lightweight web framework for backend development.  
- **Folium**: Library for creating interactive maps.  
- **pandas**: Data manipulation and filtering.  
- **Google Maps API**: Integrating Street View functionality.
- **geopy**: Distance calculation from a point on a map.

---

## Data Source  
The crime data is sourced from [Montgomery County's Open Data Portal](https://data.montgomerycountymd.gov/) and contains details about recent crime incidents, including dates, types, and locations. The data is periodically updated to ensure relevance.

---

## Future Improvements  
- **Real-Time Data Integration**: Directly pull updated crime data from public safety APIs.  
- **Predictive Analytics**: Use machine learning models to forecast crime hotspots.  
- **Mobile-Friendly Design**: Optimize the UI for smaller screens.  
- **Community Reporting**: Allow users to submit safety concerns or tips.  
- **Geofencing Alerts**: Notify users when specific crimes occur near their home or workplace.  

---

## License  
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details. 

---
