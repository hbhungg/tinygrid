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
    y = np.array([self.df.iloc[idx+self.win_length+1]['energy']])
    return x, y


def train(model, epochs, train_loader, val_loader, opt, loss_f, log_interval):
  for epoch in range(1, epochs+1):
    _train(model, epoch, train_loader, opt, loss_f, log_interval)
    _validation(model, test_loader, loss_f)

def _train(model, epoch, train_loader, opt, loss_f, log_interval):
  for batch_idx, (data, target) in enumerate(train_loader):
    optimizer.zero_grad()
    output = model(data)
    loss = loss_f(output, target)
    loss.backward()
    optimizer.step()
    if batch_idx % log_interval == 0:
      print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
        epoch, batch_idx * len(data), len(train_loader.dataset),
        100. * batch_idx / len(train_loader), loss.item()))
      torch.save(model.state_dict(), './checkpoints/model.pth')

def _validation(model, test_loader, loss_f):
  test_loss = 0
  with torch.no_grad():
    for data, target in test_loader:
      output = model(data)
      test_loss += loss_f(output, target, size_average=False).item()
    test_loss /= len(test_loader.dataset)
  print('\nTest set: Avg. loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
      test_loss, correct, len(test_loader.dataset),
      100. * correct / len(test_loader.dataset)))

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
  optimizer = torch.optim.Adam(net.parameters(), lr=0.0001)
  loss_f = torch.nn.L1Loss()


  train(net, 1, dl, [], optimizer, loss_f, 10)
