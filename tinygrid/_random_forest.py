import datetime
import sklearn.ensemble 
from . import _BaseForecaster


class RandomForestForecaster(_BaseForecaster):
  def __init__(self, verbose=0, profile="default"):
    super(RandomForestForecaster, self).__init__(verbose, profile)
    # Each series have its own Random Forest model
    # n_jobs=-1 means use all available cores.
    self.models = {
      'Building0' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Building1' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Building3' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Building4' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Building5' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Building6' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Solar0'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Solar1'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Solar2'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Solar3'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Solar4'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1),
      'Solar5'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=-1)}

    # Each series have its own cuts
    self.cutoffs = { 
      'Building0' : datetime.datetime(day=1,  month=6,  year=2020, hour=0, minute=0, second=0),
      'Building1' : datetime.datetime(day=1,  month=2,  year=2020, hour=0, minute=0, second=0),  
      'Building3' : datetime.datetime(day=1,  month=5,  year=2019, hour=0, minute=0, second=0),  
      'Building4' : datetime.datetime(day=1,  month=11, year=2019, hour=0, minute=0, second=0),  
      'Building5' : datetime.datetime(day=1,  month=1,  year=2019, hour=0, minute=0, second=0),  
      'Building6' : datetime.datetime(day=1,  month=11, year=2019, hour=0, minute=0, second=0),  
      'Solar0'    : datetime.datetime(day=1,  month=6,  year=2020, hour=0, minute=0, second=0),  
      'Solar1'    : datetime.datetime(day=21, month=5,  year=2020, hour=0, minute=0, second=0),  
      'Solar2'    : datetime.datetime(day=21, month=5,  year=2020, hour=0, minute=0, second=0),  
      'Solar3'    : datetime.datetime(day=21, month=5,  year=2020, hour=0, minute=0, second=0),  
      'Solar4'    : None,
      'Solar5'    : datetime.datetime(day=31, month=5,  year=2020, hour=0, minute=0, second=0)}

