import datetime

import sklearn.linear_model

from . import _BaseForecaster
from .utils import mase


class LassoForecaster(_BaseForecaster):
  def __init__(self):
    super(LassoForecaster, self).__init__()
    # Each series have its own Random Forest model
    self.models = {
      'Building0' : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Building1' : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Building3' : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Building4' : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Building5' : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Building6' : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Solar0'    : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Solar1'    : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Solar2'    : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Solar3'    : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Solar4'    : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False), 
      'Solar5'    : sklearn.linear_model.LassoLarsCV(max_iter=10, normalize=False)}

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

