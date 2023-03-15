import os
import pandas as pd
import datetime
import folium
from folium.plugins import HeatMapWithTime
from tkinter import Tk, Label, Button, filedialog, Toplevel, StringVar, Radiobutton


def get_coordinate_format():
    def select_latlong_format():
        nonlocal selected_format
        selected_format = "latlong"
        root.destroy()

    def select_mgrs_format():
        nonlocal selected_format
        selected_format = "mgrs"
        root.destroy()

    def on_closing():
        nonlocal selected_format
        selected_format = "terminated"
        root.destroy()

    root = Tk()
    root.title("Select Coordinate Format")
    root.geometry("300x200")

    Label(root, text="Choose the coordinate format:", pady=20).pack()

    selected_format = None

    Button(root, text="Lat/Long", command=select_latlong_format, width=20).pack(pady=10)
    Button(root, text="MGRS", command=select_mgrs_format, width=20).pack(pady=10)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

    return selected_format


def load_and_process_data(csv_path, latlong_format):
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y').dt.strftime('%Y-%m-%d')

    if not latlong_format:
        from mgrs import MGRS
        m = MGRS()
        df[['lat', 'lon']] = pd.DataFrame(df.apply(lambda row: m.toLatLon(row['MGRS']), axis=1).tolist())
        df = df.drop(columns=['MGRS'])

    return df


def create_and_save_heatmap(df):
    now = datetime.datetime.now()
    output_filename = "Heatmap_{}_{}_{}_{}_{}_{}.html".format(now.year, now.month, now.day, now.hour, now.minute, now.second)

    heatmap_map = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=5)

    grouped_df = df[['lat', 'lon', 'date']].groupby(['date', 'lat', 'lon']).size().reset_index(name='count')
    unique_dates = grouped_df['date'].unique()
    heatmap_data = []

    cumulative_data = []
    for date in unique_dates:
        daily_data = grouped_df[grouped_df['date'] == date]
        daily_data_list = daily_data[['lat', 'lon', 'count']].values.tolist()
        cumulative_data.extend(daily_data_list)
        heatmap_data.append(cumulative_data.copy())

    index_to_date = {i: date for i, date in enumerate(unique_dates)}

    HeatMapWithTime(data=heatmap_data, index=index_to_date, radius=8, auto_play=True, max_opacity=0.7, gradient=None).add_to(heatmap_map)

    desktop_path = os.path.join(os.path.join(os.environ['HOME']), 'Desktop')
    output_path = os.path.join(desktop_path, output_filename)
    heatmap_map.save(output_path)

    print("\033[1m\033[1;32mHeatmap saved to {}\033[0m".format(output_path))


if __name__ == "__main__":
    latlong_format = get_coordinate_format()

    if latlong_format == "terminated":
        print("\033[1m\033[1;31mProcess Terminated By User\033[0m")
    else:
        root = Tk()
        root.withdraw()
        csv_path = filedialog.askopenfilename(filetypes=[        ("CSV Files", "*.csv")])

        if not csv_path:
            print("\033[1m\033[1;31mProcess Terminated By User\033[0m")
        else:
            latlong_format = True if latlong_format == "latlong" else False
            df = load_and_process_data(csv_path, latlong_format)
            create_and_save_heatmap(df)


