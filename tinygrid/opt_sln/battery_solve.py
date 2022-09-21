import json
import numpy as np
import math
from ortools.sat.python import cp_model

from tinygrid import RandomForestForecaster
from tinygrid.dataset import IEEE_CISMixin
from tinygrid.schedule_eval import schedule_eval_wrapper


# Phase 1 stuffs
PERIOD_IN_HOUR = 4
START_MONDAY = 384
START_MONDAY_9AM = 384 + 9 * PERIOD_IN_HOUR 
START_MONDAY_5PM = 384 + 17 * PERIOD_IN_HOUR
FIRST_WEEK_9AM = [START_MONDAY_9AM + 24 * i * PERIOD_IN_HOUR for i in range(5)]
FIRST_WEEK_5PM = [START_MONDAY_5PM + 24 * i * PERIOD_IN_HOUR for i in range(5)]
FIRST_WEEK_IN_OFFICE = list(zip(FIRST_WEEK_9AM, FIRST_WEEK_5PM))
END = 2976


def solve_battery(ins, sol, y_preds, price_data, from_java): 
  model = cp_model.CpModel()
  bat_idxs = list(ins.batteries)

  bat_charge = {}
  bat_discharge = {}
  bat_hold = {}
  bat_cap = {}

  for bidx in bat_idxs:
    for t in range(START_MONDAY, END+1):
      # Variables for battery decision at each time step
      bat_charge[(bidx, t)] = \
        model.NewBoolVar(f"c{bidx} at {t}")
      bat_discharge[(bidx, t)] = \
        model.NewBoolVar(f"d{bidx} at {t}")
      bat_hold[(bidx, t)] = \
        model.NewBoolVar(f"h{bidx} at {t}")
      # Variables for battery capacity at each time step
      bat_cap[(bidx, t)] = \
        model.NewIntVar(0, ins.batteries[bidx].capacity, f"cap{bidx} at {t}")

  for bidx in bat_idxs:
    for t in range(START_MONDAY, END+1):
      ii = (bidx, t)
      # Each battery can only hold, charge or discharge at a time.
      model.AddExactlyOne([bat_hold[ii], bat_discharge[ii], bat_charge[ii]])

  # FIXME: Something is wrong with this
  # Capacity seem to not be following the action.
  # Leading to overcharge or overdischarge
  for bidx in bat_idxs:
    for t in range(START_MONDAY, END+1):
      ii = (bidx, t)
      if t == START_MONDAY:
        # Battery start at 100%
        model.Add(4*bat_cap[ii] == 4*ins.batteries[bidx].capacity + ins.batteries[bidx].max_power*(bat_charge[ii] - bat_discharge[ii]))
      else:
        # current battery capacity depends on previous capacity values
        model.Add(4*bat_cap[ii] == 4*bat_cap[(bidx, t-1)] + ins.batteries[bidx].max_power*(bat_charge[ii] - bat_discharge[ii]))
        print(4*bat_cap[ii] == 4*bat_cap[(bidx, t-1)] + ins.batteries[bidx].max_power*(bat_charge[ii] - bat_discharge[ii]))

  # Abolghasemi, M., Esmaeilbeigi, R., 2021
  # State-of-the-art predictive and prescriptive analytics for IEEE CIS 3rd Technical Challenge
  # at https://arxiv.org/pdf/2112.03595.pdf
  # TODO: Something is wrong here, val is too big
  obj = 0.0
  for t in range(START_MONDAY, END+1):
    # Price and base load at time t
    pp = price.iloc[t//2-1].item()
    bb = y_preds[t]
    # TODO: yea...
    cum = 0.0
    for bidx in bat_idxs:
      # For each batteries
      mxp = ins.batteries[bidx].max_power
      eff = ins.batteries[bidx].efficiency
      cc = bat_charge[(bidx, t)]
      dd = bat_discharge[(bidx, t)]
      cum += (mxp / math.sqrt(eff)) * (cc - eff * dd)
    obj += (0.25/1000) * pp*(bb + cum)

  model.Minimize(obj)

  solver = cp_model.CpSolver()
  status = solver.Solve(model)

  if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"Total hold: {sum([solver.Value(v) for v in bat_hold.values()]) :>9}")
    print(f"Total discharge: {sum([solver.Value(v) for v in bat_discharge.values()])}")
    print(f"Total charge: {sum([solver.Value(v) for v in bat_charge.values()]):>4}")
    # Why is f string allign so dumb?
    print(f"Solution eval:   {solver.ObjectiveValue()}")
    print(f"From java eval:  {from_java}")

    bat_plan = []
    for (idxc, c), (idxd, d), (idxh, h), (key, v) in zip(bat_charge.items(), bat_discharge.items(), bat_hold.items(), bat_cap.items()):
      c, d, h = solver.Value(c), solver.Value(h), solver.Value(h)
      # Parse the output according to the format
      # c # battery_id # time # decision (0, 1, 2)
      # Can skip decision 1 since no entry means hold.
      if c == 1:
        # Charge
        bat_plan.append(f"c {idxc[0]} {idxc[1]} 0\n")
        #print(f"{key}, {solver.Value(v)} charge")
      if d == 1:
        # Discharge (seem to be hold)?
        bat_plan.append(f"c {idxc[0]} {idxc[1]} 2\n")
        #print(f"{key}, {solver.Value(v)} discharge")
        #print(f"{key}, {solver.Value(v)} hold")
      # Hold (seem to be discharge)
      #print(f"{key}, {solver.Value(v)} hold")
      #bat_plan.append(f"c {idxc[0]} {idxc[1]} 2\n")
  else:
    print('No solution found.')

  return bat_plan


if __name__ == "__main__":
  CACHE = True

  # Forecasted demand and solar production
  rnn = RandomForestForecaster()
  if CACHE:
    with open("../../cache/final_forecast.json", "r") as f:
      rnn.y_preds = json.load(f)
  else:
    rnn.fit()
    rnn.predict()
  y_preds = rnn.y_preds
  y_preds = list(y_preds.values())

  buildings_sum = np.sum(y_preds[:6], axis=0)
  solars_sum = np.sum(y_preds[6:], axis=0)
  ddiff = buildings_sum - solars_sum

  # Load instance file
  ins_data = IEEE_CISMixin._load_instance_data()
  ins0 = ins_data['phase1_instance_small_0.txt']

  # Load sample solution file
  sol = IEEE_CISMixin._load_instance_sample_solution_data()
  sol0 = sol['phase1_instance_solution_small_0.txt']

  price = IEEE_CISMixin._load_AEMO_oct_price_data()['RRP']
  bat_plan = solve_battery(ins0, sol0, ddiff, price, 112112)

  #with open("tt.txt", "w") as temp:
  #  with open("../dataset/instance_sample_solution/phase1_instance_solution_small_0.txt", "r") as f:
  #    # copy
  #    for l in f:
  #      temp.write(l)
  #  for b in bat_plan:
  #    temp.write(b)
  #
  #import os 
  #dir_path = os.path.dirname(os.path.realpath(__file__))
  #f_ins_path = os.path.join(dir_path, "../dataset/instance/phase1_instance_small_0.txt")
  #f_sol_path = os.path.join(dir_path, "tt.txt")
  #print(schedule_eval_wrapper(f_ins_path, f_sol_path, 1))
