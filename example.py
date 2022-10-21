#!/usr/bin/env python3
import os, sys
from datetime import datetime

from tinygrid.dataset import IEEE_CIS
from tinygrid.forecaster import Forecaster, generate_building_data, generate_solar_data
from tinygrid.optimizer import optimizer, save_schedule
from tinygrid.utils import Const, mase, weekday_range

from extra import schedule_eval_wrapper


if __name__ == "__main__":
  sys.path.append(os.getcwd())
  cutoffs = { 
    'Building0' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),
    'Building1' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
    'Building3' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
    'Building4' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
    'Building5' : None,
    'Building6' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
    'Solar0'    : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
    'Solar1'    : None,
    'Solar2'    : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
    'Solar3'    : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
    'Solar4'    : None,
    'Solar5'    : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC)}

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


  en = IEEE_CIS.load_energy_data()
  ww = IEEE_CIS.load_ERA5_weather_data()

  ww = ww.drop(
              ['coordinates (lat,lon)', 
              'model (name)',
              'utc_offset (hrs)', 
              'model elevation (surface)',
              "mean_sea_level_pressure (Pa)",
              "wind_speed (m/s)",
              "relative_humidity ((0-1))"], 
              axis=1).resample('15min').asfreq()

  totl = 0.0
  for col in list(en.keys()):
    bb = en[col]
    b0train = bb[:Const.PHASE1_TIME_S1]
    b0test = bb[Const.PHASE1_TIME_S1:Const.PHASE2_TIME_S1]

    if col[:-1] == "Building":
      x_train, y_train = generate_building_data(data=b0train, cutoff_date=cutoffs[col], upper=omits[col][1], lower=omits[col][0])

      x_test = generate_building_data(data=None, start=Const.PHASE1_TIME, end=Const.PHASE2_TIME)
    else:
      x_train, y_train = generate_solar_data(data=b0train, weather_data=ww, cutoff_date=cutoffs[col])

      x_test = generate_solar_data(data=None, weather_data=ww, start=Const.PHASE1_TIME, end=Const.PHASE2_TIME)

    bf = Forecaster()
    bf.fit(x_train, y_train)
    y_pred = bf.predict(x_test)
    score = mase(y_pred, b0test['energy'].to_numpy(), b0train['energy'].to_numpy())
    print(f"{col}'s mase = {score}")
    totl += score
  print(f"Avg: {totl/len(en.keys())}")



  p1s = datetime(year=2020, month=10, day=1, hour=0, minute=0, tzinfo=Const.MELB)
  p1e = datetime(year=2020, month=10, day=31, hour=0, minute=0, tzinfo=Const.MELB)

  p2s = Const.PHASE2_TIME.astimezone(Const.MELB)
  p2e = Const.PHASE2_END_TIME.astimezone(Const.MELB)

  ins = IEEE_CIS().load_instance_data()
  price = IEEE_CIS().load_AEMO_price_data()['RRP']
  price = price.tz_convert(Const.MELB)
  for col in ins.keys():
    print(col, col[5])
    if col[:6] == "phase1":
      sol = optimizer(instance=ins[col], warm_start=None, price=price, start_time=p1s, end_time=p1e)
    elif col[:6] == "phase2":
      sol = optimizer(instance=ins[col], warm_start=None, price=price, start_time=p2s, end_time=p2e)
    save_schedule("output/{col[:-3]}_cpsat.txt", sol)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    f_ins_path = os.path.join(dir_path, f"tinygrid/dataset/instance/{col}")
    f_sol_path = os.path.join(dir_path, "output/{col[:-3]}_cpsat.txt")

    print(f"Java eval score: {schedule_eval_wrapper(f_ins_path, f_sol_path, col[5])}")
