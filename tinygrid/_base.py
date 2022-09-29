import os
from abc import ABC, abstractmethod
from functools import partialmethod
from datetime import datetime, timedelta

from tqdm import tqdm
import pandas as pd
import numpy as np

from .dataset import IEEE_CISMixin
from .utils import mase

# Flags
# How to invoke: DEBUG=1 python3 script.py
DEBUG = int(os.getenv('DEBUG', 0))


class _BaseForecaster(ABC, IEEE_CISMixin):
  """
  Base abstract class for different forecasting methods. This class should not be invoke.
  Inherit IEEE_CISMixin class, exposing method for loading data.
  All forecasting modules should inherit from this abstract class.
  Overide moethods if the base does not fit the inheritted functionality.
  """
  CACHE_FOLDER = "./cache/"
  CHECKPOINTS  = "./checkpoints/"


  def __init__(self, verbose: int=0, profile="default") -> None:
    """
    Params:
      verbose: level of verbosity, 0 is silent, >=1 for more info
      profile: how to split data
        - "default" is phase1 and phase2 prediction
        - "phase1" is just phase1 prediction
        - "phase2" is phase2 prediction, with phase1 include in the training data

    """
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
    self.verbose = verbose
    # Disable tqdm if self.verbose=0
    tqdm.__init__ = partialmethod(tqdm.__init__, disable=self.verbose<1)
    self.profile = profile

    # Weather data is instances agnostic, so we should only transform once
    self._prepare_weather_data()

    self.s1 = datetime(day=19, month=6, year=2020, hour=23, minute=59, second=59) # 20th June 
    self.s4 = datetime(day=1,  month=8, year=2020, hour=23, minute=59, second=59) # 2nd Aug
    self.s5 = datetime(day=14, month=9, year=2020, hour=23, minute=59, second=59) # 13th Sept
    self.s6 = datetime(day=17, month=10, year=2020, hour=23, minute=59, second=59) # 18th Oct


  def fit(self) -> None:
    """
    Fit every series with its own model.
    """
    if self.verbose>=1: print("Fitting...")
    for name in tqdm(self.names): 
      _, _, _, x_train, y_train = self._prepare_data(name)
      self.models[name].fit(x_train, y_train)


  def predict(self) -> None:
    """
    Run predict on all series with its own trained model.
    Can only be invoke after training.
    """
    if self.verbose>=1: print("Predicting...")
    for name in tqdm(self.names):
      _, x_test, _, _, _= self._prepare_data(name)
      self.y_preds[name] = self.models[name].predict(x_test)


  def evaluation(self) -> None:
    """
    Run evaludation on all predicted series.
    Can only be invoke after predict.
    """
    if self.verbose>=1: print("Evaluation...")
    for name in self.names:
      org_y_train, _, y_test, _, _ = self._prepare_data(name)
      y_pred = self.y_preds[name]
      r_mase = mase(y_pred, y_test, org_y_train)
      self.evals[name] = r_mase


  def _prepare_data(self, name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Prepare data per series basis
    """
    #energy = self.energy[name][self.cutoffs[name]:]
    #weather = self.weather[self.cutoffs[name]:]
    energy = self.energy[name]
    weather = self.weather
    # Join weather and energy data, date as shared col
    comb = energy.join(weather)

    HOUR = 24*60
    DAY = 24*60*60
    time_stamp = comb.index.map(pd.Timestamp.timestamp)
    # Transform raw seconds into sin and cos value
    # Creating a seasonal value that represent the repeat of day and year
    comb['hour_sin'] = np.cos(time_stamp * (2 * np.pi/HOUR))
    comb['hour_cos'] = np.cos(time_stamp * (2 * np.pi/HOUR))
    comb['day_sin'] = np.sin(time_stamp * (2 * np.pi/DAY))
    comb['day_cos'] = np.cos(time_stamp * (2 * np.pi/DAY))

    # Monday-Friday 1, else 0
    comb['weekday'] = comb.index.weekday < 5
    comb['weekday1'] = (comb.index.weekday < 4) & (comb.index.weekday > 0)
    # Boolean mask for weekdays
    for i in range(7):
      comb[f"wdx{i}"] = comb.index.weekday == i

    # Full capacity at before 20th June
    comb["restriction"] = ((comb.index < self.s1) == True) * 1
    # 10% occupancy 20th June - 2nd Aug
    comb["restriction"] += ((comb.index > self.s1) & (comb.index < self.s4) == True) * 0.1
    # 5% occupancy 2nd Aug - 13th Sept
    comb["restriction"] += ((comb.index > self.s4) & (comb.index < self.s5) == True) * 0.05
    # 25% occupancy 13th Sept - 18th Oct
    comb["restriction"] += ((comb.index > self.s5) & (comb.index < self.s6) == True) * 0.25
    # 30% occupancy 13th Sept - 18th Oct
    comb["restriction"] += ((comb.index > self.s6) == True) * 0.3

    # Split train and test
    if self.profile == "default":
      # Default train on historic data and predict on both phase1 and phase2
      comb_train = comb[:self.PHASE1_TIME]
      comb_test =  comb[self.PHASE1_TIME:]
    elif self.profile == "phase1":
      # Predict on phase1 only
      comb_train = comb[:self.PHASE1_TIME]
      comb_test =  comb[self.PHASE1_TIME:self.PHASE2_TIME]
    elif self.profile == "phase2":
      # Train data is now historic data and phase1 data, predict on phase2
      comb_train = comb[:self.PHASE2_TIME]
      comb_test =  comb[self.PHASE2_TIME:]

    # Non drop nan training data (used for mase calc)
    org_y_train = comb_train['energy'].to_numpy()
    y_test      = comb_test['energy'].to_numpy()

    # High and low data threshold.
    # TODO: Find a general way of doing this?
    if name == "Building0":
      comb_train = comb_train[comb_train['energy'] <=606.5]
    elif name == "Building3":
      comb_train = comb_train[(comb_train['energy']>=193) & (comb_train['energy']<=2264)]

    # Fill nan with means
    comb_train = comb_train.fillna(comb_train.mean())
    comb_test = comb_test.fillna(comb_test.mean())

    ## Cutoff data, we have to do this late because we are impute data using mean
    ## Cutting off early would result in garbage impute.
    comb_train = comb_train[self.cutoffs[name]:]

    # Turn to numpy for training
    x_test = comb_test.drop('energy', axis=1).to_numpy()
    x_train = comb_train.drop('energy', axis=1).to_numpy()
    y_train = comb_train['energy'].to_numpy()

    if DEBUG >= 1:
      print("Series:", name)
      print(f"x_train {x_train.shape}  x_test {x_test.shape}")
      print(f"y_train {y_train.shape}    y_test {y_test.shape}")
      print(f"org_y_train {org_y_train.shape}\n")

    return org_y_train, x_test, y_test, x_train, y_train

  def _prepare_weather_data(self):
    for col in list(self.weather.columns):
      for lag in range(1, 4):
        # Forward lag all columns 
        self.weather[f"{col}_lag_{lag}"] = self.weather[col].shift(lag)
        # Backward lag all columns
        self.weather[f"{col}_lag_{-lag}"] = self.weather[col].shift(-lag)
    self.weather = self.weather.interpolate()
