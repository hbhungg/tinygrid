import unittest
from tinygrid.forecaster import Forecaster, generate_solar_data, generate_building_data

class TestForecaster(unittest.TestCase):
  def test_generate_building_data(self):
    with self.assertRaises(TypeError):
      _, _ = generate_building_data()

  def test_generate_solar_data(self):
    with self.assertRaises(TypeError):
      _, _ = generate_solar_data()


if __name__ == "__main__":
  unittest.main()
