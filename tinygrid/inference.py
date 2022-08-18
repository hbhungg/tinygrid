#!/usr/bin/env python3
import torch
from net import LSTM2
from dataloader import load_data_helper
import pandas as pd
from tqdm import tqdm


# TODO: complete this
def predict_sliding(model, test_data, length):
  ret = []
  model.eval()

  for idx in tqdm(range(length)):
    slc = test_data[idx:idx+28]
    slc_t = torch.tensor(slc.values).unsqueeze(0)
    pred = model(slc_t)

    ret.append(pred.detach().item())
    test_data['energy'][idx+28] = ret[-1]
  return ret

def predict_naive(model, test_data, length):
  ret = []
  model.eval()

  for idx in tqdm(range(length)):
    slc = test_data[idx:idx+28]
    slc = torch.tensor(slc.values).unsqueeze(0)
    ret.append(model(slc).detach().item())
  return ret

if __name__ == "__main__":
  comb_train, comb_test = load_data_helper()

  torch.set_default_dtype(torch.float64)
  # Load the net with trained weights
  net = LSTM2(1, 13, 512, 4)
  net.load_state_dict(torch.load("./checkpoints/model.pth"))

  test_with_start = pd.concat([comb_train[-28:],comb_test])
  #predict_sliding(net, s_data, comb_test, len(comb_test))
  pred_v = predict_naive(net, test_with_start, len(comb_test))

  # For testing purpose
  # TODO: write into a correct format like the sample_submission.csv
  import csv
  with open("./temp/pred_vals.csv", "w") as f:
    write = csv.writer(f)
    write.writerows([pred_v])
