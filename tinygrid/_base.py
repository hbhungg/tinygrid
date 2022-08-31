from abc import ABC, abstractmethod
from .dataset import IEEE_CISMixin


class _BaseForecaster(ABC, IEEE_CISMixin):
  CACHE_FOLDER = "./cache/"
  CHECKPOINTS  = "./checkpoints/"

  def __init__(self):
    """
    Base data preparation
    Load data from IEEE_CISMixin, upsample weather to 15 mins to match the energy data
    Overide this if inheritted class have different data preparation method
    """
    self.energy = self._load_energy_data()
    self.weather = self._load_ERA5_weather_data()
    # Drop unused cols, upsample to 15 minutes
    self.weather = self.weather.drop(
               ['coordinates (lat,lon)', 
                'model (name)',
                'utc_offset (hrs)', 
                'model elevation (surface)',
                "mean_sea_level_pressure (Pa)",
                "wind_speed (m/s)",
                "relative_humidity ((0-1))"], 
               axis=1).resample('15min').asfreq()

    self.names = [i for i in self.energy]

  @abstractmethod
  def fit(self):
    pass

  @abstractmethod
  def predict(self):
    pass

  @abstractmethod
  def _prepare_data(self):
    pass
