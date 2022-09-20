from tinygrid.dataset import IEEE_CISMixin
from tinygrid import RandomForestForecaster, LassoForecaster
from tinygrid.dataset._schedule_loader import BatterySchedule
import random
import math

class Sim_Annealing:
  def __init__(self, phase, instance_file_name):
    # Phase check
    if phase != 1 and phase != 2:
      raise Exception('phase not either 1 or 2 as integer')

    # Read instance data
    instance_data = IEEE_CISMixin._load_instance_data()
    # Get the specified phase file
    self.specific_instance_data = instance_data[instance_file_name]

    # Read the sample solution schedual
    sample_solution_data = IEEE_CISMixin._load_instance_sample_solution_data()
    frag_file_name = instance_file_name.split('_')
    self.sample_solution_schedual = sample_solution_data[frag_file_name[0]+'_'+frag_file_name[1]+'_solution_'+frag_file_name[2]+'_'+frag_file_name[3]]

    # Read the AEMO price data
    # Price data in 30min intervals (jth row in price data = math.ceiling(ith/2) in inverval form)
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
      self.battery_charge[battery] = 1

  def get_load(self, schedual, t) -> float:
    l_t = 1
    
    s_1 = 0
    for b in range(len()):
      s_1 += 1

    s_2 = 0
    for i in range(len()):
      s_2 += 1
    
    s_3 = 0
    for i in range(len()):
      s_3 += 1

    return l_t + s_1 + s_2 + s_3

  def objective_function(self, schedual) -> float:
    s_1 = 0
    for t in range(len()):
      l_t = self.get_load(schedual, t)
      e_t = 1
      s_1 += l_t*e_t

    max_l_t = 0
    for t in range(len()):
      l_t = self.get_load(schedual, t)
      if max_l_t < l_t:
        max_l_t = l_t
    
    s_2 = 0
    for t in range(len()):
      s_2 += max_l_t
    
    s_3 = 0
    for i in range(len()):
      d_i = 1
      value_i = 1
      o_i = 1
      penalty_i = 1
      s_3 += d_i*(value_i - o_i*penalty_i)

    return (0.25/1000)*s_1 + 0.005*(s_2)**2 - s_3

  def get_candidate(self, schedual_candidate):

    # Get a random time based on time_line_len
    t = math.floor(random.random() * len(self.time_line_len))

    # Randomly pick a battery
    battery_id = math.floor(random.random() * len(self.specific_instance_data.batteries))

    # Check if battery_id exists in schedual_candidate.batteries
    if battery_id in schedual_candidate.batteries:
      # Check if schedual_candidate.batteries[battery_id].time != t
      if schedual_candidate.batteries[battery_id].time != t:
        # Add BatterySchedule class to dict, id=battery_id and time=t with decision=1 
        schedual_candidate.batteries[battery_id].append(BatterySchedule(time=t, decision=1))

      # Get decision at time t for battery battery_id
      d = schedual_candidate.batteries[battery_id].decision
      choices = [0,1,2] - [d]
      choice = choices[math.floor(random.random() * len(choices))]
        
      # Copy schedual_candidate
      new_schedual_candidate = schedual_candidate.copy()
      # Set choice as battery battery_id's decision
      new_schedual_candidate.batteries[battery_id].decision = choice

      return new_schedual_candidate
    else:
      # Current decision for battery battery_id is 1=hold as it does not exist in list
      # Add BatterySchedule class to dict, id=battery_id and time=t with decision=1 
      schedual_candidate.batteries[battery_id] = [BatterySchedule(time=t, decision=1)]

      # Get decision at time t for battery battery_id
      d = schedual_candidate.batteries[battery_id].decision
      choices = [0,1,2] - [d]
      choice = choices[math.floor(random.random() * len(choices))]

      # Copy schedual_candidate
      new_schedual_candidate = schedual_candidate.copy()
      # Set choice as battery battery_id's decision
      new_schedual_candidate.batteries[battery_id].decision = choice

      return new_schedual_candidate

  def get_init_candidate(self):
    return self.sample_solution_schedual

  def run(self, t_0, curvature, max_iterations) -> tuple:
    # Check if max_iterations is not zero
    if max_iterations <= 0:
      raise Exception('max_iterations must be between 1 and inf')

    # Set the number of iterations
    iteration = 1

    # Get the initial candidate
    b = self.get_init_candidate()
    # Send it to the objective function
    b_eval = self.objective_function(c)
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
      acceptance_cri = math.exp(-(c_new_eval - c_eval)/t)
      # Check to take c_new by chance
      if c_new_eval - c_eval < 0 or random.random() < acceptance_cri:
        c, c_eval = c_new, c_new_eval
      # Increment
      iteration += 1
    
    # Return the best
    return (b, b_eval)


sim_an = Sim_Annealing(phase = 1, instance_file_name = 'phase1_instance_large_0.txt')
#sol = sim_an.run(t_0 = 0.1,curavature = 1,max_iterations = 100)
#print(sim_an.objective_function(sim_an.sample_solution_schedual) - sol[1])


# Battery

# Place sample solution into timeline *RECONSIDER TIMELINE DATASTRUCTURE*
# Read and store AEMO price data into interval format
# Create the objective function
# Create candidates based on randomly taking a time-interval, then randomly choosing to (Hold, Discharge, Charge) (remove battery's current state) a randomly selected battery from all batteries.
# Initial state will be that where all batteries are on hold