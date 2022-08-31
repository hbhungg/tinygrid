import datetime
import sklearn.ensemble 
from . import _BaseForecaster


class RandomForestForecaster(_BaseForecaster):
  def __init__(self):
    super(RandomForestForecaster, self).__init__()
    # Each series have its own Random Forest model
    self.models = {
      'Building0' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Building1' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Building3' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Building4' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Building5' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Building6' : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Solar0'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Solar1'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Solar2'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Solar3'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Solar4'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20),
      'Solar5'    : sklearn.ensemble.RandomForestRegressor(n_estimators=200, n_jobs=20)}

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
      'Solar4'    : 0,
      'Solar5'    : datetime.datetime(day=31, month=5,  year=2020, hour=0, minute=0, second=0)}

