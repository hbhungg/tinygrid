from tinygrid.dataset import IEEE_CISMixin
from tinygrid import RandomForestForecaster, LassoForecaster
from tinygrid.dataset._schedule_loader import BatterySchedule, Schedule
import random
import math
import pandas as pd
import numpy as np
from scipy.special import logsumexp

class Sim_Annealing:
  def __init__(self, phase, instance_file_name):
    # Phase check
    if phase != 1 and phase != 2:
      raise Exception('phase not either 1 or 2 as integer')

    # Read instance data
    instance_data = IEEE_CISMixin._load_instance_data()
    # Get the specified phase file
    self.specific_instance_data = instance_data[instance_file_name]

    # Read the sample solution schedule
    sample_solution_data = IEEE_CISMixin._load_instance_sample_solution_data()
    frag_file_name = instance_file_name.split('_')
    self.sample_solution_schedule = sample_solution_data[frag_file_name[0]+'_'+frag_file_name[1]+'_solution_'+frag_file_name[2]+'_'+frag_file_name[3]]

    # Read the AEMO price data
    # Price data in 30min intervals (jth row in price data = math.floor(ith/2) in inverval form)
    if phase == 1:
      self.price_data = IEEE_CISMixin._load_AEMO_oct_price_data()
    elif phase == 2:
      self.price_data = IEEE_CISMixin._load_AEMO_nov_price_data()

    # Run and save forecasting
    a = RandomForestForecaster()
    a.fit()
    a.predict()

    # Take predictions as deterministic values
    # 7 Buildings with their energy demand
    self.building_demand = {}
    for i in range(7):
      # Building 2 does not exist
      if i == 2:
        continue
      # Select the specified phase data
      if phase == 1:
        self.building_demand['Building' + str(i)] = a.y_preds['Building' + str(i)][:2977]
      elif phase == 2:
        self.building_demand['Building' + str(i)] = a.y_preds['Building' + str(i)][2976:]

    # 6 Solar pannels with their energy production
    self.solar_prod = {}
    for i in range(6):
      # Select the specified phase data
      if phase == 1:
        self.solar_prod['Solar' + str(i)] = a.y_preds['Solar' + str(i)][:2977]
      elif phase == 2:
        self.solar_prod['Solar' + str(i)] = a.y_preds['Solar' + str(i)][2976:]

    # Set seed for random generation
    random.seed(1111)

    # Timeline length
    if phase == 1:
      self.time_line_len = 2976
    elif phase == 2:
      self.time_line_len = 2976 - len(a.y_preds['Solar0'])

    # Set battery charge
    self.battery_charge = {}
    for battery in self.specific_instance_data.batteries:
      self.battery_charge[battery] = self.specific_instance_data.batteries[battery].capacity

    # Initial score
    self.init_score = 0

  def get_load(self, schedule: Schedule, t: int) -> float:
    # Get the load prior to scheduling at time t
    buildings_demand_t = 0
    for building_id in self.building_demand:
      buildings_demand_t += self.building_demand[building_id][t]
    solars_production_t = 0
    for solar_id in self.solar_prod:
      solars_production_t += self.solar_prod[solar_id][t]
    # Calculate load sum
    l_t = buildings_demand_t - solars_production_t
    
    # Battery sum
    s_1 = 0
    for battery in self.specific_instance_data.batteries:
      if battery in schedule.batteries:
        res = self.check_existence_bat(schedule.batteries[battery], t)
        if res[0]:
          d = schedule.batteries[battery][res[1]].decision
          if d == 0: # Charge decision
            charge_amount = self.specific_instance_data.batteries[battery].max_power/((self.specific_instance_data.batteries[battery].efficiency)**(1/2))
            # Check if charge_amount is ok
            if self.battery_charge[battery] + 0.25*charge_amount <= self.specific_instance_data.batteries[battery].capacity:
              s_1 += charge_amount
              # Update charge
              self.battery_charge[battery] += 0.25*charge_amount
          elif d == 2: # Discharge decision
            # Check if the battery is not empty
            if self.battery_charge[battery] >= 0:
              discharge_amount = self.specific_instance_data.batteries[battery].max_power*((self.specific_instance_data.batteries[battery].efficiency)**(1/2))
              # Check if discharge_amount is ok
              if self.battery_charge[battery] - 0.25*discharge_amount >= 0:
                s_1 -= discharge_amount
                # Update charge
                self.battery_charge[battery] -= 0.25*discharge_amount

    # Once-off sum
    s_2 = 0
    for act in self.specific_instance_data.once_act:
      # Check if activity is not in schedule, stop program if so.
      if act not in schedule.once_act: continue
      # Check if recurring activity act is in t
      if t >= schedule.once_act[act].start_time and t <= schedule.once_act[act].start_time + self.specific_instance_data.once_act[act].duration:
        # 15mins of activity load
        act_total_load = (1/(4*self.specific_instance_data.once_act[act].duration))*self.specific_instance_data.once_act[act].load*self.specific_instance_data.once_act[act].n_room
        s_2 += act_total_load
    
    # Recurring sum
    s_3 = 0
    for act in self.specific_instance_data.re_act:
      # Check if activity is not in schedule, stop program if so.
      if act not in schedule.re_act: raise Exception('Provided schedule file invalid: a re_act is not in solution')
      # Check if recurring activity act is in t
      if t >= schedule.re_act[act].start_time and t <= schedule.re_act[act].start_time + self.specific_instance_data.re_act[act].duration:
        # 15mins of activity load
        act_total_load = (1/(4*self.specific_instance_data.re_act[act].duration))*self.specific_instance_data.re_act[act].load*self.specific_instance_data.re_act[act].n_room
        s_3 += act_total_load

    return l_t + s_1 + s_2 + s_3

  def objective_function(self, schedule: Schedule) -> float:
    # First sum of objective function
    s_1 = 0
    max_l_t = 0
    for t in range(self.time_line_len):
      l_t = self.get_load(schedule, t)
      # Attempt to update max load value
      if max_l_t < l_t:
        max_l_t = l_t
      e_t = self.price_data['RRP'].iloc[math.floor(t/2)]
      s_1 += l_t*e_t

    # Middle sum of objective function
    s_2 = self.time_line_len * max_l_t
    
    # Last sum of objective function
    s_3 = 0
    for act in schedule.once_act:
      value_i = self.specific_instance_data.once_act[act].value
      o_i = self.is_during_office_hours(schedule.once_act[act].start_time, self.specific_instance_data.once_act[act].duration)
      penalty_i = self.specific_instance_data.once_act[act].penalty
      s_3 += value_i - o_i*penalty_i

    return (0.25/1000)*s_1 + 0.005*(s_2)**2 - s_3

  """
  """
  def check_existence_bat(self, bats: list[BatterySchedule], t: int) -> list:
    for i in range(len(bats)):
      if bats[i].time == t: return [True, i]
    return [False, None]

  """
  Not finished
  1 for true
  0 for false
  """
  def is_during_office_hours(start: int, duration: int) -> int:
    return 1

  def get_candidate(self, schedule_candidate: Schedule) -> Schedule:

    # Get a random time based on time_line_len
    t = math.floor(random.random() * self.time_line_len)

    # Randomly pick a battery
    battery_id = random.choice(list(self.specific_instance_data.batteries.keys()))

    # Check if battery_id exists in schedule_candidate.batteries
    if battery_id in schedule_candidate.batteries:
      # Check if there exists a battery with time != t
      res = self.check_existence_bat(schedule_candidate.batteries[battery_id], t)
      if not res[0]:
        # Add BatterySchedule class to dict, id=battery_id and time=t with decision=1 
        schedule_candidate.batteries[battery_id].append(BatterySchedule(time=t, decision=1))
        res[1] = -1

      # Get decision at time t for battery battery_id
      d = schedule_candidate.batteries[battery_id][res[1]].decision
      choices = [0,1,2]
      choices.remove(d)
      choice = choices[math.floor(random.random() * len(choices))]
      # Set choice as battery battery_id's decision
      schedule_candidate.batteries[battery_id][res[1]].decision = choice

      return schedule_candidate
    else:
      # Current decision for battery battery_id is 1=hold as it does not exist in list
      # Add BatterySchedule class to dict, id=battery_id and time=t with decision=1 
      schedule_candidate.batteries[battery_id] = [BatterySchedule(time=t, decision=1)]

      # Get decision at time t for battery battery_id
      choices = [0, 2]
      choice = choices[math.floor(random.random() * len(choices))]
      # Set choice as battery battery_id's decision
      schedule_candidate.batteries[battery_id][0].decision = choice

      return schedule_candidate

  def get_init_candidate(self):
    return self.sample_solution_schedule

  def run(self, t_0: float, curvature: float, max_iterations: int) -> tuple:
    # Check if max_iterations is not zero
    if max_iterations <= 0:
      raise Exception('max_iterations must be between 1 and inf')

    # Set the number of iterations
    iteration = 1

    # Get the initial candidate
    b = self.get_init_candidate()
    # Send it to the objective function
    b_eval = self.objective_function(b)
    self.init_score = b_eval
    c, c_eval = b, b_eval

    # Run the annealing
    while iteration <= max_iterations:
      # Set the new candidate
      c_new = self.get_candidate(c)
      # Send it to the objective function
      c_new_eval = self.objective_function(c_new)
      # Check if the new candidate is best
      if c_new_eval < b_eval:
        b, b_eval = c_new, c_new_eval
      # Set the temperature
      t = t_0 * (1-(iteration/(max_iterations)))**curvature
      # Set the acceptance criterion
      acceptance_cri = 0
      if t > 0.01 or abs(c_eval-c_new_eval) >= 10000:
        acceptance_cri = math.exp(-(c_eval-c_new_eval)/t)
      # Check to take c_new by chance
      if c_new_eval < c_eval or random.random() < acceptance_cri:
        c, c_eval = c_new, c_new_eval
      # Increment
      iteration += 1
      # Console update
      if iteration % 25 == 0:
        print('iteration: ' + str(iteration) + ', improvement: ' + str(b_eval - self.init_score) + ', temp: ' + str(t))
    
    # Return the best
    return (b, b_eval)


sim_an = Sim_Annealing(phase = 1, instance_file_name = 'phase1_instance_large_0.txt')
sol = sim_an.run(t_0 = 10, curvature = 2, max_iterations = 10000)
print('Improvement :' + str(sol[1] - sim_an.init_score))