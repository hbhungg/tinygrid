import os
import datetime
import numpy as np
import pandas as pd

from dataset.tsf_loader import convert_tsf_to_dataframe


class IEEE_CIS:
  def __init__(self):
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    self.PHASE1_TIME = datetime.datetime(day=1, month=10, year=2020, hour=0, minute=0, second=0)
    self.PHASE2_TIME = datetime.datetime(day=1, month=11, year=2020, hour=0, minute=0, second=0)
    self.energy_data_path = os.path.join(_BASE_DIR, "energy/nov_data.tsf")
    self.weather_data_path = os.path.join(_BASE_DIR, "weather/ERA5_Weather_Data_Monash.csv")


  def load_energy_data(self) -> dict[str, pd.DataFrame]:
    """
    Transform the atrocious format from "convert_tsf_to_dataframe" function to a sane format.
    Each series name will now be a entry of a dict, and all values is now a DataFrame with dates as the index column.
    Also, remove all string NaN and replace it as actual np.nan value

    Return:
      dict[str, pd.DataFrame]
    """
    tsf_file = convert_tsf_to_dataframe(self.energy_data_path)[0]

    data = dict()
    for name, value, stime in zip(tsf_file["series_name"], tsf_file["series_value"], tsf_file["start_timestamp"]):
      # Turn string "NaN" into actual np.nan value
      value[value == "NaN"] = np.nan
      value = value.to_numpy().astype("float64")
      # Frequency is 15 minutes
      time_column = [stime + datetime.timedelta(minutes=15*i) for i in range(len(value))]
      data[name] = pd.DataFrame({'datetime': time_column, 'energy': value}).set_index('datetime')
    return data


  def load_ERA5_weather_data(self) -> pd.DataFrame:
    """
    Load ERA5 weather data from csv to pandas DataFrame. Transform the datetime string to appropriate type.
    Set the dataframe index to the datetime column.

    Return:
      DataFrame object
    """
    weather_data = pd.read_csv(self.weather_data_path)
    # Parse the time from string to 
    weather_data['datetime (UTC)'] = pd.to_datetime(weather_data['datetime (UTC)'], format="%Y-%m-%d %H:%M:%S")
    weather_data = weather_data.set_index('datetime (UTC)')
    return weather_data

