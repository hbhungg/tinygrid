from multiprocessing.dummy import Array
import os
import datetime
import numpy as np
import pandas as pd

from .tsf_loader import convert_tsf_to_dataframe
from ._schedule_loader import Schedule, schedule_parser

class IEEE_CISMixin:
  """
  This is a mixin class, design to
  """
  _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

  WEATHER_DATA_PATH = os.path.join(_BASE_DIR, "weather/ERA5_Weather_Data_Monash.csv")
  NOV_PRICE_DATA_PATH = os.path.join(_BASE_DIR, "price/PRICE_AND_DEMAND_202011_VIC1.csv")
  ENERGY_DATA_PATH = os.path.join(_BASE_DIR, "energy/nov_data.tsf")
  SCHEDULE_DATA_PATH = os.path.join(_BASE_DIR, "schedule/")

  PHASE1_TIME = datetime.datetime(day=30, month=9, year=2020, hour=23, minute=59, second=59)
  PHASE2_TIME = datetime.datetime(day=31, month=10, year=2020, hour=23, minute=59, second=59)


  @classmethod
  def _load_schedule_data(cls) -> dict[str, Schedule]:
    """
    Load and parse all of the schedule .txt files from IEEE-CIS's competition
    """
    schedule_data = {}
    # Get all of the files inside schedule/ folder.
    schedule_fnames = os.listdir(cls.SCHEDULE_DATA_PATH)
    for name in schedule_fnames:
      full_path = os.path.join(cls.SCHEDULE_DATA_PATH, name)
      schedule_data[name] = schedule_parser(full_path)
    return schedule_data

  
  @classmethod
  def _load_energy_data(cls) -> dict[str, pd.DataFrame]:
    """
    Transform the atrocious format from "convert_tsf_to_dataframe" function to a sane format.
    Each series name will now be a entry of a dict, and all values is now a DataFrame with dates as the index column.
    Also, remove all string NaN and replace it as actual np.nan value
    """
    tsf_file = convert_tsf_to_dataframe(cls.ENERGY_DATA_PATH)[0]
    energy_data = dict()

    for name, value, stime in zip(tsf_file["series_name"], tsf_file["series_value"], tsf_file["start_timestamp"]):
      # Turn string "NaN" into actual np.nan value
      value[value == "NaN"] = np.nan
      value = value.to_numpy().astype("float64")
      # Frequency is 15 minutes
      time_column = [stime + datetime.timedelta(minutes=15*i) for i in range(len(value))]
      energy_data[name] = pd.DataFrame({'datetime': time_column, 'energy': value}).set_index('datetime')
    return energy_data


  @classmethod
  def _load_ERA5_weather_data(cls) -> pd.DataFrame:
    """
    Load ERA5 weather data from csv to pandas DataFrame. Transform the datetime string to appropriate type.
    Set the dataframe index to the datetime column.
    """
    weather_data = pd.read_csv(cls.WEATHER_DATA_PATH)
    # Parse the time from string to 
    weather_data['datetime (UTC)'] = pd.to_datetime(weather_data['datetime (UTC)'], format="%Y-%m-%d %H:%M:%S")
    weather_data = weather_data.set_index('datetime (UTC)')
    return weather_data

  @classmethod
  def _load_AEMO_nov_price_data(cls) -> pd.DataFrame:
    """
    Load AEMO price data from csv to pandas DataFrame. Transform the datetime string to appropriate type.
    Set the dataframe index to the datetime column.
    """
    price_data = pd.read_csv(cls.NOV_PRICE_DATA_PATH)
    # Parse the time from string to 
    price_data['SETTLEMENTDATE'] = pd.to_datetime(price_data['SETTLEMENTDATE'], format="%Y-%m-%d %H:%M:%S")
    price_data = price_data.set_index('SETTLEMENTDATE')
    return price_data
  