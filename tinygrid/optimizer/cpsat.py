import json
import os
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
FIRST_WEEK_9AM = [(START_MONDAY_9AM + 24 * i * PERIOD_IN_HOUR) for i in range(5)]
FIRST_WEEK_5PM = [(START_MONDAY_5PM + 24 * i * PERIOD_IN_HOUR) for i in range(5)]
FIRST_WEEK_IN_OFFICE = list(zip(FIRST_WEEK_9AM, FIRST_WEEK_5PM))
OFFICE_PERIOD = 8 * PERIOD_IN_HOUR
PERIOD_IN_DAY = 24 * PERIOD_IN_HOUR
PERIOD_IN_WEEK = PERIOD_IN_DAY * 7

ss = datetime.datetime.strptime("2020-9-30 14:00", "%Y-%m-%d %H:%M")
ee = datetime.datetime.strptime("2020-10-31 13:59", "%Y-%m-%d %H:%M")

DEBUG = int(os.getenv('DEBUG', 0))


class CP_SAT_Solver(IEEE_CISMixin):
  def __init__(self):
    self.model = cp_model.CpModel()

    # TODO: load all instance ofc
    temp_ins_name = 'phase1_instance_small_0.txt'
    temp_sol_name = 'phase1_instance_solution_small_0.txt'
    self.instances = self._load_instance_data()[temp_ins_name]
    self.sample_solution = self._load_instance_sample_solution_data()[temp_sol_name]
    self.price = self._load_AEMO_price_data()['RRP'][ss:ee]

    self.re_act = self.instances.re_act
    self.total_small = sum([i.n_small for i in self.instances.buildings.values()])
    self.total_large = sum([i.n_large for i in self.instances.buildings.values()])

    with open("../../cache/final_forecast.json", "r") as f:
      y_preds = json.load(f)

    y_preds = list(y_preds.values())
    buildings_sum = np.sum(y_preds[:6], axis=0)
    solars_sum = np.sum(y_preds[6:], axis=0)
    self.ddiff = buildings_sum - solars_sum
  def create_variables(self):
    # Start time for each activity
    self.act_start_day = {}
    for key, val in self.re_act.items():
      # Activity cannot start at time [(end-duration) -> end]
      self.act_start_day[key] = \
        self.model.NewIntVar(1, 31, f"act_start_day_{key}")

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

    # Cummulative energy at each time step
    self.cum_en = {}
    for t in range(0, END):
      self.cum_en[t] = self.model.NewIntVar(0, 1000000, f"cum_en_{t}")
    # Max Cummulative energy
    self.max_cum_em = self.model.NewIntVar(0, 1000000, f"max_cum_en_{t}")
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
          st += t//PERIOD_IN_DAY * self.act_start_bool[(key, t)]
        # Activity in duration
        for t in range(s, e):
          zt = sum([self.act_start_bool.get((key, tt), 0) for tt in range(t-val.duration+1, t+1)])
          self.model.Add(self.act_in_duration[(key, t)] == zt)
      # Activity must be scheduled and can only be schedule once
      self.model.AddExactlyOne(temp)
      # Activity start time
      self.model.Add(self.act_start_day[key] == st+1)
    
    # Precedences
    for key, val in self.re_act.items():
      for prec in val.prec:
        self.model.Add(self.act_start_day[key] > self.act_start_day[prec])

    for s, e in FIRST_WEEK_IN_OFFICE:
      for t in range(s, e):
        c_small = 0
        c_large = 0
        for key, val in self.re_act.items():
          if self.instances.re_act[key].size == "S":
            c_small += self.act_in_duration[(key, t)] * self.instances.re_act[key].n_room
          elif self.instances.re_act[key].size == "L":
            c_large += self.act_in_duration[(key, t)] * self.instances.re_act[key].n_room
          
        # At every timestep, total number of small room and large room must not exceed the total large and small room available.
        self.model.Add(c_small <= self.total_small)
        self.model.Add(c_large <= self.total_large)

    def map_to_first_week(t, start):
      if t > start:
        return (t - start + (0 % PERIOD_IN_WEEK) + PERIOD_IN_WEEK) % PERIOD_IN_WEEK + start
      else:
        return t

    # TODO: Add minimizing obj function
    obj = 0
    for t in range(0, END):
      cum = 0
      mt = map_to_first_week(t, START_MONDAY)
      # Sum all energy from buildings at time step t
      for key, val in self.re_act.items():
        if (key, mt) in self.act_in_duration:
          cum += val.load * val.n_room * self.act_in_duration[(key, mt)] 
      # Add base load (base building - solar)
      cum += math.ceil(self.ddiff[t])
      self.model.Add(self.cum_en[t] == cum)
      self.model.Add(self.max_cum_em >= self.cum_en[t])
      obj += self.price[t] * cum

    self.model.Minimize((0.25/1000)*obj + 0.0005*self.max_cum_em*2)


  def create_hint(self):
    re_act = self.sample_solution.re_act
    for key, val in re_act.items():
      self.model.AddHint(self.act_start_bool[(key, val.start_time)], 1)

  def fix_start(self):
    re_act = self.sample_solution.re_act
    for key, val in re_act.items():
      self.model.Add(self.act_start_bool[(key, val.start_time)] == 1)

  def solve(self):
    self.solver = cp_model.CpSolver()
    if DEBUG==2:
      self.solver.parameters.log_search_progress = True 
    self.solver.parameters.num_search_workers = 10 
    status = self.solver.Solve(self.model)

    ret = []
    curr_small = [None] * self.total_small
    curr_large = [None] * self.total_large
    curr_small_bmap = []
    curr_large_bmap = []
    debug_r = {}
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
              lb = " ".join(map(str, temp))
              ret.append(f"r {key} {t} {self.re_act[key].n_room} {lb}\n")
          if DEBUG:
            debug_r[t] = ((curr_small[::], curr_large[::]))

      print(self.solver.ObjectiveValue())
      with open("../cache/tt.txt", "w") as f:
        with open("../dataset/instance/phase1_instance_small_0.txt", "r") as tt:
          f.write(tt.readline())
          f.write(f"sched {len(self.re_act)} 0\n")
          for r in ret:
            f.write(r)

      dir_path = os.path.dirname(os.path.realpath(__file__))
      f_ins_path = os.path.join(dir_path, "../dataset/instance/phase1_instance_small_0.txt")
      f_sol_path = os.path.join(dir_path, "../cache/tt.txt")
      print(f"Java eval score: {schedule_eval_wrapper(f_ins_path, f_sol_path, 1)}")

      if DEBUG:
        for i in range(len(self.re_act)//10):
          print(i, " "*18, end ="")
        print()

        print("       ", end="")
        for key, val in self.re_act.items():
          print(key%10, end=" ")
        print()

        print("       ", end="")
        for key, val in self.re_act.items():
          print(val.size, end=" ")
        print(curr_small_bmap, curr_large_bmap)

        tg = '\033[32m'
        endg = '\033[m'
        for s, e in FIRST_WEEK_IN_OFFICE:
          for t in range(s, e):
            print("t=",t, end=" ")
            for key, val in self.re_act.items():
              vv = self.solver.Value(self.act_in_duration[(key, t)])
              if vv == 1:
                print(tg + str(vv) + endg, end=" ")
              else:
                print(vv, end=" ")
            print(debug_r[t])
          print()

    else:
      print("No solution found")

  def compare_to_java(self):
    pass
  


if __name__ == "__main__":
  a = CP_SAT_Solver()
  a.create_variables()
  #a.create_hint()
  a.fix_start()
  a.create_constraint()
  a.solve()
