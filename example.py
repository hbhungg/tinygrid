#!/usr/bin/env python3
import os, sys
from datetime import datetime

from tinygrid.dataset import IEEE_CISMixin
from tinygrid.forecaster import Forecaster, generate_building_data, generate_solar_data
from tinygrid.optimizer.rewrite import optimizer, save_schedule
from tinygrid.utils import Const, mase, weekday_range

from extra import schedule_eval_wrapper


if __name__ == "__main__":
#  cutoffs = { 
#    'Building0' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),
#    'Building1' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
#    'Building3' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
#    'Building4' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
#    'Building5' : None,
#    'Building6' : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
#    'Solar0'    : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
#    'Solar1'    : None,
#    'Solar2'    : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
#    'Solar3'    : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC),  
#    'Solar4'    : None,
#    'Solar5'    : datetime(day=1, month=1,  year=2020, hour=0, minute=0, second=0, tzinfo=Const.UTC)}
#
#  omits = { 
#    'Building0' : (None, 606.5),
#    'Building1' : (None, None) ,
#    'Building3' : (193, 2264)  ,
#    'Building4' : (None, None) ,
#    'Building5' : (None, None) ,
#    'Building6' : (None, None) ,
#    'Solar0'    : (None, None) ,
#    'Solar1'    : (None, None) ,
#    'Solar2'    : (None, None) ,
#    'Solar3'    : (None, None) ,
#    'Solar4'    : (None, None) ,
#    'Solar5'    : (None, None) }
#
#
#  en = IEEE_CISMixin._load_energy_data()
#  ww = IEEE_CISMixin._load_ERA5_weather_data()
#
#  totl = 0.0
#  for col in list(en.keys()):
#    bb = en[col]
#    b0train = bb[:Const.PHASE1_TIME_S1]
#    b0test = bb[Const.PHASE1_TIME_S1:Const.PHASE2_TIME_S1]
#    #print(b0train, b0test)
#
#    if col[:-1] == "Building":
#      x_train, y_train = generate_building_data(data=b0train, cutoff_date=cutoffs[col], upper=omits[col][1], lower=omits[col][0])
#
#      x_test = generate_building_data(data=None, start=Const.PHASE1_TIME, end=Const.PHASE2_TIME)
#    else:
#      x_train, y_train = generate_solar_data(data=b0train, weather_data=ww, cutoff_date=cutoffs[col])
#
#      x_test = generate_solar_data(data=None, weather_data=ww, start=Const.PHASE1_TIME, end=Const.PHASE2_TIME)
#
#    bf = Forecaster()
#    bf.fit(x_train, y_train)
#    y_pred = bf.predict(x_test)
#    score = mase(y_pred, b0test['energy'].to_numpy(), b0train['energy'].to_numpy())
#    print(f"{col}'s mase = {score}")
#    totl += score
#  print(f"Avg: {totl/len(en.keys())}")
#


  p1s = datetime(year=2020, month=10, day=1, hour=0, minute=0, tzinfo=Const.MELB)
  p1e = datetime(year=2020, month=10, day=31, hour=0, minute=0, tzinfo=Const.MELB)

  p2s = Const.PHASE2_TIME.astimezone(Const.MELB)
  p2e = Const.PHASE2_END_TIME.astimezone(Const.MELB)

  ins = IEEE_CISMixin()._load_instance_data()["phase1_instance_small_0.txt"]
  sam_sol = IEEE_CISMixin()._load_instance_sample_solution_data()["phase1_instance_solution_small_0.txt"]
  price = IEEE_CISMixin()._load_AEMO_price_data()['RRP']

  sol = optimizer(instance=ins, warm_start=sam_sol, start_time=p1s, end_time=p1e)
  save_schedule("oo.txt", sol)
  dir_path = os.path.dirname(os.path.realpath(__file__))
  f_ins_path = os.path.join(dir_path, "tinygrid/dataset/instance/phase1_instance_small_0.txt")
  f_sol_path = os.path.join(dir_path, "oo.txt")
  #f_sol_path = os.path.join(dir_path, "tinygrid/dataset/instance_sample_solution/phase1_instance_solution_small_0.txt")

  print(f"Java eval score: {schedule_eval_wrapper(f_ins_path, f_sol_path, 1)}")

  #sss = list(weekday_range(p2s, p2e, True))
  #for i in range(1, len(sss)):
  #  if sss[i][0] - sss[i-1][0] == 1:
  #    print(sss[i], True)
  #  else:
  #    print()
  #    print(sss[i], False)
