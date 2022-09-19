from tinygrid.dataset import IEEE_CISMixin
from tinygrid import RandomForestForecaster, LassoForecaster
import random
import math

class Sim_Annealing:
  def __init__(self, phase, instance_file_name):
    # Phase check
    if phase != 1 and phase != 2:
      raise Exception('phase not either 1 or 2 as integer')

    # Read instance data
    data = IEEE_CISMixin._load_instance_data()
    # Get the specified phase file
    self.s_schedual = data[instance_file_name]

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

    # Timeline of events (each entry is 15min interval)
    # Ignoring assignment of batteries to buildings, batteries can be accessed everywhere
    # time_line[t] = [(rec_act_0, info...) ,(once_act_0, info...), (bat_2, toggle, info...)]
    # time_line[t-1] = None -> nothing assigned to that time
    if phase == 1:
      self.time_line = [None for i in range(2977)]
    elif phase == 2:
      self.time_line = [None for i in range(2976 - len(a.y_preds['Solar0']))]

  def objective_function(self, params) -> float:
    
    s_1 = 0
    for i in range(len()):
      var = 0
      s_1 += var

    s_2 = 0
    for i in range(len()):
      var = 0
      s_2 += var

    s_3 = 0
    for i in range(len()):
      var = 0
      s_3 += var

    return (0.25/1000)*s_1 + 0.005*s_2 - s_3

  def get_candidates(self, params):
    return []

  def get_init_candidate(self):
    return ''

  def assign_bats(self):
    # Batteries assigned after the assignment of activities
    pass

  def run(self, t_0, curvature, max_iterations):
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
      # Get the candidate solutions
      candidates = self.get_candidates(c)
      # Get a random index in the candidates array
      candidate_index = math.floor(random.random() * len(candidates))
      # Set the new candidate
      c_new = candidates[candidate_index]
      # Send it to the objective function
      c_new_eval = self.objective_function(c_new)
      
      # Check if the new candidate is best
      if c_new_eval < b_eval:
        b, b_eval = c_new, c_new_eval
      
      # Set the temperature
      t = t_0 * (1-(iteration/(max_iterations)))**curvature

      # Set the acceptance criterion
      acceptance_cri = math.exp(-(c_new_eval - c_eval)/t)
      
      # Check to check c_new by chance
      if c_new_eval - c_eval < 0 or random.random() < acceptance_cri:
        c, c_eval = c_new, c_new_eval

      # Increment
      iteration += 1
    
    # Return the best
    return (b, b_eval)




a = Sim_Annealing(phase = 1, instance_file_name = 'phase1_instance_large_0.txt')

print(a.solar_prod)
print(a.building_demand)


# Battery schedual is based on a seperate metric: charge during off-peaks, discharge during activites.

# Only for activities
# 1. Objective function f(X), Temperature T = T_0 * a^k (T_0 is the inital temperature, cooling rate (0.8 to 0.99)) or T = T_0 * (1-(k/k_max))^b (k)max is the max num of iterations, b is the curavature (between 1 and 4))
# 2. Initial state will be a simple assignment of activities and batteries (Let this be X)
# 3. If k != k_max:
  # 4. Perform annealing process
    # 5. In the neighbourhood (selecting similar scheduals) of the schedual assignment, randomly choose a new schedual X_new from this set
      # 6. If f(X_new) - f(X) >= 0: X <- X_new
      # 7. Elif random number < exp[-(f(X_new)-f(X))/T]: X <- X_new
      # 8. GOTO line 5, k++

# The set N = Neighbourhood will be definded as follows:
# N: (for each activity act: change act to a random legal time slot.)
