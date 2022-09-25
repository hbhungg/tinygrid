import json
import math
import datetime
import numpy as np
from ortools.sat.python import cp_model

from tinygrid import RandomForestForecaster
from tinygrid.dataset import IEEE_CISMixin
from tinygrid.schedule_eval import schedule_eval_wrapper


# Phase 1 stuffs
PERIOD_IN_HOUR = 4
START_MONDAY = 384
END = 2976
START_MONDAY_9AM = 384 + 9 * PERIOD_IN_HOUR 
START_MONDAY_5PM = 384 + 17 * PERIOD_IN_HOUR
FIRST_WEEK_9AM = [(START_MONDAY_9AM + 24 * i * PERIOD_IN_HOUR)+1 for i in range(5)]
FIRST_WEEK_5PM = [(START_MONDAY_5PM + 24 * i * PERIOD_IN_HOUR)-1 for i in range(5)]
FIRST_WEEK_IN_OFFICE = list(zip(FIRST_WEEK_9AM, FIRST_WEEK_5PM))
OFFICE_PERIOD = 8 * PERIOD_IN_HOUR
DAY_PERIOD = 24 * PERIOD_IN_HOUR

ss = datetime.datetime.strptime("2020-9-30 14:00", "%Y-%m-%d %H:%M")
ee = datetime.datetime.strptime("2020-10-31 13:59", "%Y-%m-%d %H:%M")


class CP_SAT_Solver(IEEE_CISMixin):
  def __init__(self):
    self.model = cp_model.CpModel()

    # TODO: load all instance ofc
    temp_ins_name = 'phase1_instance_small_0.txt'
    temp_sol_name = 'phase1_instance_solution_small_0.txt'
    self.instances = self._load_instance_data()[temp_ins_name]
    self.sample_solution = self._load_instance_sample_solution_data()[temp_sol_name]
    self.price = self._load_AEMO_price_data()['RRP']

    self.re_act = self.instances.re_act
    self.total_small = sum([i.n_small for i in self.instances.buildings.values()])
    self.total_large = sum([i.n_large for i in self.instances.buildings.values()])

    with open("../../cache/final_forecast.json", "r") as f:
      self.y_preds = json.load(f)

  def create_variables(self):
    # Start time for each activity
    self.act_start_time = {}
    for key, val in self.re_act.items():
      # Activity cannot start at time [(end-duration) -> end]
      self.act_start_time[key] = \
        self.model.NewIntVar(START_MONDAY_9AM, START_MONDAY_5PM * 24 * 4-1, f"act_start_time_{key}")

    # Binary array for if activity is in duration
    self.act_in_duration = {}
    # Binary array for activity start time
    self.act_start_bool = {}

    for key, val in self.re_act.items():
      for s, e in FIRST_WEEK_IN_OFFICE:
        for t in range(s, e):
          self.act_in_duration[(key, t)] = \
            self.model.NewBoolVar(f"act_in_duration_{key}_{t}")
        for t in range(s, e-val.duration):
          self.act_start_bool[(key, t)] = \
              self.model.NewBoolVar(f"act_start_bool_{key}_{t}")

    # NOTES: Use this for when optimizing once off, since recurrence is always scheduled.
    ## If a particular activity is scheduled
    #self.act_scheduled = {}
    #for key, val in self.re_act.items():
    #  self.act_scheduled[key] = self.model.NewBoolVar(f"act_scheduled_{key}")

  def create_constraint(self):
    for key, val in self.re_act.items():
      temp = []
      st = 0
      for s, e in FIRST_WEEK_IN_OFFICE:
        for t in range(s, e-val.duration):
          temp.append(self.act_start_bool[(key, t)])
          st += t * self.act_start_bool[(key, t)]
        for t in range(s, e):
          zt = sum([self.act_start_bool.get((key, tt), 0) for tt in range(t-val.duration+1, t)])
          self.model.Add(self.act_in_duration[(key, t)] == zt)
      # Activity must be scheduled and can only be schedule once
      self.model.AddExactlyOne(temp)
      # Activity start time
      self.model.Add(self.act_start_time[key] == st)
    
    # Precedences
    for key, val in self.re_act.items():
      for prec in val.prec:
        self.model.Add(self.act_start_time[key] >= self.act_start_time[prec] + self.re_act[prec].duration)

    for s, e in FIRST_WEEK_IN_OFFICE:
      for t in range(s, e):
        c_small = 0
        c_large = 0
        for key, val in self.re_act.items():
          if self.instances.re_act[key].size == "S":
            c_small += self.act_in_duration[(key, t)] * self.instances.re_act[key].n_room
          elif self.instances.re_act[key].size == "L":
            c_large += self.act_in_duration[(key, t)] * self.instances.re_act[key].n_room
          
    #    # At every timestep, total number of small room and large room must not exceed the total large and small room available.
        self.model.Add(c_small <= self.total_small)
        self.model.Add(c_large <= self.total_large)

    # TODO: Add minimizing obj function

  def create_hint(self):
    re_act = self.sample_solution.re_act
    for key, val in re_act.items():
      print(val)

  def solve(self):
    self.solver = cp_model.CpSolver()
    status = self.solver.Solve(self.model)

    ret = []
    curr_small = [None] * self.total_small
    curr_large = [None] * self.total_large
    curr_small_bmap = []
    curr_large_bmap = []
    for key, val in self.instances.buildings.items():
        for i in range(val.n_small):
          curr_small_bmap.append(key)
        for i in range(val.n_large):
          curr_large_bmap.append(key)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
      # NOTES: This are bad code. Need to be refractor
      for s, e in FIRST_WEEK_IN_OFFICE:
        for t in range(s, e):
          for key, val in self.re_act.items():
            # if t == 0 and t-1 == 1, activity end
            if (self.solver.Value(self.act_in_duration[(key, t)]) == 0) and (self.solver.Value(self.act_in_duration.get((key, t-1), 0)) == 1):
              for r in range(self.re_act[key].n_room):
                if val.size == "S":
                  for idx, v in enumerate(curr_small):
                    if v == key :
                      curr_small[idx] = None
                      break
                if val.size == "L":
                  for idx, v in enumerate(curr_large):
                    if v == key:
                      curr_large[idx] = None
                      break

          for key, val in self.re_act.items():
            # if t == 1 and t-1 == 0, activity start, assigning rooms to for activity
            if (self.solver.Value(self.act_in_duration[(key, t)]) == 1) and (self.solver.Value(self.act_in_duration.get((key, t-1), 0)) == 0):
              temp = []
              for r in range(self.re_act[key].n_room):
                if val.size == "S":
                  for idx, v in enumerate(curr_small):
                    if v is None:
                      curr_small[idx] = key
                      temp.append(curr_small_bmap[idx])
                      break
                if val.size == "L":
                  for idx, v in enumerate(curr_large):
                    if v is None:
                      curr_large[idx] = key
                      temp.append(curr_large_bmap[idx])
                      break
              #print(key, val.size, curr_small, curr_large)
              lb = " ".join(map(str, temp))
              #print(lb)
              ret.append(f"r {key} {self.solver.Value(self.act_start_time[key])} {self.re_act[key].n_room} {lb}\n")

      with open("../cache/tt.txt", "w") as f:
        with open("../dataset/instance/phase1_instance_small_0.txt", "r") as tt:
          f.write(tt.readline())
          f.write(f"sched {len(self.re_act)} 0\n")
          for r in ret:
            f.write(r)

      import os
      dir_path = os.path.dirname(os.path.realpath(__file__))
      f_ins_path = os.path.join(dir_path, "../dataset/instance/phase1_instance_small_0.txt")
      f_sol_path = os.path.join(dir_path, "../cache/tt.txt")
      print(f"Java eval score: {schedule_eval_wrapper(f_ins_path, f_sol_path, 1)}")
    else:
      print("No solution found")

  def compare_to_java(self):
    pass
  


if __name__ == "__main__":
  a = CP_SAT_Solver()
  a.create_variables()
  a.create_constraint()
  a.solve()
