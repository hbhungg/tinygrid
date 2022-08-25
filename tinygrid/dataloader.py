import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np


class SlidingDataset(Dataset):
  def __init__(self, df: pd.DataFrame, win_length: int, sliding_length: int, target: str):
    """
    A sliding dataset, return x input values of variable length and y target of variable length
    Params:
      df: pandas.DataFrame
      win_length: int x length
      sliding_length: int y length
      target: str name of the column that would be use as target
    """
    self.df = df
    self.win_length = win_length
    self.sliding_length = sliding_length
    self.length = len(self.df)-self.win_length-self.sliding_length
    self.target = target

  def __len__(self):
    return self.length

  def __getitem__(self, idx: int):
    mid = idx+self.win_length
    x = np.array(self.df[idx:mid])
    y = np.array([self.df.iloc[mid:mid+self.sliding_length][self.target]]).reshape(-1)
    return x, y


class DataCleaner:
  def __init__(self):
    """
    A helper class that prepare and clean data
    """
    from dataset import IEEE_CIS
    self.dm = IEEE_CIS()
    self.energy = self.dm.load_energy_data()
    self.weather = self.dm.load_ERA5_weather_data()
    # NOTE: is there a better way to fill the data?
    self.weather = self.weather.resample('15min').asfreq().fillna(method='bfill')

    # Names of all the columns
    self.cols = [i for i in self.energy]
  
  def load_data_helper(self, name):
    energy = self.energy[name]
    # Join weather and energy data, date as shared col
    comb = energy.join(self.weather)
    comb = comb.drop(['coordinates (lat,lon)', 
                      'model (name)',
                      'utc_offset (hrs)', 
                      'model elevation (surface)'], 
                     axis=1)

    # Normalize values to 0-1
    comb = (comb-comb.min())/(comb.max()-comb.min())

    # Transform raw seconds into sin and cos value
    # Creating a seasonal value that represent the repeat of day and year
    DAY = 24*60*60
    YEAR = (365.2425)*DAY
    time_stamp = comb.index.map(pd.Timestamp.timestamp)
    comb['day_sin'] = np.sin(time_stamp * (2 * np.pi/DAY))
    comb['day_cos'] = np.cos(time_stamp * (2 * np.pi/DAY))
    comb['year_sin'] = np.sin(time_stamp * (2 * np.pi/YEAR))
    comb['year_cos'] = np.cos(time_stamp * (2 * np.pi/YEAR))

    # TODO: Add a way to clean data

    # Split train and test (test is phase1 + phase2)
    comb_train = comb[:self.dm.PHASE1_TIME]
    comb_test = comb[self.dm.PHASE1_TIME:]

    return comb_train, comb_test

