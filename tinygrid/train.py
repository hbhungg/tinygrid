#!/usr/bin/env python3
import torch

from tinygrid.net import LSTM2
from tinygrid.dataloader import SlidingDataset, load_data_helper
from torch.utils.data import Dataset, DataLoader


def train(model, epochs, train_loader, val_loader, opt, loss_f, log_interval) -> None:
  """
  Training loop
  Params:
    model: Torch model
    epochs: how many time to train
    train_loader: Torch DataLoader
    val_loader: Torch DataLoader
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
  # Ensure reproducibility
  random_seed = 1
  torch.manual_seed(random_seed)

  # Properly clean and prepare data
  comb_train, comb_test = load_data_helper()

  # Make into PyTorch iterable sliding window dataset
  ds_train = SlidingDataset(comb_train, 28)
  ds_test = SlidingDataset(comb_test, 28)

  BATCH_SIZE = 128 
  # Make into dataloader, train have random
  dl_train = DataLoader(ds_train, batch_size=BATCH_SIZE, shuffle=True)
  dl_test = DataLoader(ds_test, batch_size=BATCH_SIZE, shuffle=False)

  LEARNING_RATE = 0.0001
  # IDK is this good?
  # TODO: find out if im shooting myself with this
  torch.set_default_dtype(torch.float64)

  net = LSTM2(1, 13, 512, 4)
  optimizer = torch.optim.Adam(net.parameters(), lr=LEARNING_RATE)
  loss_f = torch.nn.L1Loss()

  train(net, 3, dl_train, dl_test, optimizer, loss_f, 10)
