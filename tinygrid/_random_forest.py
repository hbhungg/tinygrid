import os
import datetime
import warnings
from functools import partialmethod

import sklearn.ensemble 
import pandas as pd
import numpy as np
from tqdm import tqdm

from . import _BaseForecaster
from .utils import mase


# Flags
# How to invoke: DEBUG=1 python3 script.py
DEBUG = int(os.getenv('DEBUG', 0))
VERBOSE = int(os.getenv('VERBOSE', 0))

CUTOFFS = { 'Building0' : datetime.datetime(day=1,  month=6,  year=2020, hour=0, minute=0, second=0),
            'Building1' : datetime.datetime(day=1,  month=2,  year=2020, hour=0, minute=0, second=0),  
            'Building3' : datetime.datetime(day=1,  month=5,  year=2019, hour=0, minute=0, second=0),  
            'Building4' : datetime.datetime(day=1,  month=11, year=2019, hour=0, minute=0, second=0),  
            'Building5' : datetime.datetime(day=1,  month=1,  year=2019, hour=0, minute=0, second=0),  
            'Building6' : datetime.datetime(day=1,  month=11, year=2019, hour=0, minute=0, second=0),  
            'Solar0'    : datetime.datetime(day=1,  month=6,  year=2020, hour=0, minute=0, second=0),  
            'Solar1'    : datetime.datetime(day=21, month=5,  year=2020, hour=0, minute=0, second=0),  
            'Solar2'    : datetime.datetime(day=21, month=5,  year=2020, hour=0, minute=0, second=0),  
            'Solar3'    : datetime.datetime(day=21, month=5,  year=2020, hour=0, minute=0, second=0),  
            'Solar4'    : 0,
            'Solar5'    : datetime.datetime(day=31, month=5,  year=2020, hour=0, minute=0, second=0)}   

# Disable tqmd if not in debug mode
tqdm.__init__ = partialmethod(tqdm.__init__, disable=VERBOSE<1)

class RandomForestForecaster(_BaseForecaster):
  def __init__(self):
    super(RandomForestForecaster, self).__init__()
    self.rfs = dict()
    self.y_preds = dict()
    self.evals = dict()
    # Each series have its own Random Forest model
    for name in self.names:
      self.rfs[name] = sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20)
      self.y_preds[name] = None


  def fit(self):
    """
    Fit every series with its own random forest model
    """
    if VERBOSE>=1: print("Fitting...")
    for name in tqdm(self.names): 
      _, _, _, x_train, y_train = self._prepare_data(name)
      self.rfs[name].fit(x_train, y_train)

  def predict(self):
    """
    Run predict
    """
    if VERBOSE>=1: print("Predicting...")
    for name in tqdm(self.names):
      _, x_test, _, _, _= self._prepare_data(name)
      self.y_preds[name] = self.rfs[name].predict(x_test)


  def evaluation(self):
    if VERBOSE>=1: print("Evaluation...")
    for name in self.names:
      org_y_train, _, y_test, _, _ = self._prepare_data(name)
      y_pred = self.y_preds[name]
      #print(f"predicted response:\n{y_pred}")
      #print("mean square error:", sklearn.metrics.mean_squared_error(y_test, y_pred))
      #print("mean abs error:", sklearn.metrics.mean_absolute_error(y_test, y_pred))
      r_mase = mase(y_pred, y_test, org_y_train)
      self.evals[name] = r_mase

  def _prepare_data(self, name: str):
    """
    Prepare data per series basis
    """
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

    # Split train and test (test is phase1 + phase2)
    comb_train = comb[:_BaseForecaster.PHASE1_TIME]
    comb_test =  comb[_BaseForecaster.PHASE1_TIME:]

    # Non drop nan training data (used for mase calc)
    org_y_train = comb_train['energy'].to_numpy()
    x_test      = comb_test.drop('energy', axis=1).to_numpy()
    y_test      = comb_test['energy'].to_numpy()

    # Cutoff data
    comb_train = comb_train[CUTOFFS[name]:]

    # Drop nan training data, used for fitting
    x_train = comb_train.dropna().drop('energy', axis=1).to_numpy()
    y_train = comb_train.dropna()['energy'].to_numpy()

    if DEBUG >= 1:
      print("Series:", name)
      print("Before", org_x_train.shape, x_test.shape)
      print("After", x_train.shape, x_test.shape)
      print("Before", org_y_train.shape, y_test.shape)
      print(f"After {y_train.shape} {y_test.shape}\n")

    return org_y_train, x_test, y_test, x_train, y_train


if __name__ == "__main__":
  rf = RandomForest()
  rf.load_energy_data()

