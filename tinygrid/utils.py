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
  if not isinstance(pred, np.ndarray):
    raise TypeError("'pred' must be numpy array")
  if not isinstance(true, np.ndarray):
    raise TypeError("'true' must be numpy array")
  if not isinstance(training, np.ndarray):
    raise TypeError("'training' must be numpy array")
  assert pred.shape == true.shape, "Predicted and actual array must have the same shape"

  f_horizon = len(pred)
  M = len(training)

  # TODO: how do we handle NaN value?
  up = np.sum(np.absolute(pred - true))
  down = f_horizon/(M - cycle) * np.sum(np.absolute(training[cycle:] - training[:-cycle]))
  return up/down


def denormalize(vals, mx: int, mi: int):
  return vals * (mx - mi) - mi


def normalize(vals, mx: int, mi: int):
  return (vals-mi)/(mx-mi)
