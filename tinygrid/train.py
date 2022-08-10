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


def train(model, epochs, train_loader, val_loader, opt, loss_f, log_interval) -> None:
  """
  Training loop
  Params:
    model: Torch model
    epochs: how many time to train
    train_loader:
    val_loader:
    opt: Torch optimizer
    loss_f: Torch loss function
    log_interval: interval to log data outside
  Return:
    None
  """
  for epoch in range(1, epochs+1):
    _train(model, epoch, train_loader, opt, loss_f, log_interval)
    validation(model, val_loader, loss_f)

def _train(model, epoch, train_loader, opt, loss_f, log_interval) -> None:
  """
  Internal training loop, handles all of the actual training logics
  Params: see train()
  Return: None
  """
  model.train()
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

def validation(model, test_loader, loss_f) -> None:
  """
  Validation loop. Similar to train but to back prop. Just forward and loss calc.
  Params: see train()
  Return: None
  """
  test_loss = 0
  model.eval()
  with torch.no_grad():
    for data, target in test_loader:
      output = model(data)
      test_loss += loss_f(output, target).item()
    test_loss /= len(test_loader)
  print('Test set: Avg. loss: {:.4f}'.format(test_loss))

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

  # Remove bunch of 0s
  comb = comb[2460:]

  # Norm col values to 0-1, except for the last 4 (day and year)
  for i in comb.iloc[:,:-4]:
    comb[i] = (comb[i]-comb[i].min())/(comb[i].max()-comb[i].min())

  # Split train and test (test is phase1 + phase2)
  comb_train = comb[:dm.PHASE1_TIME]
  comb_test = comb[dm.PHASE1_TIME:]

  # Make into PyTorch iterable sliding window dataset
  ds_train = IEEE_CIS_Torch(comb_train, 28)
  ds_test = IEEE_CIS_Torch(comb_test, 28)

  BATCH_SIZE = 128 

  # Make into dataloader, train have random
  dl_train = DataLoader(ds_train, batch_size=BATCH_SIZE, shuffle=True)
  dl_test = DataLoader(ds_test, batch_size=BATCH_SIZE, shuffle=False)

  # IDK is this good?
  # TODO: find out if im shooting myself with this
  torch.set_default_dtype(torch.float64)

  net = LSTM2(1, 13, 512, 4)
  optimizer = torch.optim.Adam(net.parameters(), lr=0.0001)
  loss_f = torch.nn.L1Loss()

  train(net, 3, dl_train, dl_test, optimizer, loss_f, 10)
