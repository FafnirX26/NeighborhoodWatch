# This file exists to update & read the csv file and communicate data with the main file
import pandas as pd
import requests
from tqdm import tqdm


def data(u):
    # cut out some columns from the data that won't be useful to us
    if u.lower() == 'y':
        update()  # calls update function for latest file

    df = pd.read_csv("Crime.csv")
    df = df[['Incident ID', 'Start_Date_Time', 'End_Date_Time', 'Victims', 'Crime Name1', 'City', 'State', 'Zip Code',
             'Street Name', 'Location']]
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
