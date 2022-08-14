from multiprocessing.dummy import Array
import os
import datetime
import numpy as np
import pandas as pd

from dataset.tsf_loader import convert_tsf_to_dataframe
from dataset.schedule_data_model import Schedule_Model

class IEEE_CIS:
  def __init__(self) -> None:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    self.PHASE1_TIME = datetime.datetime(day=1, month=10, year=2020, hour=0, minute=0, second=0)
    self.PHASE2_TIME = datetime.datetime(day=1, month=11, year=2020, hour=0, minute=0, second=0)
    self.energy_data_path = os.path.join(_BASE_DIR, "energy/nov_data.tsf")
    self.weather_data_path = os.path.join(_BASE_DIR, "weather/ERA5_Weather_Data_Monash.csv")
    self.nov_price_data_path = os.path.join(_BASE_DIR, "price/PRICE_AND_DEMAND_202011_VIC1.csv")
    self.base_dir = _BASE_DIR


  def helper_schedule_data_paths(self, phase_num: int) -> list[str]:
    """
    # helper_schedule_data_paths 
    ### Creates all file paths for phase phase_num.

    @param phase_num: The phase number
    @complexity: Worst-Best-Case: O(c), where c represents some constant
    @return: [path_large_0, path_small_0,path_large_1, path_small_1,...] 
      Where, path_large are the paths with large in their name, 
        path_small are the paths with small in their name
    """
    arr = []
    for j in range(5):
      # Create file names for large and small instances
      fileNameLarge = "phase" + str(phase_num) + "_instance_large_" + str(j) + ".txt"
      fileNameSmall = "phase" + str(phase_num) + "_instance_small_" + str(j) + ".txt"
      # Join file name to the os path base_dir
      schedule_data_path_large = os.path.join(self.base_dir, "schedule/" + fileNameLarge)
      schedule_data_path_small = os.path.join(self.base_dir, "schedule/" + fileNameSmall)
      # Append array to arr
      arr += [schedule_data_path_large, schedule_data_path_small]
    return arr

  def helper_schedule_reader(self, phase_num: int, f_path: str) -> Schedule_Model:
    """
    # helper_schedule_reader
    ### Lines are read from file path and are placed into object named Schedule_Model based on identifier at the beginning of each line.

    @param phase_num: The phase number
    @param f_path: The txt file path
    @complexity: Worst-Best-Case: O(k), where k represents the amount of lines in file f_path
    @return: schedule_model object
    """
    lines = []
    # Read lines of f_path
    with open(f_path) as f:
      lines = f.read().splitlines()

    # List identifiers
    identifiers = ['ppoi', 'b', 's', 'c', 'r', 'a']
    # Init schedule model
    schedule_m = Schedule_Model(phase_num, f_path)
    # For each line check identifier and put data into model
    for line in lines:
      splitLine = line.split(' ')
      identifier = splitLine[0]
      # ppoi
      if identifiers[0] == identifier:
        # ppoi # buildings # solar # battery # recurring # once-off
        schedule_m.add_ppoi(splitLine)
      # b
      elif identifiers[1] == identifier:
        # b # building id # small # large
        schedule_m.add_building(splitLine)
      # s
      elif identifiers[2] == identifier:
        # s # solar id # building id
        schedule_m.add_solar(splitLine)
      # c
      elif identifiers[3] == identifier:
        # c # battery id # building id # capacity kWh # max power kW # efficiency
        schedule_m.add_battery(splitLine)
      # r
      elif identifiers[4] == identifier:
        # r # activity # precedences
        schedule_m.add_act(splitLine)
      # a
      elif identifiers[5] == identifier:
        # a # activity # $value # $penalty # precedences
        schedule_m.add_once_off_act(splitLine)
    return schedule_m

  def load_schedule_data(self, schedule_data_paths_P1: list, schedule_data_paths_P2: list) -> list[list[Schedule_Model]]:
    """
    # load_schedule_data 
    ### Calls self.helper_schedule_reader for each path in input lists.

    @param schedule_data_paths_P1: The schedule data paths for Phase 1
    @param schedule_data_paths_P2: The schedule data paths for Phase 2
    @complexity: Worst-Best-Case: O(N), where N represents the len(schedule_data_paths_P1)+len(schedule_data_paths_P2)
    @return: lst = [[schedule_model object],[schedule_model object]]
      Where, lst[0] is Phase 1, lst[1] is Phase 2
    """
    arr1 = []
    arr2 = []
    # Phase 1
    for path in schedule_data_paths_P1:
      # Call helper schedule reader and append to array
      arr1.append(self.helper_schedule_reader(1, path))
    # Phase 2
    for path in schedule_data_paths_P2:
      # Call helper schedule reader and append to array
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

