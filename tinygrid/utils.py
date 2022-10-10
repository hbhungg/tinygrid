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
    raise TypeError(f"'pred' type {type(pred)} is not numpy array")
  if not isinstance(true, np.ndarray):
    raise TypeError(f"'true' type {type(true)} is not numpy array")
  if not isinstance(training, np.ndarray):
    raise TypeError(f"'training' type {type(training)} is not numpy array")
  if pred.shape != true.shape:
    raise ValueError(f"{pred.shape} does not match {true.shape}")

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

