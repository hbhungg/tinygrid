from dataset.schedule_data_model import Schedule_Model 

class Precedence_Graph(Schedule_Model):
  def add_p(self) -> None:
    self.acts = []
    self.once_off_acts = []
