from multiprocessing.dummy import Array
import os
import datetime
import numpy as np
import pandas as pd

from dataset.tsf_loader import convert_tsf_to_dataframe
from dataset.schedual_data_model import Schedual_Model

class IEEE_CIS:
  def __init__(self) -> None:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    self.PHASE1_TIME = datetime.datetime(day=1, month=10, year=2020, hour=0, minute=0, second=0)
    self.PHASE2_TIME = datetime.datetime(day=1, month=11, year=2020, hour=0, minute=0, second=0)
    self.energy_data_path = os.path.join(_BASE_DIR, "energy/nov_data.tsf")
    self.weather_data_path = os.path.join(_BASE_DIR, "weather/ERA5_Weather_Data_Monash.csv")
    self.nov_price_data_path = os.path.join(_BASE_DIR, "price/PRICE_AND_DEMAND_202011_VIC1.csv")
    self.base_dir = _BASE_DIR


  def helper_schedule_data_paths(self, phase_num, _BASE_DIR):
    """
    Takes phase_num and _BASE_DIR, creates all file paths for phase phase_num.
    Return:
      arr
    """
    arr = []
    for j in range(5):
      fileNameLarge = "phase" + str(phase_num) + "_instance_large_" + str(j) + ".txt"
      fileNameSmall = "phase" + str(phase_num) + "_instance_small_" + str(j) + ".txt"
      schedule_data_path_Large = os.path.join(_BASE_DIR, "schedule/" + fileNameLarge)
      schedule_data_path_Small = os.path.join(_BASE_DIR, "schedule/" + fileNameSmall)
      arr += [schedule_data_path_Large, schedule_data_path_Small]
    return arr

  def helper_schedule_reader(self, phase_num, path):
    """
    Takes path and phase_num, puts it into data model.
    Return:
      schedual_model object
    """
    lines = []
    with open(path) as f:
      lines = f.read().splitlines()

    identifiers = ['ppoi', 'b', 's', 'c', 'r', 'a']
    schedual_m = Schedual_Model(phase_num, path)
    for line in lines:
      splitLine = line.split(' ')
      identifier = splitLine[0]
      # ppoi
      if identifiers[0] == identifier:
        # ppoi # buildings # solar # battery # recurring # once-off
        schedual_m.add_ppoi(splitLine)
      # b
      elif identifiers[1] == identifier:
        # b # building id # small # large
        schedual_m.add_building(splitLine)
      # s
      elif identifiers[2] == identifier:
        # s # solar id # building id
        schedual_m.add_solar(splitLine)
      # c
      elif identifiers[3] == identifier:
        # c # battery id # building id # capacity kWh # max power kW # efficiency
        schedual_m.add_battery(splitLine)
      # r
      elif identifiers[4] == identifier:
        # r # activity # precedences
        schedual_m.add_act(splitLine)
      # a
      elif identifiers[5] == identifier:
        # a # activity # $value # $penalty # precedences
        schedual_m.add_once_off_act(splitLine)
    return schedual_m

  def load_schedule_data(self, schedule_data_paths_P1, schedule_data_paths_P2):
    arr1 = []
    arr2 = []
    # Phase 1
    for path in schedule_data_paths_P1:
      # helper schedule reader
      arr1.append(self.helper_schedule_reader(1, path))
    # Phase 2
    for path in schedule_data_paths_P2:
      # helper schedule reader
      arr2.append(self.helper_schedule_reader(2, path))
    return [arr1, arr2]

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

  def load_AEMO_nov_price_data(self) -> pd.DataFrame:
      """
      Load AEMO price data from csv to pandas DataFrame. Transform the datetime string to appropriate type.
      Set the dataframe index to the datetime column.

      Return:
        DataFrame object
      """
      price_data = pd.read_csv(self.nov_price_data_path)
      # Parse the time from string to 
      price_data['SETTLEMENTDATE'] = pd.to_datetime(price_data['SETTLEMENTDATE'], format="%Y-%m-%d %H:%M:%S")
      price_data = price_data.set_index('SETTLEMENTDATE')
      return price_data

