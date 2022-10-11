import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo

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


class Const:
  UTC = ZoneInfo("UTC")
  MELB = ZoneInfo("Australia/Melbourne")
  PHASE1_TIME = datetime(day=1, month=10, year=2020, hour=0, minute=0, second=0, tzinfo=UTC)
  PHASE2_TIME = datetime(day=1, month=11, year=2020, hour=0, minute=0, second=0, tzinfo=UTC)
  # Phase 1 and 2 time with 1 sec subtract, used to deal with dataframe split boundary.
  PHASE1_TIME_S1 = datetime(day=30, month=9, year=2020, hour=23, minute=59, second=59,tzinfo=UTC)
  PHASE2_TIME_S1 = datetime(day=31, month=10, year=2020, hour=23, minute=59, second=59,tzinfo=UTC)

  PERIOD_IN_HOUR = 4
  OFFICE_PERIOD = 8 * PERIOD_IN_HOUR
  PERIOD_IN_DAY = 24 * PERIOD_IN_HOUR
  PERIOD_IN_WEEK = PERIOD_IN_DAY * 7

  # Date for covid restriction
  S1 = datetime(day=19, month=6, year=2020, hour=23, minute=59, second=59, tzinfo=UTC) # 20th June 
  S2 = datetime(day=1,  month=8, year=2020, hour=23, minute=59, second=59, tzinfo=UTC) # 2nd Aug
  S3 = datetime(day=14, month=9, year=2020, hour=23, minute=59, second=59, tzinfo=UTC) # 13th Sept
  S4 = datetime(day=17, month=10, year=2020, hour=23, minute=59, second=59, tzinfo=UTC) # 18th Oct
