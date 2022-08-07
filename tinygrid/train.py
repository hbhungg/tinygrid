#!/usr/bin/env python3
import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np

from dataset import IEEE_CIS
from net import LSTM2

# Ensure reproducibility
random_seed = 1
torch.manual_seed(random_seed)

class IEEE_CIS_Torch(Dataset):
  def __init__(self, df, win_length):
    self.df = df
    self.win_length = win_length

  def __len__(self):
    return len(self.df)-self.win_length-1

  def __getitem__(self, idx):
    x = np.array(self.df[idx:idx+self.win_length])
    y = self.df.iloc[idx+self.win_length+1]['energy']
    return x, y

if __name__ == "__main__":
  dm = IEEE_CIS()

  energy = dm.load_energy_data()['Solar0']
  weather = dm.load_ERA5_weather_data()

  comb = energy.join(weather)
  comb = comb.drop(['coordinates (lat,lon)', 'model (name)', 'utc_offset (hrs)', 'model elevation (surface)'], axis=1)
  comb = comb.fillna(method="ffill")

  day = 24*60*60
  year = (365.2425)*day
  time_stamp = comb.index.map(pd.Timestamp.timestamp)
  # Transform raw seconds into sin and cos value, creating a seasonal value that represent the repeat of day and year
  comb['day_sin'] = np.sin(time_stamp * (2 * np.pi/day))
  comb['day_cos'] = np.cos(time_stamp * (2 * np.pi/day))
  comb['year_sin'] = np.sin(time_stamp * (2 * np.pi/year))
  comb['year_cos'] = np.cos(time_stamp * (2 * np.pi/year))

  ds = IEEE_CIS_Torch(comb, 28)
  dl = DataLoader(ds, batch_size=128)

  torch.set_default_dtype(torch.float64)
  net = LSTM2(1, 13, 512, 4)

  for x, y in dl:
    print(x.dtype)
    print(net(x))
    break
    
