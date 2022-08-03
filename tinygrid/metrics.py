import math
import numpy as np
from dataset import IEEE_CIS

def mase(pred: np.array, true: np.array, training: np.array, cycle: int=2688) -> int:
  """
  Compute the Mean Absolute Square Error (MASE)
  Params:
    pred: array of predicted value
    true: array of true value
    training: array of training value
    cycle: seasonal cycle (default 28-day-ahead seasonal naive, 28 * 96 = 2688)
  Return:
    MASE value
  """
  assert len(pred) == len(true)
  f_horizon = len(pred)

  up = np.sum(np.absolute(pred - true))
  down = f_horizon/(len(training_data) - cycle) * np.sum(np.absolute(training_data[cycle:] - training_data[:-cycle]))
  return up/down


if __name__ == "__main__":
  a = IEEE_CIS()
  energy = a.load_energy_data()
  pred = "sample_submission.csv"
  pred_data = dict()

  import csv
  with open(pred, "r") as f:
    read = csv.reader(f, delimiter=",")
    for row in read:
      pred_data[row[0]] = [int(i) for i in row[1:]]

  name = "Solar0"
  # Very scuff
  training_data = np.array(energy[name]['energy'][:-(2880*2 + 2976)])
  actual_data = np.array(energy[name]['energy'][-(2880*2 + 2976):-(2880 + 2976)])
  pp_data = np.array(pred_data[name][:2880])
  print(training_data.shape, actual_data.shape, pp_data.shape)
  print(mase(pp_data, actual_data, training_data))
  #print(actual_data)

    
     
