import unittest
from tinygrid.dataset import IEEE_CISMixin

class load_ERA5_weather_data_tests(unittest.TestCase):
  def setUp(self):
    self.cl = IEEE_CISMixin
  def tearDown(self):
    pass

  def test_call(self):
    try:
      self.cl._load_ERA5_weather_data()
    except:
      self.fail("Instance failed at _load_ERA5_weather_data")


class load_AEMO_price_datatests(unittest.TestCase):
  def setUp(self):
    self.cl = IEEE_CISMixin
  def tearDown(self):
    pass
  def test_call(self):
    try:
      self.cl._load_AEMO_price_data()
    except:
      self.fail("Instance failed at _load_AEMO_price_data")

class load_energy_data_tests(unittest.TestCase):
  def setUp(self):
    self.cl = IEEE_CISMixin
  def tearDown(self):
    pass  
  def test_call(self):
    try:
      self.cl._load_energy_data()
    except:
      self.fail("Instance failed at _load_energy_data")


if __name__ == '__main__':
    unittest.main()