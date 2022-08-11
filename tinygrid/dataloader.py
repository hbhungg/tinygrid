import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np

from dataset import IEEE_CIS


class SlidingDataset(Dataset):
  def __init__(self, df, win_length):
    self.df = df
    self.win_length = win_length

  def __len__(self):
    return len(self.df)-self.win_length-1

  def __getitem__(self, idx):
    x = np.array(self.df[idx:idx+self.win_length])
    y = np.array([self.df.iloc[idx+self.win_length+1]['energy']])
    return x, y


# Do we even need this?
# TODO: complete this
class SinglePointDataset(Dataset):
  def __init__(self, df, win_length):
    pass

  def __len__(self):
    pass

  def __getitem__(self, idx):
    pass


# TODO: make this to load all data
# TODO: is there a better name, I hate this name
def load_data_helper():
  """
  A helper function that prepare data
  """
  dm = IEEE_CIS()

  energy = dm.load_energy_data()['Solar0']
  weather = dm.load_ERA5_weather_data()

  # Join weather and energy data, date as shared col
  comb = energy.join(weather)
  comb = comb.drop(['coordinates (lat,lon)', 'model (name)', 'utc_offset (hrs)', 'model elevation (surface)'], axis=1)

  # Fill NaN values
  comb = comb.fillna(method="ffill")

  # Transform raw seconds into sin and cos value
  # Creating a seasonal value that represent the repeat of day and year
  DAY = 24*60*60
  YEAR = (365.2425)*DAY
  time_stamp = comb.index.map(pd.Timestamp.timestamp)
  comb['day_sin'] = np.sin(time_stamp * (2 * np.pi/DAY))
  comb['day_cos'] = np.cos(time_stamp * (2 * np.pi/DAY))
  comb['year_sin'] = np.sin(time_stamp * (2 * np.pi/YEAR))
  comb['year_cos'] = np.cos(time_stamp * (2 * np.pi/YEAR))

  # Remove bunch of 0s
  comb = comb[2460:]

  # Norm col values to 0-1, except for the last 4 (day and year)
  # Should there be a prettier way?
  comb.iloc[:,:-4] = (comb.iloc[:,:-4]-comb.iloc[:,:-4].min())/(comb.iloc[:,:-4].max()-comb.iloc[:,:-4].min())

  # Split train and test (test is phase1 + phase2)
  comb_train = comb[:dm.PHASE1_TIME]
  comb_test = comb[dm.PHASE1_TIME:]

  # Make into PyTorch iterable sliding window dataset
  ds_train = SlidingDataset(comb_train, 28)
  ds_test = SlidingDataset(comb_test, 28)

  BATCH_SIZE = 128 
  # Make into dataloader, train have random
  dl_train = DataLoader(ds_train, batch_size=BATCH_SIZE, shuffle=True)
  dl_test = DataLoader(ds_test, batch_size=BATCH_SIZE, shuffle=False)

  return dl_train, dl_test 

