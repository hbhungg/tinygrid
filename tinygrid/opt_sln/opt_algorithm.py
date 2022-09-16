from tinygrid.dataset import IEEE_CISMixin
from tinygrid import RandomForestForecaster, LassoForecaster

class Sim_Annealing:
  def __init__(self, phase, schedule_path):
    # Read schedule data
    data = IEEE_CISMixin._load_schedule_data()
    # Get the specified phase file
    self.s_schedual = data[schedule_path]

    # Run and save forecasting
    a = RandomForestForecaster()
    a.fit()
    a.predict()
    self.solar_prediction = a.y_preds

  def objective_function(self, params) -> float:
    return
