import os
import datetime
from dataset.ieee_cis.tsf_loader import convert_tsf_to_dataframe

class DataManager:
  def __init__(self, 
               # Default phase1 and phase2 time in the documents
               phase1_time = datetime.datetime(day=1, month=10, year=2020, hour=0, minute=0, second=0),
               phase2_time = datetime.datetime(day=1, month=11, year=2020, hour=0, minute=0, second=0)):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    energy_data_path = os.path.join(BASE_DIR, "energy/nov_data.tsf")
    tsf = convert_tsf_to_dataframe(energy_data_path)

    self.df = tsf[0]

    series_name = self.df["series_name"]
    series_value = self.df["series_value"]
    start_timestamp = self.df["start_timestamp"]


    self.train = dict()
    self.phase1 = dict()
    self.phase2 = dict()

    for name, value, stime in zip(series_name, series_value, start_timestamp):
      phase_1_idx = int((phase1_time - stime).total_seconds()/60/15)
      phase_2_idx = int((phase2_time - stime).total_seconds()/60/15)

      self.train[name] = value[:phase_1_idx]
      self.phase1[name] = value[phase_1_idx:phase_2_idx]
      self.phase2[name] = value[phase_2_idx:]


if __name__ == "__main__":
  d = DataManager()
  for k,v in d.train.items():
    print(len(v))
