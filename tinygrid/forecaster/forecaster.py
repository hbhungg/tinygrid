import os
from datetime import datetime, timedelta

from tqdm import tqdm
import pandas as pd
import numpy as np
import sklearn.ensemble

from ..dataset import IEEE_CISMixin
from ..utils import Const, mase

# Flags
# How to invoke: DEBUG=1 python3 script.py
DEBUG = int(os.getenv('DEBUG', 0))

def generate_building_data(data: pd.DataFrame,
                           upper: int=None,
                           lower: int=None,
                           start: datetime=None,
                           end: datetime=None,
                           cutoff_date: datetime=None):
  """
  Generate building data for forecasting. 
  Params:
    data: energy data for buildings
    start: start time, if data is None, will use this to generate x data for prediction, else this will be ignore
    end: end time, if data is None, will use this to generate x data for prediction, else this will be ignore
    upper: omit data higher, if data is None, this will be ignore.
    lower: omit data lower, if daat is None, this will be ignore.
    cutoff_date: date to cut off, if data is None, this will be ignore.
  """
  HOUR = 24*60
  DAY = 24*60*60

  # Transform raw seconds into sin and cos value
  # Creating values that represent the repeat of hour and day
  if data is None:
    idx = pd.date_range(start, end-timedelta(seconds=1), freq="15min")
    data = pd.DataFrame(index=idx)
  else:
    data = data.copy()
    data = data[cutoff_date:]

  time_stamp = data.index.tz_convert("Australia/Melbourne").map(pd.Timestamp.timestamp)
  data['hour_sin'] = np.cos(time_stamp * (2 * np.pi/HOUR))
  data['hour_cos'] = np.cos(time_stamp * (2 * np.pi/HOUR))
  data['day_sin'] = np.sin(time_stamp * (2 * np.pi/DAY))
  data['day_cos'] = np.cos(time_stamp * (2 * np.pi/DAY))

  # Monday-Friday 1, else 0
  data['weekday'] = data.index.weekday < 5
  data['weekday1'] = (data.index.weekday < 4) & (data.index.weekday > 0)
  # Boolean mask for weekdays
  for i in range(7):
    data[f"wdx{i}"] = data.index.weekday == i

  # This section model the covid restriction for occupancy from June to October 2020.
  # Full capacity at before 20th June
  data["restriction"] = ((data.index < Const.S1) == True) * 1
  # 10% occupancy 20th June - 2nd Aug
  data["restriction"] += ((data.index > Const.S1) & (data.index < Const.S2) == True) * 0.1
  # 5% occupancy 2nd Aug - 13th Sept
  data["restriction"] += ((data.index > Const.S2) & (data.index < Const.S3) == True) * 0.05
  # 25% occupancy 13th Sept - 18th Oct
  data["restriction"] += ((data.index > Const.S3) & (data.index < Const.S4) == True) * 0.25
  # 30% occupancy 13th Sept - 18th Oct
  data["restriction"] += ((data.index > Const.S4) == True) * 0.3
  data = data.dropna()

  if 'energy' in data:
    if upper is None and lower is not None:
      data = data[data['energy']>=lower] 
    elif upper is not None and lower is None:
      data = data[data['energy']<=upper] 
    elif upper is not None and lower is not None:
      data = data[(data['energy']>=lower) & (data['energy']<=upper)]
    return data.drop("energy", axis=1).to_numpy(), data['energy'].to_numpy()
  else:
    return data.to_numpy()


def generate_solar_data(data: pd.DataFrame,
                        weather_data: pd.DataFrame,
                        start: datetime=None,
                        end: datetime=None,
                        cutoff_date: datetime=None,
                        cache: bool=False):
  """
  Transform the solar data using the ERA5 weather data.
  """
  weather_data = weather_data.drop(
             ['coordinates (lat,lon)', 
              'model (name)',
              'utc_offset (hrs)', 
              'model elevation (surface)',
              "mean_sea_level_pressure (Pa)",
              "wind_speed (m/s)",
              "relative_humidity ((0-1))"], 
             axis=1).resample('15min').asfreq()

  for col in list(weather_data.columns):
    for lag in range(1, 4):
      # Forward lag all columns 
      weather_data[f"{col}_lag_{lag}"] = weather_data[col].shift(lag)
      # Backward lag all columns
      weather_data[f"{col}_lag_{-lag}"] = weather_data[col].shift(-lag)
  weather_data = weather_data.interpolate()

  if data is not None:
    data = data[cutoff_date:]
    data = data.join(weather_data).dropna()
    return data.drop("energy", axis=1).to_numpy(), data['energy'].to_numpy()
  else:
    return weather_data[start:end-timedelta(seconds=1)].to_numpy()


class Forecaster:
  """
  A wrapper around sklearn.ensemble.RandomForestRegressor
  """
  CACHE_FOLDER = "./cache/"
  CHECKPOINTS  = "./checkpoints/"

  def __init__(self, verbose: int=0):
    self.verbose = verbose
    self.model = sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1)

  def fit(self, x, y):
    self.model.fit(x, y)

  def predict(self, x):
    return self.model.predict(x)

