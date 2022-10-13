import numpy as np
from datetime import datetime, time, timedelta
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

def date_range(start: datetime, end: datetime, 
               step=timedelta(minutes=15)) -> datetime:
  """
  Similar to range(), but for dates.
  Inclusive start, exclusive end.
  """
  curr = start
  while curr != end:
    yield curr
    curr += step

def weekday_range(start: datetime, end: datetime, office=False) -> tuple[int, int]:
  """
  Generate all indexes of weekday (Monday - Friday)
  Params:
    start: start time
    end: end time
    office: True, take office hour timestep only, False, take all weekday timestep
  """
  fw = False
  for idx, tx in enumerate(date_range(start, end)):
    isow = tx.isoweekday()
    # Start at the first week of the month (first Monday).
    if isow == Const.MONDAY: 
      fw = True
    if isow <= Const.FRIDAY and fw is True: 
      if office is True and (Const.OFFICE_OPEN_TIME <= tx.time() <= Const.OFFICE_CLOSE_TIME):
        yield (idx, isow)
      elif office is False: 
        yield (idx, isow)


def first_dow(dow: int, start: datetime, end: datetime) -> tuple[int, datetime]:
  """
  Return the index of the first time step of the first week day of the month
  Params:
    dow: iso weekday
    start: start time
    end: end time
  """
  for idx, tx in enumerate(date_range(start, end)):
    if tx.isoweekday() == dow: return idx, tx

def first_week_map(start: datetime, end: datetime, office=False) -> int:
  """
  Similar to weekday_range, but map all day to the first week
  Use for the recurrence activity.
  """
  fw = False
  fmonday, _ = first_dow(1, start, end)
  idx = fmonday
  curr_isow = 1
  for _, isow in weekday_range(start, end, office):
    if isow >= curr_isow:
      curr_isow = isow
      yield idx
    else:
      idx = fmonday
      curr_isow = 1
      yield idx
    idx += 1


class Const:
  UTC = ZoneInfo("UTC")
  MELB = ZoneInfo("Australia/Melbourne")
  PHASE1_TIME = datetime(day=1, month=10, year=2020, hour=0, minute=0, second=0, tzinfo=UTC)
  PHASE2_TIME = datetime(day=1, month=11, year=2020, hour=0, minute=0, second=0, tzinfo=UTC)
  PHASE2_END_TIME = datetime(day=1, month=12, year=2020, hour=0, minute=0, second=0, tzinfo=UTC)
  # Phase 1 and 2 time with 1 sec subtract, used to deal with dataframe split boundary.
  PHASE1_TIME_S1 = datetime(day=30, month=9, year=2020, hour=23, minute=59, second=59,tzinfo=UTC)
  PHASE2_TIME_S1 = datetime(day=31, month=10, year=2020, hour=23, minute=59, second=59,tzinfo=UTC)

  # Office open and close time (9:00am - 5:00pm) (9:00 - 17:00)
  OFFICE_OPEN_TIME = time(hour=9, minute=0, second=0) 
  OFFICE_CLOSE_TIME = time(hour=17, minute=0, second=0)
  PERIOD_IN_HOUR = 4
  OFFICE_PERIOD = 8 * PERIOD_IN_HOUR
  PERIOD_IN_DAY = 24 * PERIOD_IN_HOUR
  PERIOD_IN_WEEK = PERIOD_IN_DAY * 7
  PERIOD_MINUTE = timedelta(minutes=15)
  
  # ISO integer value of weekday.
  MONDAY    = 1
  TUESDAY   = 2
  WEDNESDAY = 3
  THURSDAY  = 4
  FRIDAY    = 5
  SATURDAY  = 6
  SUNDAY    = 7

  # Date for covid restriction
  S1 = datetime(day=19, month=6, year=2020, hour=23, minute=59, second=59, tzinfo=UTC) # 20th June 
  S2 = datetime(day=1,  month=8, year=2020, hour=23, minute=59, second=59, tzinfo=UTC) # 2nd Aug
  S3 = datetime(day=14, month=9, year=2020, hour=23, minute=59, second=59, tzinfo=UTC) # 13th Sept
  S4 = datetime(day=17, month=10, year=2020, hour=23, minute=59, second=59, tzinfo=UTC) # 18th Oct
