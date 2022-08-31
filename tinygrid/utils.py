import math
import numpy as np

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

  # Remove NaN values
  pred = pred[~np.isnan(true), ...]
  true = true[~np.isnan(true), ...]

  error = np.mean(np.absolute(pred - true))
  # Calc diff with NaN values, any subtract with NaN will equal to NaN
  diff = training[cycle:] - training[:-cycle] 
  # Remove NaN values
  diff = diff[~np.isnan(diff), ...]
  scale = np.mean(np.absolute(diff))
  return error/scale


def denormalize(vals, mx: int, mi: int):
  return vals * (mx - mi) - mi


def normalize(vals, mx: int, mi: int):
  return (vals-mi)/(mx-mi)

