import os
from abc import ABC, abstractmethod
from functools import partialmethod

from tqdm import tqdm
import pandas as pd
import numpy as np

from .dataset import IEEE_CISMixin
from .utils import mase

#import warnings
#warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# Flags
# How to invoke: DEBUG=1 python3 script.py
DEBUG = int(os.getenv('DEBUG', 0))
VERBOSE = int(os.getenv('VERBOSE', 0))

# Disable tqdm if VERBOSE=0
tqdm.__init__ = partialmethod(tqdm.__init__, disable=VERBOSE<1)

class _BaseForecaster(ABC, IEEE_CISMixin):
  """
  Base abstract class for different forecasting methods. This class should not be invoke.
  Inherit IEEE_CISMixin class, exposing method for loading data.
  All forecasting modules should inherit from this abstract class.
  Overide moethods if the base does not fit the inheritted functionality.
  """
  CACHE_FOLDER = "./cache/"
  CHECKPOINTS  = "./checkpoints/"

  def __init__(self) -> None:
    self.energy = self._load_energy_data()
    self.weather = self._load_ERA5_weather_data()
    # Drop unused cols, upsample to 15 minutes
    self.weather = self.weather.drop(
               ['coordinates (lat,lon)', 
                'model (name)',
                'utc_offset (hrs)', 
                'model elevation (surface)',
                "mean_sea_level_pressure (Pa)",
                "wind_speed (m/s)",
                "relative_humidity ((0-1))"], 
               axis=1).resample('15min').asfreq()

    self.names = [i for i in self.energy]
    self.y_preds = dict()
    self.evals = dict()
    self.models = dict()
    self.cutoffs = dict()


  def fit(self) -> None:
    """
    Fit every series with its own model.
    """
    if VERBOSE>=1: print("Fitting...")
    for name in tqdm(self.names): 
      _, _, _, x_train, y_train = self._prepare_data(name)
      self.models[name].fit(x_train, y_train)


  def predict(self) -> None:
    """
    Run predict on all series with its own trained model.
    Can only be invoke after training.
    """
    if VERBOSE>=1: print("Predicting...")
    for name in tqdm(self.names):
      _, x_test, _, _, _= self._prepare_data(name)
      self.y_preds[name] = self.models[name].predict(x_test)


  def evaluation(self) -> None:
    """
    Run evaludation on all predicted series.
    Can only be invoke after predict.
    """
    if VERBOSE>=1: print("Evaluation...")
    for name in self.names:
      org_y_train, _, y_test, _, _ = self._prepare_data(name)
      y_pred = self.y_preds[name]
      r_mase = mase(y_pred, y_test, org_y_train)
      self.evals[name] = r_mase


  def _prepare_data(self, name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Prepare data per series basis
    """
    no_lag = []

    self.weather = self.weather.interpolate()
    energy = self.energy[name]
    # Join weather and energy data, date as shared col
    comb = energy.join(self.weather)

    HOUR = 24*60
    DAY = 24*60*60
    time_stamp = comb.index.map(pd.Timestamp.timestamp)
    # Transform raw seconds into sin and cos value
    # Creating a seasonal value that represent the repeat of day and year
    comb['hour_sin'] = np.cos(time_stamp * (2 * np.pi/HOUR))
    comb['hour_cos'] = np.cos(time_stamp * (2 * np.pi/HOUR))
    comb['day_sin'] = np.sin(time_stamp * (2 * np.pi/DAY))
    comb['day_cos'] = np.cos(time_stamp * (2 * np.pi/DAY))
    no_lag += ['hour_sin', 'hour_cos', 'day_sin', 'day_cos']

    # Monday-Friday 1, else 0
    comb['weekday'] = comb.index.weekday < 5
    comb['weekday1'] = (comb.index.weekday < 4) & (comb.index.weekday > 0)
    no_lag.append('weekday')
    no_lag.append('weekday1')
    # Boolean mask for weekdays
    for i in range(7):
      comb[f"wdx{i}"] = comb.index.weekday == i
      no_lag.append(f"wdx{i}")

    # Split train and test (test is phase1 + phase2)
    comb_train = comb[:_BaseForecaster.PHASE1_TIME].copy()
    comb_test =  comb[_BaseForecaster.PHASE1_TIME:].copy()

    # Non drop nan training data (used for mase calc)
    org_y_train = comb_train['energy'].to_numpy()
    y_test      = comb_test['energy'].to_numpy()

    # Cutoff data
    comb_train = comb_train[self.cutoffs[name]:]
    no_lag.append('energy')

    for col in comb:
      if col not in no_lag:
        for lag in range(1, 4):
          # Forward lag all columns 
          comb_train[f"{col}_lag_{lag}"] = comb_train[col].copy().shift(lag).copy()
          comb_test[f"{col}_lag_{lag}"] = comb_test[col].copy().shift(lag).copy()
          # Backward lag all columns
          comb_train[f"{col}_lag_{-lag}"] = comb_train[col].copy().shift(-lag).copy()
          comb_test[f"{col}_lag_{-lag}"] = comb_test[col].copy().shift(-lag).copy()

    # Fill nan with means
    comb_train = comb_train.fillna(comb_train.mean())
    comb_test = comb_test.fillna(comb_test.mean())
    #x_train = comb_train.dropna().drop('energy', axis=1).to_numpy()
    #y_train = comb_train.dropna()['energy'].to_numpy()

    x_test = comb_test.drop('energy', axis=1).to_numpy()
    x_train = comb_train.drop('energy', axis=1).to_numpy()
    y_train = comb_train['energy'].to_numpy()

    if DEBUG >= 1:
      print("Series:", name)
      print(f"x_train {x_train.shape}  x_test {x_test.shape}")
      print(f"y_train {y_train.shape}    y_test {y_test.shape}")
      print(f"org_y_train {org_y_train.shape}\n")

    return org_y_train, x_test, y_test, x_train, y_train

