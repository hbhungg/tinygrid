#!/usr/bin/env python3
import torch
from net import LSTM2
from dataloader import load_data_helper
import pandas as pd


# TODO: complete this
def predict_sliding(model, s_data, test_data, length):
  ret = []
  model.eval()
  return ret

def predict_naive(model, test_data, length):
  ret = []
  model.eval()

  from tqdm import tqdm
  for idx in tqdm(range(length)):
    slc = test_data[idx:idx+28].values
    slc = torch.tensor(slc)
    slc = slc.unsqueeze(0)
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
