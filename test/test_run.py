import json
import datetime

from tinygrid.dataset import IEEE_CISMixin
from tinygrid.forecaster import Forecaster, generate_building_data, generate_solar_data
from tinygrid.utils import Const, mase

cutoffs = { 
  'Building0' : datetime.datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),
  'Building1' : datetime.datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
  'Building3' : datetime.datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
  'Building4' : datetime.datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
  'Building5' : None,
  'Building6' : datetime.datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
  'Solar0'    : datetime.datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
  'Solar1'    : None,
  'Solar2'    : datetime.datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
  'Solar3'    : datetime.datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
  'Solar4'    : None,
  'Solar5'    : datetime.datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC)}

omits = { 
  'Building0' : (None, 606.5),
  'Building1' : (None, None) ,
  'Building3' : (193, 2264)  ,
  'Building4' : (None, None) ,
  'Building5' : (None, None) ,
  'Building6' : (None, None) ,
  'Solar0'    : (None, None) ,
  'Solar1'    : (None, None) ,
  'Solar2'    : (None, None) ,
  'Solar3'    : (None, None) ,
  'Solar4'    : (None, None) ,
  'Solar5'    : (None, None) }


if __name__ == "__main__":
  en = IEEE_CISMixin._load_energy_data()

  totl = 0.0
  for col in list(en.keys()):
    bb = en[col]
    b0train = bb[:Const.PHASE1_TIME_S1]
    b0test = bb[Const.PHASE1_TIME_S1:Const.PHASE2_TIME_S1]
    #print(b0train, b0test)

    if col[:-1] == "Building":
      x_train, y_train = generate_building_data(data=b0train, cutoff_date=cutoffs[col], upper=omits[col][1], lower=omits[col][0])
      #print(x_train.shape, y_train.shape)

      x_test = generate_building_data(data=None, start=Const.PHASE1_TIME, end=Const.PHASE2_TIME)
      #print(x_test.shape, b0test.shape)
    else:
      ww = IEEE_CISMixin._load_ERA5_weather_data()
      x_train, y_train = generate_solar_data(data=b0train, weather_data=ww, cutoff_date=cutoffs[col])
      #print(x_train.shape, y_train.shape)

      x_test = generate_solar_data(data=None, weather_data=ww, start=Const.PHASE1_TIME, end=Const.PHASE2_TIME)
      #print(x_test.shape, b0test.shape)
      #print(col)

    bf = Forecaster()
    bf.fit(x_train, y_train)
    y_pred = bf.predict(x_test)
    score = mase(y_pred, b0test['energy'].to_numpy(), b0train['energy'].to_numpy())
    print(f"{col}'s mase = {score}")
    totl += score
  print(f"Avg: {totl/len(en.keys())}")


  # Optimization
#  a = CP_SAT_Solver()
#  a.create_variables()
#  a.create_hint()
#  #a.fix_start()
#  a.create_constraint()
#  a.solve()
#  a.compare_to_java()


